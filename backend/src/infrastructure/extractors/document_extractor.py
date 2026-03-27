import base64
import io
import os
from pathlib import Path

from langchain_core.messages import HumanMessage
from PIL import Image


def _logger():
    from src.core.logger import get_logger

    return get_logger(__name__)


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = PDF_EXTENSIONS | IMAGE_EXTENSIONS

ORIENTATION_CHECK_PROMPT = (
    "Look at the main text in this document image. "
    "In which direction does the text run? "
    "Is it horizontal and readable (normal), "
    "or is it rotated sideways or upside down?"
)

ORIENTATION_SCHEMA = {
    "title": "orientation_check",
    "type": "object",
    "properties": {
        "text_direction": {
            "type": "string",
            "enum": ["normal", "rotated_left", "rotated_right", "upside_down"],
            "description": (
                "How the text in the document currently appears: "
                "'normal' = reads left-to-right horizontally, "
                "'rotated_left' = text runs upward (top of text is on the left side of image), "
                "'rotated_right' = text runs downward (top of text is on the right side of image), "
                "'upside_down' = text is flipped 180 degrees."
            ),
        },
    },
    "required": ["text_direction"],
}

# Map detected text direction to clockwise rotation needed to correct it
DIRECTION_TO_ROTATION = {
    "normal": 0,
    "rotated_left": 270,  # top of text points left → rotate 270° CW (= 90° CCW)
    "rotated_right": 90,  # top of text points right → rotate 90° CW
    "upside_down": 180,
}


PROVIDERS = {
    "anthropic": {
        "prefixes": ("claude-",),
        "env_key": "ANTHROPIC_API_KEY",
        "native_pdf": True,
        "llm_factory": lambda model, api_key, max_tokens: _import_anthropic()(
            model=model, api_key=api_key, max_tokens=max_tokens, temperature=0
        ),
    },
    "openai": {
        "prefixes": ("gpt-", "o1", "o3", "o4"),
        "env_key": "OPENAI_KEY",
        "native_pdf": False,
        "llm_factory": lambda model, api_key, max_tokens: _import_openai()(
            model=model, api_key=api_key, max_tokens=max_tokens, temperature=0
        ),
    },
    "google": {
        "prefixes": ("gemini-",),
        "env_key": "GOOGLE_API_KEY",
        "native_pdf": False,
        "llm_factory": lambda model, api_key, max_tokens: _import_google()(
            model=model, api_key=api_key, max_tokens=max_tokens, temperature=0
        ),
    },
}


def _import_anthropic():
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic


def _import_openai():
    from langchain_openai import ChatOpenAI

    return ChatOpenAI


def _import_google():
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI


def _resolve_provider(model: str) -> dict:
    for provider in PROVIDERS.values():
        if model.startswith(provider["prefixes"]):
            return provider
    return PROVIDERS["anthropic"]


def _create_llm(model: str, api_key: str, max_tokens: int):
    provider = _resolve_provider(model)
    return provider["llm_factory"](model, api_key, max_tokens)


