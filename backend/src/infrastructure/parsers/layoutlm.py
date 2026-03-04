import logging
import re
from pathlib import Path
from typing import Optional

import torch
from pdf2image import convert_from_path
from PIL import Image
from transformers import AutoModelForTokenClassification, AutoProcessor

logger = logging.getLogger(__name__)

from src.domain.constants import UNKNOWN_ACCOUNT, UNKNOWN_OWNER
from src.domain.parser_interface import BaseParser
from src.domain.schemas import BankAccount
from src.domain.validators import bank_patterns, clabe_pattern, clabe_with_spaces_pattern


class LayoutLMParser(BaseParser):
    def __init__(self, model_name: str = "microsoft/layoutlmv3-base"):
        self.model_name = model_name
        self.processor = AutoProcessor.from_pretrained(model_name, apply_ocr=True)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)

        self.clabe_pattern = clabe_pattern
        self.clabe_with_spaces_pattern = clabe_with_spaces_pattern
        self.bank_patterns = bank_patterns

    def _pdf_to_images(self, file_path: Path) -> list[Image.Image]:
        if file_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            return [Image.open(file_path)]

        images = convert_from_path(str(file_path), first_page=1, last_page=3)
        return images

    def _extract_text_from_image(self, image: Image.Image) -> str:
        encoding = self.processor(image, return_tensors="pt")

        with torch.no_grad():
            self.model(**encoding)

        words = encoding.words[0] if hasattr(encoding, "words") else []
        text = " ".join(words) if words else ""

        return text

    def _extract_text_from_images(self, images: list[Image.Image]) -> str:
        all_text = []
        for image in images:
            text = self._extract_text_from_image(image)
            all_text.append(text)
        return "\n".join(all_text)

    def _extract_clabe(self, text: str) -> Optional[str]:
        matches = self.clabe_pattern.findall(text)
        if matches:
            return matches[0]

        matches_with_spaces = self.clabe_with_spaces_pattern.findall(text)
        if matches_with_spaces:
            clabe = re.sub(r"[\s\-]", "", matches_with_spaces[0])
            return clabe

        return None

    def _extract_bank_name(self, text: str) -> Optional[str]:
        for bank_name, pattern in self.bank_patterns.items():
            if pattern.search(text):
                return bank_name
        return None

    def _extract_owner(self, text: str) -> Optional[str]:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "titular" in line.lower() or "cliente" in line.lower():
                if i + 1 < len(lines):
                    potential_owner = lines[i + 1].strip()
                    if potential_owner and len(potential_owner) > 3:
                        return potential_owner

        owner_patterns = [
            r"Titular[:\s]+([A-ZÑÁÉÍÓÚ\s\.]+)",
            r"Cliente[:\s]+([A-ZÑÁÉÍÓÚ\s\.]+)",
            r"Nombre[:\s]+([A-ZÑÁÉÍÓÚ\s\.]+)",
        ]

        for pattern in owner_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def parse_file(self, file_path: Path) -> BankAccount:
        try:
            images = self._pdf_to_images(file_path)
            text = self._extract_text_from_images(images)
        except Exception as e:
            logger.error("Error processing document with LayoutLM: %s", e)
            text = ""

        owner = self._extract_owner(text) or UNKNOWN_OWNER
        account_number = self._extract_clabe(text) or UNKNOWN_ACCOUNT
        bank_name = self._extract_bank_name(text) or UNKNOWN_OWNER

        return BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
