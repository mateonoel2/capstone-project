import json
import re
from pathlib import Path
from typing import Optional

import ollama
import pdfplumber

from src.extraction.base_parser import BaseParser
from src.extraction.schemas import BankAccount
from src.preprocessing.ocr_processor import OCRProcessor


class HybridParser(BaseParser):
    def __init__(
        self, model: str = "llama3.2", fallback_to_regex: bool = True, use_ocr_fallback: bool = True
    ):
        self.model = model
        self.fallback_to_regex = fallback_to_regex
        self.use_ocr_fallback = use_ocr_fallback
        self.ocr = OCRProcessor() if use_ocr_fallback else None

        self.clabe_pattern = re.compile(r"\b\d{18}\b")
        self.clabe_with_spaces_pattern = re.compile(
            r"\b\d{3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}\b"
        )
        self.bank_patterns = {
            "BBVA MEXICO": re.compile(r"BBVA|Bancomer", re.IGNORECASE),
            "SANTANDER": re.compile(r"Santander", re.IGNORECASE),
            "BANAMEX": re.compile(r"Banamex|Citibanamex", re.IGNORECASE),
            "BANORTE": re.compile(r"Banorte", re.IGNORECASE),
            "HSBC": re.compile(r"HSBC", re.IGNORECASE),
            "SCOTIABANK": re.compile(r"Scotiabank", re.IGNORECASE),
            "AFIRME": re.compile(r"Afirme", re.IGNORECASE),
            "BAJIO": re.compile(r"Bajío|Bajio", re.IGNORECASE),
            "BANREGIO": re.compile(r"Banregio", re.IGNORECASE),
            "MIFEL": re.compile(r"Mifel", re.IGNORECASE),
            "BMONEX": re.compile(r"Bmonex|Monex", re.IGNORECASE),
        }

    def _extract_text_with_pdfplumber(self, file_path: Path) -> str:
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

    def _extract_with_ollama(self, text: str) -> dict:
        prompt = f"""Extrae la siguiente información de esta carátula bancaria mexicana:
1. Titular/Owner: Nombre completo del titular de la cuenta
2. CLABE: Número de 18 dígitos (CLABE interbancaria)
3. Banco: Nombre del banco

Texto del documento:
{text[:3000]}

Responde SOLO con un JSON válido en este formato exacto:
{{
    "owner": "nombre completo del titular",
    "account_number": "18 dígitos de la CLABE",
    "bank_name": "nombre del banco"
}}

Si no encuentras algún campo, usa "Unknown" para owner y bank_name, y "000000000000000000" para account_number.
"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1},
            )

            response_text = response["message"]["content"]

            json_match = re.search(r"\{[^}]+\}", response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result

            return {}

        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return {}

    def _extract_clabe_regex(self, text: str) -> Optional[str]:
        matches = self.clabe_pattern.findall(text)
        if matches:
            return matches[0]

        matches_with_spaces = self.clabe_with_spaces_pattern.findall(text)
        if matches_with_spaces:
            clabe = re.sub(r"[\s\-]", "", matches_with_spaces[0])
            return clabe

        return None

    def _extract_bank_name_regex(self, text: str) -> Optional[str]:
        for bank_name, pattern in self.bank_patterns.items():
            if pattern.search(text):
                return bank_name
        return None

    def _extract_owner_regex(self, text: str) -> Optional[str]:
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

    def _validate_clabe(self, clabe: str) -> bool:
        if not clabe or clabe == "000000000000000000":
            return False
        return bool(re.match(r"^\d{18}$", clabe))

    def parse_file(self, file_path: Path) -> BankAccount:
        text = self._extract_text_with_pdfplumber(file_path)

        ollama_result = self._extract_with_ollama(text)

        owner = ollama_result.get("owner", "Unknown")
        account_number = ollama_result.get("account_number", "000000000000000000")
        bank_name = ollama_result.get("bank_name", "Unknown")

        if self.fallback_to_regex:
            if not self._validate_clabe(account_number):
                regex_clabe = self._extract_clabe_regex(text)
                if regex_clabe:
                    account_number = regex_clabe

            if bank_name == "Unknown" or not bank_name:
                regex_bank = self._extract_bank_name_regex(text)
                if regex_bank:
                    bank_name = regex_bank

            if owner == "Unknown" or not owner:
                regex_owner = self._extract_owner_regex(text)
                if regex_owner:
                    owner = regex_owner

        return BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
