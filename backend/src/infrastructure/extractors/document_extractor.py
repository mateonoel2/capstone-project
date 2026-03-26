import base64
import io
import os
import re
from pathlib import Path

from langchain_core.messages import HumanMessage
from PIL import Image

from src.core.logger import get_logger

logger = get_logger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = PDF_EXTENSIONS | IMAGE_EXTENSIONS

EXTRACTION_PROMPT = """Analiza este documento y determina si es un estado de
cuenta o carátula bancaria mexicana.

Si ES un estado de cuenta o carátula bancaria, extrae:

1. Titular/Owner: Nombre completo del titular de la cuenta (persona o empresa).
   Busca el nombre que aparece en la sección de datos del cliente, NO el nombre
   del asesor, ejecutivo, o personas mencionadas en transacciones.

2. CLABE Interbancaria: Número de EXACTAMENTE 18 dígitos.
   IMPORTANTE — Distingue entre estos campos que son DIFERENTES:
   - CLABE Interbancaria: SIEMPRE tiene 18 dígitos. Busca etiquetas como
     "CLABE", "CLABE Interbancaria", "No. Cuenta CLABE", "Cuenta CLABE".
   - Número de cuenta: Típicamente 10-11 dígitos. NO es la CLABE.
   - Número de cliente: Típicamente 7-8 dígitos. NO es la CLABE.
   La CLABE aparece inmediatamente al costado o debajo de su etiqueta
   "CLABE Interbancaria". Lee el número que está junto a esa etiqueta.
   La CLABE puede aparecer con espacios (ej: "072 691 00844421773 3").
   Elimina todos los espacios y devuelve SOLO los 18 dígitos consecutivos.
   Lee cada dígito individualmente con cuidado, no agrupes ni asumas.
   Si ves la CLABE en la sección "PRODUCTOS DE VISTA" o "RESUMEN INTEGRAL",
   usa ese valor.

3. Banco: Nombre del banco (debe ser uno de: BBVA MEXICO, SANTANDER, BANAMEX,
   BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX, INBURSA)

Si NO es un estado de cuenta bancario (por ejemplo: facturas, contratos, recibos,
comprobantes de transferencia, documentos legales, etc.), marca is_valid_document
como false.

Si no encuentras algún campo, usa "Unknown" para owner y bank_name,
y "000000000000000000" para account_number.
NO inventes información. Solo extrae lo que está claramente visible en el documento."""

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

CLABE_RETRY_PROMPT = """El valor de CLABE que extrajiste NO tiene 18 dígitos.
Revisa el documento nuevamente. La CLABE interbancaria:
- SIEMPRE tiene EXACTAMENTE 18 dígitos
- Aparece etiquetada como "CLABE", "CLABE Interbancaria" o "No. Cuenta CLABE"
- NO es el número de cuenta (10-13 dígitos) ni el número de cliente (7-8 dígitos)
- Puede estar en la sección "PRODUCTOS DE VISTA" o "RESUMEN INTEGRAL"

Extrae nuevamente TODOS los campos del documento."""

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
        prompt: str = EXTRACTION_PROMPT,
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
        if output_schema:
            if isinstance(output_schema, dict) and "title" not in output_schema:
                output_schema = {"title": "extraction_output", **output_schema}
            self.structured_llm = self.llm.with_structured_output(output_schema)
        else:
            from src.domain.schemas import ExtractionOutput

            self.structured_llm = self.llm.with_structured_output(ExtractionOutput)

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

    def _image_to_base64(self, image: Image.Image) -> str:
        max_dimension = 2048
        if image.width > max_dimension or image.height > max_dimension:
            ratio = min(max_dimension / image.width, max_dimension / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)
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
            logger.info("Orientation check: %s → rotation %d°", direction, rotation)
            return rotation
        except Exception as e:
            logger.warning("Orientation check failed, assuming normal: %s", e)
            return 0

    def _load_image_file(self, image_path: Path) -> list[str]:
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # First pass: encode for orientation check
        image_b64 = self._image_to_base64(image)
        rotation = self._check_orientation(image_b64)

        if rotation != 0:
            logger.info("Rotating image %d° clockwise", rotation)
            # PIL rotate is counterclockwise, so negate
            image = image.rotate(-rotation, expand=True)
            image_b64 = self._image_to_base64(image)

        return [image_b64]

    def _pdf_to_image(self, pdf_path: Path) -> Image.Image | None:
        """Convert first page of PDF to PIL Image for orientation check."""
        try:
            from pdf2image import convert_from_path

            images = convert_from_path(str(pdf_path), first_page=1, last_page=1, dpi=200)
            return images[0] if images else None
        except Exception as e:
            logger.warning("PDF to image conversion failed: %s", e)
            return None

    def _extract_with_pdf(self, pdf_path: Path) -> dict:
        logger.info("=== PDF extraction ===")
        logger.info("Model: %s, prompt length: %d", self.model_name, len(self.prompt))

        # Check orientation by converting first page to image
        img = self._pdf_to_image(pdf_path)
        if img is not None:
            img_b64 = self._image_to_base64(img)
            rotation = self._check_orientation(img_b64)
            if rotation != 0:
                logger.info("PDF is rotated %d°, using vision extraction instead", rotation)
                img = img.rotate(-rotation, expand=True)
                img_b64 = self._image_to_base64(img)
                return self._extract_with_vision([img_b64])

        # Non-Anthropic models don't support native PDF — use vision
        if not self.provider["native_pdf"]:
            if img is None:
                img = self._pdf_to_image(pdf_path)
            if img is None:
                raise ValueError("No se pudo convertir el PDF a imagen")
            img_b64 = self._image_to_base64(img)
            return self._extract_with_vision([img_b64])

        pdf_data = pdf_path.read_bytes()
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
        result = self.structured_llm.invoke([message])
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        logger.info("Extraction result: %s", result)
        return result

    def _extract_with_vision(
        self, base64_images: list[str] | None = None, *, image_url: str | None = None
    ) -> dict:
        logger.info("=== Vision extraction ===")
        logger.info("Model: %s, prompt length: %d", self.model_name, len(self.prompt))
        if image_url:
            logger.info("Using direct URL (no base64 encoding)")
            img_block = self._image_content(url=image_url)
        elif base64_images:
            img_block = self._image_content(b64=base64_images[0])
        else:
            raise ValueError("Se requiere base64_images o image_url")
        content = [img_block, {"type": "text", "text": self.prompt}]
        message = HumanMessage(content=content)
        result = self.structured_llm.invoke([message])
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        logger.info("Extraction result: %s", result)
        return result

    def extract_file(self, file_path: Path, *, image_url: str | None = None) -> dict:
        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Tipo de archivo no soportado: {suffix}")

        if suffix in PDF_EXTENSIONS:
            return self._extract_with_pdf(file_path)
        elif image_url and image_url.startswith("https://"):
            return self._extract_with_vision(image_url=image_url)
        else:
            base64_images = self._load_image_file(file_path)
            if not base64_images:
                raise ValueError("No se pudo procesar el archivo")
            return self._extract_with_vision(base64_images)