class DocumentExtractor:
    def __init__(
        self,
        prompt: str,
        model: str = "claude-haiku-4-5-20251001",
        output_schema: dict | None = None,
        api_key: str | None = None,
        max_tokens: int = 1024,
    ):
        self.provider = _resolve_provider(model)
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get(self.provider["env_key"], "")
        self.model_name = model
        self.max_tokens = max_tokens
        self.prompt = prompt
        self.output_schema = output_schema
        self.llm = _create_llm(model, self.api_key, max_tokens)
        if isinstance(output_schema, dict) and "title" not in output_schema:
            output_schema = {"title": "extraction_output", **output_schema}
        self.structured_llm = self.llm.with_structured_output(output_schema)

    def _image_content(self, *, b64: str | None = None, url: str | None = None) -> dict:
        """Build the image content block in the correct format for the current provider."""
        if url and url.startswith("https://"):
            if self.provider["native_pdf"]:
                return {
                    "type": "image",
                    "source": {"type": "url", "url": url},
                }
            return {"type": "image_url", "image_url": {"url": url}}

        if b64 is None:
            raise ValueError("Se requiere b64 o url")

        if self.provider["native_pdf"]:
            # Anthropic format
            return {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
            }
        # OpenAI / others format
        return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}

    def _image_to_base64(self, image: Image.Image, max_dimension: int = 4096) -> str:
        if image.width > max_dimension or image.height > max_dimension:
            ratio = min(max_dimension / image.width, max_dimension / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=95)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _check_orientation(self, image_b64: str) -> int:
        """Ask the model to detect text orientation. Returns CW degrees to correct."""
        try:
            orientation_llm = _create_llm(self.model_name, self.api_key, 256)
            structured = orientation_llm.with_structured_output(ORIENTATION_SCHEMA)
            content = [
                self._image_content(b64=image_b64),
                {"type": "text", "text": ORIENTATION_CHECK_PROMPT},
            ]
            message = HumanMessage(content=content)
            result = structured.invoke([message])
            if hasattr(result, "model_dump"):
                result = result.model_dump()
            direction = result.get("text_direction", "normal")
            rotation = DIRECTION_TO_ROTATION.get(direction, 0)
            _logger().info("Orientation check: %s → rotation %d°", direction, rotation)
            return rotation
        except Exception as e:
            _logger().warning("Orientation check failed, assuming normal: %s", e)
            return 0

    def _load_image_file(self, image_path: Path) -> list[str]:
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # First pass: encode for orientation check
        image_b64 = self._image_to_base64(image)
        rotation = self._check_orientation(image_b64)

        if rotation != 0:
            _logger().info("Rotating image %d° clockwise", rotation)
            # PIL rotate is counterclockwise, so negate
            image = image.rotate(-rotation, expand=True)
            image_b64 = self._image_to_base64(image)

        return [image_b64]

    def _pdf_to_image(self, pdf_path: Path) -> Image.Image | None:
        """Convert first page of PDF to PIL Image."""
        try:
            import PIL

            # Allow large images from high-res scans
            PIL.Image.MAX_IMAGE_PIXELS = 200_000_000

            from pdf2image import convert_from_path

            images = convert_from_path(str(pdf_path), first_page=1, last_page=1, dpi=200)
            if not images:
                return None
            img = images[0]
            _logger().info("PDF to image: %dx%d pixels", img.width, img.height)
            return img
        except Exception as e:
            _logger().warning("PDF to image conversion failed: %s", e)
            return None

    def _pdf_page_count(self, pdf_path: Path) -> int:
        """Return the number of pages in a PDF."""
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        except Exception:
            return 0

    def _ocr_pdf(self, pdf_path: Path) -> str | None:
        """Run OCR on the first page of a PDF via pytesseract."""
        try:
            import pytesseract

            img = self._pdf_to_image(pdf_path)
            if img is None:
                return None
            text = pytesseract.image_to_string(img)
            if text and text.strip():
                _logger().info("OCR extracted %d chars from PDF", len(text))
                return text.strip()
            return None
        except Exception as e:
            _logger().warning("OCR failed: %s", e)
            return None

    def _extract_with_pdf(self, pdf_path: Path) -> dict:
        pdf_size = pdf_path.stat().st_size
        page_count = self._pdf_page_count(pdf_path)
        _logger().info(
            "=== PDF extraction === size=%.1fKB pages=%d model=%s",
            pdf_size / 1024,
            page_count,
            self.model_name,
        )

        # Heavy single-page PDFs (>1MB): try OCR first (much cheaper)
        if page_count == 1 and pdf_size > 1_000_000:
            ocr_text = self._ocr_pdf(pdf_path)
            if ocr_text:
                return self._extract_with_text(ocr_text)
            _logger().info("OCR produced no text, falling back to PDF/image")

        # Light PDFs, multi-page, or OCR failed:

        # Providers with native PDF support send the file directly
        if self.provider["native_pdf"]:
            return self._extract_raw_pdf(pdf_path)

        # Non-native: convert to image, check orientation, then use vision
        img = self._pdf_to_image(pdf_path)
        if img is None:
            raise ValueError("No se pudo convertir el PDF a imagen")

        img_b64 = self._image_to_base64(img)
        rotation = self._check_orientation(img_b64)
        if rotation != 0:
            _logger().info("PDF is rotated %d°, rotating image", rotation)
            img = img.rotate(-rotation, expand=True)
            img_b64 = self._image_to_base64(img)

        return self._extract_with_vision([img_b64])

    def _extract_with_text(self, text: str) -> dict:
        """Extract data from plain text — no PDF or image needed."""
        _logger().info("=== Text-only extraction === text_len=%d", len(text))
        prompt_with_text = (
            f"{self.prompt}\n\n--- TEXTO DEL DOCUMENTO ---\n{text}\n--- FIN DEL TEXTO ---"
        )
        message = HumanMessage(content=prompt_with_text)
        result = self.structured_llm.invoke([message])
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        _logger().info("Text extraction result: %s", result)
        return result

    def _extract_raw_pdf(self, pdf_path: Path) -> dict:
        """Send the raw PDF bytes to providers with native PDF support."""
        pdf_data = pdf_path.read_bytes()
        pdf_b64_len = len(base64.b64encode(pdf_data))
        _logger().info(
            "=== Raw PDF extraction (native) === pdf_bytes=%d b64_len=%d",
            len(pdf_data),
            pdf_b64_len,
        )
        pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")
        content = [
            {
                "type": "file",
                "source_type": "base64",
                "mime_type": "application/pdf",
                "data": pdf_base64,
            },
            {"type": "text", "text": self.prompt},
        ]
        message = HumanMessage(content=content)
        _logger().info("Invoking structured_llm (model=%s)", self.model_name)
        result = self.structured_llm.invoke([message])
        _logger().info("Raw LLM response type: %s", type(result).__name__)
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        _logger().info("Parsed extraction result: %s", result)
        return result

    def _extract_with_vision(
        self, base64_images: list[str] | None = None, *, image_url: str | None = None
    ) -> dict:
        if image_url:
            _logger().info("=== Vision extraction === mode=url")
            img_block = self._image_content(url=image_url)
        elif base64_images:
            b64_kb = len(base64_images[0]) // 1024
            _logger().info("=== Vision extraction === mode=b64 (%dKB)", b64_kb)
            img_block = self._image_content(b64=base64_images[0])
        else:
            raise ValueError("Se requiere base64_images o image_url")
        content = [img_block, {"type": "text", "text": self.prompt}]
        message = HumanMessage(content=content)
        result = self.structured_llm.invoke([message])
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        _logger().info("Extraction result: %s", result)
        return result

    def extract_file(self, file_path: Path, *, image_url: str | None = None) -> dict:
        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Tipo de archivo no soportado: {suffix}")

        if suffix in PDF_EXTENSIONS:
            return self._extract_with_pdf(file_path)
        elif image_url and image_url.startswith("https://"):
            # Check orientation before deciding whether to use URL or base64
            image = Image.open(file_path)
            if image.mode != "RGB":
                image = image.convert("RGB")
            image_b64 = self._image_to_base64(image)
            rotation = self._check_orientation(image_b64)
            if rotation != 0:
                _logger().info("Image rotated %d°, sending as base64 instead of URL", rotation)
                image = image.rotate(-rotation, expand=True)
                image_b64 = self._image_to_base64(image)
                return self._extract_with_vision([image_b64])
            return self._extract_with_vision(image_url=image_url)
        else:
            base64_images = self._load_image_file(file_path)
            if not base64_images:
                raise ValueError("No se pudo procesar el archivo")
            return self._extract_with_vision(base64_images)
