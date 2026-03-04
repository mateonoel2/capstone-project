import tempfile
from pathlib import Path

from fastapi import UploadFile

from src.domain.schemas import BankAccount
from src.infrastructure.parsers.claude_ocr import ClaudeOCRParser
from src.infrastructure.parsers.claude_vision import ClaudeVisionParser

PARSER_MAP = {
    "claude_ocr": ClaudeOCRParser,
    "claude_vision": ClaudeVisionParser,
}


class ExtractionService:
    async def extract_from_pdf(self, file: UploadFile, parser: str = "claude_ocr") -> BankAccount:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported")
        if parser not in PARSER_MAP:
            raise ValueError(f"Unknown parser: {parser}. Options: {list(PARSER_MAP.keys())}")

        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = Path(tmp_file.name)

            parser_instance = PARSER_MAP[parser]()
            result = parser_instance.parse_file(tmp_file_path)

            tmp_file_path.unlink()

            return result

        except Exception as e:
            if tmp_file_path and tmp_file_path.exists():
                tmp_file_path.unlink()
            raise e
