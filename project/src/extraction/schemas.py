from pydantic import BaseModel, Field


class BankAccount(BaseModel):
    owner: str = Field(
        ...,
        description="Dueño de la cuenta, puede ser una persona física o una entidad legal",
    )
    account_number: str = Field(..., description="número clabe de la cuenta (18 dígitos)")
    bank_name: str = Field(..., description="nombre del banco")
