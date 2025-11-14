import json
import os
import re
from pathlib import Path

import anthropic
import pdfplumber

from src.extraction.base_parser import BaseParser
from src.extraction.schemas import BankAccount


class ClaudeParser(BaseParser):
    def __init__(
        self,
        api_key: str = None,
        model: str = "claude-3-5-haiku-latest",
        max_tokens: int = 1024,
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.max_tokens = max_tokens
        self.client = anthropic.Anthropic(api_key=self.api_key)

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
        return text

    def _extract_with_claude(self, text: str) -> dict:
        prompt = f"""Analiza esta carátula bancaria mexicana y extrae la siguiente información:

1. Titular/Owner: Nombre completo del titular de la cuenta (persona o empresa)
2. CLABE: Número de 18 dígitos (CLABE interbancaria).
   IMPORTANTE: debe ser exactamente 18 dígitos numéricos consecutivos.
3. Banco: Nombre del banco (debe ser uno de: BBVA MEXICO, SANTANDER, BANAMEX,
   BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX)

Texto del documento:
{text[:4000]}

Responde SOLO con un JSON válido en este formato exacto, sin texto adicional:
{{
    "owner": "nombre completo del titular",
    "account_number": "18 dígitos de la CLABE",
    "bank_name": "nombre del banco en mayúsculas"
}}

Si no encuentras algún campo, usa "Unknown" para owner y bank_name,
y "000000000000000000" para account_number.
NO inventes información. Solo extrae lo que está claramente visible en el texto.
"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            json_match = re.search(r"\{[^}]+\}", response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result

            return {}

        except Exception as e:
            print(f"Error calling Claude: {e}")
            return {}

    def _validate_clabe(self, clabe: str) -> bool:
        if not clabe or clabe == "000000000000000000":
            return False
        return bool(re.match(r"^\d{18}$", clabe))

    def parse_file(self, file_path: Path) -> BankAccount:
        text = self._extract_text_with_pdfplumber(file_path)

        if not text.strip():
            return BankAccount(
                owner="Unknown", account_number="000000000000000000", bank_name="Unknown"
            )

        claude_result = self._extract_with_claude(text)

        owner = claude_result.get("owner", "Unknown") or "Unknown"
        account_number = (
            claude_result.get("account_number", "000000000000000000") or "000000000000000000"
        )
        bank_name = claude_result.get("bank_name", "Unknown") or "Unknown"

        if not self._validate_clabe(account_number):
            account_number = "000000000000000000"

        return BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
