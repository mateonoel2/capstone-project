import re
from pathlib import Path
from typing import Optional

import pypdf

from src.domain.constants import UNKNOWN_ACCOUNT, UNKNOWN_OWNER
from src.domain.parser_interface import BaseParser
from src.domain.schemas import BankAccount
from src.domain.validators import bank_patterns, clabe_pattern, clabe_with_spaces_pattern
from src.infrastructure.preprocessing.ocr_processor import OCRProcessor


class RegexParser(BaseParser):
    def __init__(self, use_ocr_fallback: bool = True):
        self.use_ocr_fallback = use_ocr_fallback
        self.ocr = OCRProcessor() if use_ocr_fallback else None
        self.clabe_pattern = clabe_pattern
        self.clabe_with_spaces_pattern = clabe_with_spaces_pattern
        self.bank_patterns = bank_patterns

    def _extract_text_from_pdf(self, file_path: Path) -> str:
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages[:3]:
                text += page.extract_text()

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
                    return lines[i + 1].strip()
        return None

    def parse_file(self, file_path: Path) -> BankAccount:
        text = self._extract_text_from_pdf(file_path)

        owner = self._extract_owner(text) or UNKNOWN_OWNER
        account_number = self._extract_clabe(text) or UNKNOWN_ACCOUNT
        bank_name = self._extract_bank_name(text) or UNKNOWN_OWNER

        return BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
