import base64
import io
import os
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from pdf2image import convert_from_path
from PIL import Image

from src.core.logger import get_logger
from src.domain.constants import UNKNOWN_ACCOUNT, UNKNOWN_OWNER
from src.domain.parser_interface import BaseParser
from src.domain.schemas import BankAccount, ExtractionOutput
from src.domain.validators import validate_clabe

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


class StatementParser(BaseParser):
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-haiku-4-5-20251001",
        max_tokens: int = 1024,
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model_name = model
        self.max_tokens = max_tokens
        self.llm = ChatAnthropic(
            model=model,
            api_key=self.api_key,
            max_tokens=max_tokens,
            temperature=0,
        )
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

    def _extract_with_vision(self, base64_images: list[str]) -> ExtractionOutput:
        content = [
            {
                "type": "image",
                "source_type": "base64",
                "data": base64_images[0],
                "mime_type": "image/jpeg",
            },
            {"type": "text", "text": EXTRACTION_PROMPT},
        ]
        message = HumanMessage(content=content)
        return self.structured_llm.invoke([message])

    def parse_file(self, file_path: Path) -> BankAccount:
        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Tipo de archivo no soportado: {suffix}")

        if suffix in PDF_EXTENSIONS:
            base64_images = self._pdf_to_base64_images(file_path)
        else:
            base64_images = self._load_image_file(file_path)

        if not base64_images:
            raise ValueError("No se pudo procesar el archivo")

        result = self._extract_with_vision(base64_images)

        if not result.is_bank_statement:
            raise ValueError("El documento no es un estado de cuenta bancario")

        owner = result.owner if result.owner != "Unknown" else UNKNOWN_OWNER
        raw_account = result.account_number
        account_number = raw_account if raw_account != "000000000000000000" else UNKNOWN_ACCOUNT
        bank_name = result.bank_name if result.bank_name != "Unknown" else UNKNOWN_OWNER

        if not validate_clabe(account_number):
            account_number = UNKNOWN_ACCOUNT

        # Fallback: if both bank and account are unknown, it's not a useful extraction
        if bank_name == UNKNOWN_OWNER and account_number == UNKNOWN_ACCOUNT:
            raise ValueError(
                "No se encontró información bancaria útil en el documento. "
                "Verifica que sea un estado de cuenta o carátula bancaria."
            )

        return BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
