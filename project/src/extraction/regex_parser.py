import re
from pathlib import Path
from typing import Optional

import PyPDF2

from src.extraction.base_parser import BaseParser
from src.extraction.schemas import BankAccount


class RegexParser(BaseParser):
    def __init__(self):
        self.clabe_pattern = re.compile(r"\b\d{18}\b")
        self.bank_patterns = {
            "BBVA": re.compile(r"BBVA|Bancomer", re.IGNORECASE),
            "Santander": re.compile(r"Santander", re.IGNORECASE),
            "Banamex": re.compile(r"Banamex|Citibanamex", re.IGNORECASE),
            "Banorte": re.compile(r"Banorte", re.IGNORECASE),
            "HSBC": re.compile(r"HSBC", re.IGNORECASE),
            "Scotiabank": re.compile(r"Scotiabank", re.IGNORECASE),
            "Inbursa": re.compile(r"Inbursa", re.IGNORECASE),
        }

    def _extract_text_from_pdf(self, file_path: Path) -> str:
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages[:3]:
                text += page.extract_text()
        return text

    def _extract_clabe(self, text: str) -> Optional[str]:
        matches = self.clabe_pattern.findall(text)
        return matches[0] if matches else None

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

        owner = self._extract_owner(text) or "Unknown"
        account_number = self._extract_clabe(text) or "000000000000000000"
        bank_name = self._extract_bank_name(text) or "Unknown"

        return BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
