import base64
import json
import logging
import os
import re
from pathlib import Path

import anthropic
from anthropic.types import TextBlock
from pdf2image import convert_from_path
from PIL import Image

logger = logging.getLogger(__name__)

from src.constants import UNKNOWN_ACCOUNT, UNKNOWN_OWNER
from src.extraction.base_parser import BaseParser
from src.extraction.schemas import BankAccount
from src.extraction.validators import validate_clabe


class ClaudeVisionParser(BaseParser):
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-haiku-4-5-20251001",
        max_tokens: int = 1024,
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = model
        self.max_tokens = max_tokens
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _pdf_to_base64_images(self, pdf_path: Path, max_pages: int = 2) -> list[str]:
        try:
            images = convert_from_path(str(pdf_path), dpi=150, first_page=1, last_page=max_pages)

            base64_images = []
            for image in images:
                import io

                max_dimension = 1568
                if image.width > max_dimension or image.height > max_dimension:
                    ratio = min(max_dimension / image.width, max_dimension / image.height)
                    new_size = (int(image.width * ratio), int(image.height * ratio))
                    image = image.resize(new_size, Image.Resampling.LANCZOS)

                buffer = io.BytesIO()
                image.save(buffer, format="JPEG", quality=85)
                image_bytes = buffer.getvalue()
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
                base64_images.append(base64_image)

            return base64_images
        except Exception as e:
            logger.error("Error converting PDF to images: %s", e)
            return []

    def _extract_with_vision(self, base64_images: list[str]) -> dict:
        if not base64_images:
            return {}

        content = []

        for i, base64_image in enumerate(base64_images[:1]):
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_image,
                    },
                }
            )

        content.append(
            {
                "type": "text",
                "text": """Analiza esta carátula bancaria mexicana y extrae la
siguiente información:

1. Titular/Owner: Nombre completo del titular de la cuenta (persona o empresa)
2. CLABE: Número de 18 dígitos (CLABE interbancaria).
   IMPORTANTE: debe ser exactamente 18 dígitos numéricos consecutivos.
3. Banco: Nombre del banco (debe ser uno de: BBVA MEXICO, SANTANDER, BANAMEX,
   BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX)

Responde SOLO con un JSON válido en este formato exacto, sin texto adicional:
{
    "owner": "nombre completo del titular",
    "account_number": "18 dígitos de la CLABE",
    "bank_name": "nombre del banco en mayúsculas"
}

Si no encuentras algún campo, usa "Unknown" para owner y bank_name,
y "000000000000000000" para account_number.
NO inventes información. Solo extrae lo que está claramente visible en el documento.""",
            }
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0,
                messages=[{"role": "user", "content": content}],
            )

            text_blocks = [block for block in message.content if isinstance(block, TextBlock)]
            response_text = text_blocks[0].text if text_blocks else ""

            json_match = re.search(r"\{[^}]+\}", response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result

            return {}

        except Exception as e:
            logger.error("Error calling Claude Vision: %s", e)
            return {}

    def parse_file(self, file_path: Path) -> BankAccount:
        base64_images = self._pdf_to_base64_images(file_path)

        if not base64_images:
            return BankAccount(
                owner=UNKNOWN_OWNER, account_number=UNKNOWN_ACCOUNT, bank_name=UNKNOWN_OWNER
            )

        vision_result = self._extract_with_vision(base64_images)

        owner = vision_result.get("owner", UNKNOWN_OWNER) or UNKNOWN_OWNER
        account_number = (
            vision_result.get("account_number", UNKNOWN_ACCOUNT) or UNKNOWN_ACCOUNT
        )
        bank_name = vision_result.get("bank_name", UNKNOWN_OWNER) or UNKNOWN_OWNER

        if not validate_clabe(account_number):
            account_number = UNKNOWN_ACCOUNT

        return BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
