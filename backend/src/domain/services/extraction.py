import tempfile
import time
from pathlib import Path

from src.domain.constants import UNKNOWN_ACCOUNT, UNKNOWN_BANK, UNKNOWN_OWNER
from src.domain.entities import ApiCallResult, ExtractionError, ExtractorConfigData
from src.domain.schemas import BankAccount
from src.domain.validators import validate_clabe
from src.infrastructure.extractors.document_extractor import (
    SUPPORTED_EXTENSIONS,
    DocumentExtractor,
    retry_bank_statement_clabe,
)

ALLOWED_EXTENSIONS = SUPPORTED_EXTENSIONS


def apply_bank_statement_postprocessing(raw: dict) -> dict:
    if not raw.get("is_valid_document"):
        raise ValueError("El documento no es un estado de cuenta bancario")

    owner = raw.get("owner", "Unknown")
    if owner == "Unknown":
        owner = UNKNOWN_OWNER

    account_number = raw.get("account_number", "000000000000000000")
    # Strip spaces/dashes (Banorte formats CLABE as "072 691 00844421773 3")
    account_number = "".join(c for c in account_number if c.isdigit())
    # Take first 18 digits if extra check digit was included
    if len(account_number) > 18:
        account_number = account_number[:18]
    if account_number == "000000000000000000":
        account_number = UNKNOWN_ACCOUNT

    bank_name = raw.get("bank_name", "Unknown")
    if bank_name == "Unknown":
        bank_name = UNKNOWN_BANK

    if not validate_clabe(account_number):
        account_number = UNKNOWN_ACCOUNT

    # Normalize bank name
    bank_account = BankAccount(owner=owner, account_number=account_number, bank_name=bank_name)
    bank_name = bank_account.bank_name

    if bank_name == UNKNOWN_BANK and account_number == UNKNOWN_ACCOUNT:
        raise ValueError(
            "No se encontró información bancaria útil en el documento. "
            "Verifica que sea un estado de cuenta o carátula bancaria."
        )

    return {
        "owner": owner,
        "account_number": account_number,
        "bank_name": bank_name,
    }


def _create_extractor(config: ExtractorConfigData) -> DocumentExtractor:
    return DocumentExtractor(
        prompt=config.prompt,
        model=config.model,
        output_schema=config.output_schema,
    )


class ExtractionService:
    def extract(
        self,
        file_bytes: bytes,
        filename: str,
        config: ExtractorConfigData | None = None,
        image_url: str | None = None,
    ) -> tuple[dict, ApiCallResult, ExtractorConfigData | None]:
        if not filename:
            raise ValueError("No se proporcionó un archivo")

        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Tipo de archivo no soportado: {suffix}. "
                f"Formatos aceptados: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(file_bytes)
                tmp_file_path = Path(tmp_file.name)

            if config:
                extractor = _create_extractor(config)
            else:
                extractor = DocumentExtractor()

            start = time.monotonic()
            try:
                raw_result = extractor.extract_file(tmp_file_path, image_url=image_url)
            except ValueError as e:
                elapsed_ms = round((time.monotonic() - start) * 1000, 1)
                call_result = ApiCallResult(
                    model=extractor.model_name,
                    success=False,
                    response_time_ms=elapsed_ms,
                    error_type="InvalidDocument",
                    error_message=str(e),
                )
                raise ExtractionError(str(e), call_result)
            except Exception as e:
                elapsed_ms = round((time.monotonic() - start) * 1000, 1)
                call_result = ApiCallResult(
                    model=extractor.model_name,
                    success=False,
                    response_time_ms=elapsed_ms,
                    error_type=type(e).__name__,
                    error_message=str(e)[:500],
                )
                raise ExtractionError(str(e), call_result)

            elapsed_ms = round((time.monotonic() - start) * 1000, 1)

            # Apply bank-statement-specific logic only for bank statement extractors
            is_default = config is None or config.is_default
            has_bank_fields = config is None or "account_number" in config.output_schema.get(
                "properties", {}
            )
            if is_default and has_bank_fields:
                raw_result = retry_bank_statement_clabe(extractor, tmp_file_path, raw_result)
                try:
                    raw_result = apply_bank_statement_postprocessing(raw_result)
                except ValueError as e:
                    call_result = ApiCallResult(
                        model=extractor.model_name,
                        success=False,
                        response_time_ms=elapsed_ms,
                        error_type="InvalidDocument",
                        error_message=str(e),
                    )
                    raise ExtractionError(str(e), call_result)

            call_result = ApiCallResult(
                model=extractor.model_name,
                success=True,
                response_time_ms=elapsed_ms,
            )
            return raw_result, call_result, config
        finally:
            if tmp_file_path and tmp_file_path.exists():
                tmp_file_path.unlink()
