import tempfile
import time
from pathlib import Path

from fastapi import UploadFile

from src.domain.entities import ApiCallResult, ExtractionError
from src.domain.schemas import BankAccount
from src.infrastructure.parsers.statement_parser import SUPPORTED_EXTENSIONS, StatementParser

ALLOWED_EXTENSIONS = SUPPORTED_EXTENSIONS


class ExtractionService:
    async def extract(self, file: UploadFile) -> tuple[BankAccount, ApiCallResult]:
        if not file.filename:
            raise ValueError("No se proporcionó un archivo")

        suffix = Path(file.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Tipo de archivo no soportado: {suffix}. "
                f"Formatos aceptados: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = Path(tmp_file.name)

            parser = StatementParser()
            start = time.monotonic()
            try:
                result = parser.parse_file(tmp_file_path)
            except ValueError as e:
                # ValueError = API worked, but doc is not a valid bank statement
                elapsed_ms = round((time.monotonic() - start) * 1000, 1)
                call_result = ApiCallResult(
                    model=parser.model_name,
                    success=False,
                    response_time_ms=elapsed_ms,
                    error_type="InvalidDocument",
                    error_message=str(e),
                )
                raise ExtractionError(str(e), call_result)
            except Exception as e:
                # Other exceptions = API failure
                elapsed_ms = round((time.monotonic() - start) * 1000, 1)
                call_result = ApiCallResult(
                    model=parser.model_name,
                    success=False,
                    response_time_ms=elapsed_ms,
                    error_type=type(e).__name__,
                    error_message=str(e)[:500],
                )
                raise ExtractionError(str(e), call_result)

            elapsed_ms = round((time.monotonic() - start) * 1000, 1)
            call_result = ApiCallResult(
                model=parser.model_name,
                success=True,
                response_time_ms=elapsed_ms,
            )
            return result, call_result
        finally:
            if tmp_file_path and tmp_file_path.exists():
                tmp_file_path.unlink()
