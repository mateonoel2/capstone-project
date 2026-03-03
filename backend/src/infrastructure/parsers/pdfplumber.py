import re
from pathlib import Path
from typing import Optional

import pdfplumber

from src.domain.constants import UNKNOWN_ACCOUNT, UNKNOWN_OWNER
from src.domain.parser_interface import BaseParser
from src.domain.schemas import BankAccount
from src.domain.validators import bank_patterns, clabe_pattern, clabe_with_spaces_pattern
from src.infrastructure.preprocessing.ocr_processor import OCRProcessor


class PDFPlumberParser(BaseParser):
    def __init__(self, use_ocr_fallback: bool = True):
        self.use_ocr_fallback = use_ocr_fallback
        self.ocr = OCRProcessor() if use_ocr_fallback else None
        self.clabe_pattern = clabe_pattern
        self.clabe_with_spaces_pattern = clabe_with_spaces_pattern
        self.bank_patterns = bank_patterns

    def _extract_text_with_layout(self, file_path: Path) -> str:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages[:3]:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row:
                            text += " ".join([cell or "" for cell in row]) + "\n"

        if not text.strip() and self.use_ocr_fallback and self.ocr:
            text = self.ocr.process_pdf(file_path, preserve_layout=True)

        return text

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
        text = self._extract_text_with_layout(file_path)

        owner = self._extract_owner(text) or UNKNOWN_OWNER
        account_number = self._extract_clabe(text) or UNKNOWN_ACCOUNT
        bank_name = self._extract_bank_name(text) or UNKNOWN_OWNER

        return BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
