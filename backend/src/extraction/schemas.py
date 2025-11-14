from pydantic import BaseModel, Field, field_validator

BANK_DICT_KUSHKI = {
    "ABC CAPITAL": "0001",
    "ACTINVER": "0002",
    "AFIRME": "0003",
    "AKALA": "0004",
    "ALTERNATIVOS": "0091",
    "ARCUS": "0005",
    "ASP INTEGRA OPC": "0006",
    "AUTOFIN": "0007",
    "AZTECA": "0008",
    "BAJIO": "0009",
    "BANAMEX": "0010",
    "BANCO FINTERRA": "0011",
    "BANCO S3": "0012",
    "BANCOMEXT": "0013",
    "BANCOPPEL": "0014",
    "BANCREA": "0015",
    "BANJERCITO": "0016",
    "BANK OF AMERICA": "0017",
    "BANKAOOL": "0018",
    "BANOBRAS": "0019",
    "BANORTE": "0020",
    "BANREGIO": "0021",
    "BANSEFI": "0022",
    "BANSI": "0023",
    "BANXICO": "0024",
    "BARCLAYS": "0025",
    "BBASE": "0026",
    "BBVA MEXICO": "0027",
    "BMONEX": "0028",
    "CAJA POP MEXICA": "0029",
    "CAJA TELEFONIST": "0030",
    "CB INTERCAM": "0031",
    "CI BOLSA": "0032",
    "CIBANCO": "0033",
    "COMPARTAMOS": "0034",
    "CONSUBANCO": "0035",
    "CREDICAPITAL": "0036",
    "CREDIT SUISSE": "0037",
    "CRISTOBAL COLON": "0038",
    "CoDi Valida": "0039",
    "DONDE": "0040",
    "EVERCORE": "0041",
    "FINAMEX": "0042",
    "FINCOMUN": "0043",
    "FOMPED": "0044",
    "FONDO (FIRA)": "0045",
    "GBM": "0046",
    "GEM - STP": "0090",
    "HIPOTECARIA FED": "0047",
    "HSBC": "0048",
    "ICBC": "0049",
    "INBURSA": "0050",
    "INDEVAL": "0051",
    "INMOBILIARIO": "0052",
    "INTERCAM BANCO": "0053",
    "INVERCAP": "0054",
    "INVEX": "0055",
    "JP MORGAN": "0056",
    "KUSPIT": "0057",
    "LIBERTAD": "0058",
    "MASARI": "0059",
    "MIFEL": "0060",
    "MIZUHO BANK": "0061",
    "MONEXCB": "0062",
    "MUFG": "0063",
    "MULTIVA BANCO": "0064",
    "MULTIVA CBOLSA": "0065",
    "NAFIN": "0066",
    "PAGATODO": "0067",
    "PROFUTURO": "0068",
    "REFORMA": "0069",
    "SABADELL": "0070",
    "SANTANDER": "0071",
    "SCOTIABANK": "0072",
    "SHINHAN": "0073",
    "STP": "0074",
    "TRANSFER": "0075",
    "UNAGRA": "0076",
    "VALMEX": "0077",
    "VALUE": "0078",
    "VE POR MAS": "0079",
    "VECTOR": "0080",
    "VOLKSWAGEN": "0081",
}


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
