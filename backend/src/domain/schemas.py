import re

from pydantic import BaseModel, Field, field_validator

from src.domain.constants import BANK_DICT_KUSHKI


class ExtractionOutput(BaseModel):
    """Structured output from Claude for bank statement extraction."""

    is_valid_document: bool = Field(
        ...,
        description="True si el documento es un estado de cuenta o carátula bancaria mexicana, "
        "False si es otro tipo de documento",
    )
    owner: str = Field(
        ...,
        description="Nombre completo del titular de la cuenta. Usa 'Unknown' si no se encuentra.",
    )
    account_number: str = Field(
        ...,
        description="CLABE interbancaria de EXACTAMENTE 18 dígitos. "
        "NO es el número de cuenta (10-11 dígitos) ni el número de cliente (7-8 dígitos). "
        "Busca la etiqueta 'CLABE' o 'CLABE Interbancaria'. "
        "Elimina espacios si los tiene. "
        "Usa '000000000000000000' si no se encuentra.",
    )
    bank_name: str = Field(
        ...,
        description="Nombre del banco en mayúsculas. Usa 'Unknown' si no se encuentra.",
    )

    @field_validator("account_number")
    @classmethod
    def normalize_clabe(cls, v: str) -> str:
        # Remove spaces, dots, dashes
        digits = re.sub(r"[^\d]", "", v)
        if digits == "0" * 18 or not digits:
            return "000000000000000000"
        # Zero-pad to 18 if close (e.g. leading zero was dropped)
        if 16 <= len(digits) < 18:
            digits = digits.zfill(18)
        # Truncate if over 18 (e.g. check digit appended)
        if len(digits) > 18:
            digits = digits[:18]
        return digits


class BankAccount(BaseModel):
    owner: str = Field(
        ...,
        description="Dueño de la cuenta, puede ser una persona física o una entidad legal",
    )
    account_number: str = Field(..., description="número clabe de la cuenta (18 dígitos)")
    bank_name: str = Field(
        ...,
        description=f"nombre del banco. Debe ser exactamente uno de: {
            ', '.join(BANK_DICT_KUSHKI.keys())
        }",
    )

    @field_validator("bank_name")
    @classmethod
    def validate_bank_name(cls, v: str) -> str:
        if v.upper() in BANK_DICT_KUSHKI:
            return v.upper()

        for valid_name in BANK_DICT_KUSHKI.keys():
            if v.upper() in valid_name or valid_name in v.upper():
                return valid_name

        return v
