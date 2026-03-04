from pydantic import BaseModel, Field, field_validator

from src.domain.constants import BANK_DICT_KUSHKI


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
