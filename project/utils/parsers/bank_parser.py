from utils.parsers.parser_utils.parser import get_page_nodes, get_response_from_docs
from pydantic import BaseModel, Field


class BankSchema(BaseModel):
    owner: str = Field(
        ...,
        description="Dueño de la cuenta, puede ser una persona física o una entidad legal",
    )
    account_number: str = Field(
        ..., description="número clabe de la cuenta (18 dígitos)"
    )
    bank_name: str = Field(..., description="nombre del banco")


query = "En la carátula del estado de cuenta, encuentra el dueño de la cuenta, el número clabe de 18 dígitos y el nombre del banco"


def get_bank_parser_result(number_of_banks=1):
    result = []
    for i in range(1, number_of_banks + 1):
        docs = get_page_nodes(f"school_files/BANCO_{str(i)}.pdf")
        response = get_response_from_docs(docs, query, BankSchema)
        result.append(response)
    return result
