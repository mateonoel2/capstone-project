import tempfile
import time
from pathlib import Path

from fastapi import UploadFile

from src.domain.constants import UNKNOWN_ACCOUNT, UNKNOWN_OWNER
from src.domain.entities import ApiCallResult, ExtractionError, ParserConfigData
from src.domain.schemas import BankAccount
from src.domain.validators import validate_clabe
from src.infrastructure.parsers.statement_parser import SUPPORTED_EXTENSIONS, StatementParser

ALLOWED_EXTENSIONS = SUPPORTED_EXTENSIONS

# ID of the seeded default config
DEFAULT_CONFIG_ID = 1


def apply_bank_statement_postprocessing(raw: dict) -> dict:
    if not raw.get("is_bank_statement"):
        raise ValueError("El documento no es un estado de cuenta bancario")

    owner = raw.get("owner", "Unknown")
    if owner == "Unknown":
        owner = UNKNOWN_OWNER

    account_number = raw.get("account_number", "000000000000000000")
    if account_number == "000000000000000000":
        account_number = UNKNOWN_ACCOUNT

    bank_name = raw.get("bank_name", "Unknown")
    if bank_name == "Unknown":
        bank_name = UNKNOWN_OWNER

    if not validate_clabe(account_number):
        account_number = UNKNOWN_ACCOUNT

    # Normalize bank name
    bank_account = BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
    bank_name = bank_account.bank_name

    if bank_name == UNKNOWN_OWNER and account_number == UNKNOWN_ACCOUNT:
        raise ValueError(
            "No se encontró información bancaria útil en el documento. "
            "Verifica que sea un estado de cuenta o carátula bancaria."
        )

    return {
        "owner": owner,
        "account_number": account_number,
        "bank_name": bank_name,
    }


def _create_parser(config: ParserConfigData) -> StatementParser:
    return StatementParser(
        prompt=config.prompt,
        model=config.model,
        output_schema=config.output_schema,
    )


class ExtractionService:
    async def extract(
        self,
        file: UploadFile,
        config: ParserConfigData | None = None,
    ) -> tuple[dict, ApiCallResult, ParserConfigData | None]:
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

            if config:
                parser = _create_parser(config)
            else:
                parser = StatementParser()

            start = time.monotonic()
            try:
                raw_result = parser.parse_file(tmp_file_path)
            except ValueError as e:
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

            # Apply bank statement postprocessing for default parser
            is_default = config is None or config.is_default
            if is_default:
                try:
                    raw_result = apply_bank_statement_postprocessing(raw_result)
                except ValueError as e:
                    call_result = ApiCallResult(
                        model=parser.model_name,
                        success=False,
                        response_time_ms=elapsed_ms,
                        error_type="InvalidDocument",
                        error_message=str(e),
                    )
                    raise ExtractionError(str(e), call_result)

            call_result = ApiCallResult(
                model=parser.model_name,
                success=True,
                response_time_ms=elapsed_ms,
            )
            return raw_result, call_result, config
        finally:
            if tmp_file_path and tmp_file_path.exists():
                tmp_file_path.unlink()