def _needs_clabe_retry(result: dict) -> bool:
    """Check if the CLABE needs a retry (not 18 digits and not default)."""
    clabe = str(result.get("account_number", "000000000000000000"))
    digits = re.sub(r"[^\d]", "", clabe)
    if digits == "0" * 18:
        return False
    return len(digits) != 18


def retry_bank_statement_clabe(extractor: DocumentExtractor, file_path: Path, result: dict) -> dict:
    """Retry extraction if CLABE is not 18 digits. Bank-statement-specific."""
    if not _needs_clabe_retry(result):
        return result

    suffix = file_path.suffix.lower()
    bad_clabe = result.get("account_number", "")
    logger.info("CLABE '%s' is not 18 digits, retrying...", bad_clabe)

    # Stage 1: retry with reinforced prompt
    original_prompt = extractor.prompt
    extractor.prompt = extractor.prompt + "\n\n" + CLABE_RETRY_PROMPT
    try:
        if suffix in PDF_EXTENSIONS:
            retry_result = extractor._extract_with_pdf(file_path)
        else:
            retry_result = extractor._extract_with_vision()
        retry_clabe = str(retry_result.get("account_number", ""))
        retry_digits = re.sub(r"[^\d]", "", retry_clabe)
        if len(retry_digits) == 18 and retry_digits != "0" * 18:
            logger.info("Retry fixed CLABE: %s", retry_digits)
            return retry_result
        logger.info("Retry did not improve CLABE, keeping original")
    except Exception as e:
        logger.warning("Retry failed: %s", e)
    finally:
        extractor.prompt = original_prompt

    # Stage 2: try with 90° rotation (PDF only)
    if suffix in PDF_EXTENSIONS and _needs_clabe_retry(result):
        logger.info("Attempting rotation retry for PDF...")
        img = extractor._pdf_to_image(file_path)
        if img is not None:
            rotated = img.rotate(-90, expand=True)
            img_b64 = extractor._image_to_base64(rotated)
            try:
                rot_result = extractor._extract_with_vision([img_b64])
                rot_clabe = str(rot_result.get("account_number", ""))
                rot_digits = re.sub(r"[^\d]", "", rot_clabe)
                if len(rot_digits) == 18 and rot_digits != "0" * 18:
                    logger.info("Rotation retry fixed CLABE: %s", rot_digits)
                    return rot_result
                logger.info("Rotation retry did not improve CLABE")
            except Exception as e:
                logger.warning("Rotation retry failed: %s", e)

    return result
