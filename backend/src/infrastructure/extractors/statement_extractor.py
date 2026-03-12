import base64
import io
import os
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from pdf2image import convert_from_path
from PIL import Image

from src.core.logger import get_logger

logger = get_logger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = PDF_EXTENSIONS | IMAGE_EXTENSIONS

EXTRACTION_PROMPT = """Analiza esta imagen de un documento y determina si es un estado de
cuenta o carátula bancaria mexicana.

Si ES un estado de cuenta o carátula bancaria, extrae:
1. Titular/Owner: Nombre completo del titular de la cuenta (persona o empresa)
2. CLABE: Número de 18 dígitos (CLABE interbancaria).
   IMPORTANTE: debe ser exactamente 18 dígitos numéricos consecutivos.
3. Banco: Nombre del banco (debe ser uno de: BBVA MEXICO, SANTANDER, BANAMEX,
   BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX)

Si NO es un estado de cuenta bancario (por ejemplo: facturas, contratos, recibos, documentos
legales, etc.), marca is_bank_statement como false.

Si no encuentras algún campo, usa "Unknown" para owner y bank_name,
y "000000000000000000" para account_number.
NO inventes información. Solo extrae lo que está claramente visible en el documento."""


class StatementExtractor:
    def __init__(
        self,
        prompt: str = EXTRACTION_PROMPT,
        model: str = "claude-haiku-4-5-20251001",
        output_schema: dict | None = None,
        api_key: str | None = None,
        max_tokens: int = 1024,
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model_name = model
        self.max_tokens = max_tokens
        self.prompt = prompt
        self.output_schema = output_schema
        self.llm = ChatAnthropic(
            model=model,
            api_key=self.api_key,
            max_tokens=max_tokens,
            temperature=0,
        )
        if output_schema:
            if isinstance(output_schema, dict) and "title" not in output_schema:
                output_schema = {"title": "extraction_output", **output_schema}
            self.structured_llm = self.llm.with_structured_output(output_schema)
        else:
            from src.domain.schemas import ExtractionOutput

            self.structured_llm = self.llm.with_structured_output(ExtractionOutput)

    def _image_to_base64(self, image: Image.Image) -> str:
        max_dimension = 1568
        if image.width > max_dimension or image.height > max_dimension:
            ratio = min(max_dimension / image.width, max_dimension / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _pdf_to_base64_images(self, pdf_path: Path, max_pages: int = 2) -> list[str]:
        images = convert_from_path(str(pdf_path), dpi=150, first_page=1, last_page=max_pages)
        return [self._image_to_base64(img) for img in images]

    def _load_image_file(self, image_path: Path) -> list[str]:
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        return [self._image_to_base64(image)]

    def _extract_with_vision(self, base64_images: list[str]) -> dict:
        content = [
            {
                "type": "image",
                "source_type": "base64",
                "data": base64_images[0],
                "mime_type": "image/jpeg",
            },
            {"type": "text", "text": self.prompt},
        ]
        message = HumanMessage(content=content)
        result = self.structured_llm.invoke([message])
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    def extract_file(self, file_path: Path) -> dict:
        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Tipo de archivo no soportado: {suffix}")

        if suffix in PDF_EXTENSIONS:
            base64_images = self._pdf_to_base64_images(file_path)
        else:
            base64_images = self._load_image_file(file_path)

        if not base64_images:
            raise ValueError("No se pudo procesar el archivo")

        return self._extract_with_vision(base64_images)
