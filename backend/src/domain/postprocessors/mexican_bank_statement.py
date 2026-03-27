"""Postprocessor for Mexican bank statement (carátula bancaria) extraction.

Handles CLABE validation, retry logic, field normalization, and bank name matching
specific to Mexican banking documents.
"""

import re
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


def _logger():
    from src.core.logger import get_logger

    return get_logger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UNKNOWN_OWNER = "Unknown"
UNKNOWN_BANK = "Unknown"
UNKNOWN_ACCOUNT = "000000000000000000"
CLABE_LENGTH = 18

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

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

clabe_pattern = re.compile(r"\b\d{18}\b")
clabe_with_spaces_pattern = re.compile(
    r"\b\d{3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}\b"
)

bank_patterns = {
    "BBVA MEXICO": re.compile(r"BBVA|Bancomer", re.IGNORECASE),
    "SANTANDER": re.compile(r"Santander", re.IGNORECASE),
    "BANAMEX": re.compile(r"Banamex|Citibanamex", re.IGNORECASE),
    "BANORTE": re.compile(r"Banorte", re.IGNORECASE),
    "HSBC": re.compile(r"HSBC", re.IGNORECASE),
    "SCOTIABANK": re.compile(r"Scotiabank", re.IGNORECASE),
    "AFIRME": re.compile(r"Afirme", re.IGNORECASE),
    "BAJIO": re.compile(r"Bajío|Bajio", re.IGNORECASE),
    "BANREGIO": re.compile(r"Banregio", re.IGNORECASE),
    "MIFEL": re.compile(r"Mifel", re.IGNORECASE),
    "BMONEX": re.compile(r"Bmonex|Monex", re.IGNORECASE),
}

# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


def validate_clabe(clabe: str) -> bool:
    if not clabe or clabe == UNKNOWN_ACCOUNT:
        return False
    return bool(re.match(rf"^\d{{{CLABE_LENGTH}}}$", clabe))


# CLABE check digit weights: [3,7,1] repeating for positions 1-17
_CLABE_WEIGHTS = [3, 7, 1] * 6


def verify_clabe_checksum(clabe: str) -> bool:
    """Validate the CLABE check digit (position 18).

    The algorithm multiplies each of the first 17 digits by weights [3,7,1]
    (repeating), takes mod 10 of each product, sums them, and the check digit
    is (10 - sum % 10) % 10.
    """
    if not validate_clabe(clabe):
        return False
    digits = [int(d) for d in clabe]
    total = sum((d * w) % 10 for d, w in zip(digits[:17], _CLABE_WEIGHTS))
    expected_check = (10 - total % 10) % 10
    return digits[17] == expected_check


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class MexicanBankStatementSchema(BaseModel):
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
        digits = re.sub(r"[^\d]", "", v)
        if digits == "0" * 18 or not digits:
            return "000000000000000000"
        if 16 <= len(digits) < 18:
            digits = digits.zfill(18)
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
        for valid_name in BANK_DICT_KUSHKI:
            if v.upper() in valid_name or valid_name in v.upper():
                return valid_name
        return v


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

MEXICAN_BANK_STATEMENT_PROMPT = """Analiza este documento y determina si es un estado de
cuenta o carátula bancaria mexicana.

Si ES un estado de cuenta o carátula bancaria, extrae:

1. Titular/Owner: Nombre completo del titular de la cuenta (persona o empresa).
   Busca el nombre que aparece en la sección de datos del cliente, NO el nombre
   del asesor, ejecutivo, o personas mencionadas en transacciones.

2. CLABE Interbancaria: Número de EXACTAMENTE 18 dígitos.
   IMPORTANTE — Distingue entre estos campos que son DIFERENTES:
   - CLABE Interbancaria: SIEMPRE tiene 18 dígitos. Busca etiquetas como
     "CLABE", "CLABE Interbancaria", "No. Cuenta CLABE", "Cuenta CLABE".
   - Número de cuenta: Típicamente 10-11 dígitos. NO es la CLABE.
   - Número de cliente: Típicamente 7-8 dígitos. NO es la CLABE.
   La CLABE aparece inmediatamente al costado o debajo de su etiqueta
   "CLABE Interbancaria". Lee el número que está junto a esa etiqueta.

   FORMATOS COMUNES en que aparece la CLABE en documentos:
   - Con espacios cada 3 dígitos: "014 027 001 234 567 890"
   - Con espacios irregulares: "014 027 00123456789 0"
   - Sin espacios: "014027001234567890"
   - Con guiones: "014-027-001234567890"
   Elimina todos los espacios/guiones y devuelve SOLO los 18 dígitos consecutivos.

   Lee cada dígito individualmente de izquierda a derecha con cuidado.
   No agrupes, no asumas, no reordenes dígitos.
   Si ves la CLABE en la sección "PRODUCTOS DE VISTA" o "RESUMEN INTEGRAL",
   usa ese valor.

3. Banco: Nombre del banco (debe ser uno de: BBVA MEXICO, SANTANDER, BANAMEX,
   BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX, INBURSA)

Si NO es un estado de cuenta bancario (por ejemplo: facturas, contratos, recibos,
comprobantes de transferencia, documentos legales, etc.), marca is_valid_document
como false.

Si no encuentras algún campo, usa "Unknown" para owner y bank_name,
y "000000000000000000" para account_number.
NO inventes información. Solo extrae lo que está claramente visible en el documento."""

CLABE_RETRY_PROMPT = """La CLABE extraída es incorrecta (longitud incorrecta o dígito verificador
inválido). Tu ÚNICA tarea ahora es encontrar la CLABE interbancaria en este documento.

La CLABE interbancaria:
- SIEMPRE tiene EXACTAMENTE 18 dígitos
- Aparece etiquetada como "CLABE", "CLABE Interbancaria" o "No. Cuenta CLABE"
- NO es el número de cuenta (10-13 dígitos) ni el número de cliente (7-8 dígitos)
- Puede aparecer con espacios (ej: "014 027 00123456789 0") — lee cada dígito uno por uno
- Puede estar en la sección "PRODUCTOS DE VISTA" o "RESUMEN INTEGRAL"
- El dígito 18 es un dígito de control — si lo lees mal, la CLABE será inválida

Busca la etiqueta "CLABE" en el documento y lee los 18 dígitos que aparecen junto a ella,
uno por uno, de izquierda a derecha. No agrupes ni asumas valores."""

# ---------------------------------------------------------------------------
# CLABE retry logic
# ---------------------------------------------------------------------------


def _needs_clabe_retry(result: dict) -> bool:
    """Check if the CLABE needs a retry (missing, wrong length, or invalid checksum).

    When this function runs, the document has already been validated as a bank
    statement (is_valid_document check happens earlier in the pipeline). So if
    the model returned all-zeros it means it couldn't read the CLABE, and a
    retry with a reinforced prompt is worthwhile.
    """
    clabe = str(result.get("account_number", "000000000000000000"))
    digits = re.sub(r"[^\d]", "", clabe)
    if digits == "0" * 18:
        return True  # Model couldn't read CLABE — retry
    if len(digits) != 18:
        return True
    return not verify_clabe_checksum(digits)


def _is_valid_clabe_result(result: dict) -> bool:
    """Check if a result contains a valid CLABE (18 digits + valid checksum)."""
    clabe = str(result.get("account_number", ""))
    digits = re.sub(r"[^\d]", "", clabe)
    if len(digits) != 18 or digits == "0" * 18:
        return False
    return verify_clabe_checksum(digits)


def _merge_clabe(original: dict, retry_result: dict) -> dict:
    """Take only account_number from retry, keep everything else from original."""
    merged = dict(original)
    merged["account_number"] = retry_result.get("account_number", original.get("account_number"))
    return merged


# Minimal schema for CLABE-only retry — focuses model on reading just the number
CLABE_ONLY_SCHEMA = {
    "title": "clabe_extraction",
    "type": "object",
    "properties": {
        "account_number": {
            "type": "string",
            "description": (
                "CLABE interbancaria de EXACTAMENTE 18 dígitos. "
                "Elimina espacios y guiones. Usa '000000000000000000' si no se encuentra."
            ),
        },
    },
    "required": ["account_number"],
}


def retry_bank_statement_clabe(extractor, file_path: Path, result: dict) -> dict:
    """Single lightweight retry focused on CLABE using a minimal schema.

    Uses OCR text if available (cheapest), falls back to image for non-PDFs.
    """
    from langchain_core.messages import HumanMessage

    from src.infrastructure.extractors.document_extractor import PDF_EXTENSIONS

    if not _needs_clabe_retry(result):
        return result

    bad_clabe = result.get("account_number", "")
    _logger().info("CLABE '%s' invalid (bad checksum or length), single retry...", bad_clabe)

    suffix = file_path.suffix.lower()
    clabe_llm = extractor.llm.with_structured_output(CLABE_ONLY_SCHEMA)

    # For PDFs, try OCR text retry (cheapest)
    if suffix in PDF_EXTENSIONS:
        ocr_text = extractor._ocr_pdf(file_path)
        if ocr_text:
            _logger().info("CLABE retry using OCR text (%d chars)", len(ocr_text))
            prompt = f"{CLABE_RETRY_PROMPT}\n\n--- TEXTO DEL DOCUMENTO ---\n{ocr_text}\n--- FIN ---"
            try:
                retry_result = clabe_llm.invoke([HumanMessage(content=prompt)])
                if hasattr(retry_result, "model_dump"):
                    retry_result = retry_result.model_dump()
                _logger().info("CLABE retry result: %s", retry_result)
                if _is_valid_clabe_result(retry_result):
                    _logger().info("Retry fixed CLABE: %s", retry_result.get("account_number"))
                    return _merge_clabe(result, retry_result)
                _logger().info("Retry did not produce valid CLABE, keeping original")
            except Exception as e:
                _logger().warning("CLABE text retry failed: %s", e)
            return result

    # Image-based retry for non-PDF files
    try:
        from PIL import Image

        img = Image.open(file_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        image_b64 = extractor._image_to_base64(img)
        content = [
            extractor._image_content(b64=image_b64),
            {"type": "text", "text": CLABE_RETRY_PROMPT},
        ]
        _logger().info("CLABE retry using image")
        retry_result = clabe_llm.invoke([HumanMessage(content=content)])
        if hasattr(retry_result, "model_dump"):
            retry_result = retry_result.model_dump()
        _logger().info("CLABE retry result: %s", retry_result)
        if _is_valid_clabe_result(retry_result):
            _logger().info("Retry fixed CLABE: %s", retry_result.get("account_number"))
            return _merge_clabe(result, retry_result)
        _logger().info("Retry did not produce valid CLABE, keeping original")
    except Exception as e:
        _logger().warning("CLABE retry failed: %s", e)

    return result


# ---------------------------------------------------------------------------
# Field normalization / postprocessing
# ---------------------------------------------------------------------------


def apply_bank_statement_postprocessing(raw: dict) -> dict:
    owner = raw.get("owner", "Unknown")
    if owner == "Unknown":
        owner = UNKNOWN_OWNER

    account_number = raw.get("account_number", "000000000000000000")
    # Strip spaces/dashes (Banorte formats CLABE as "014 027 00123456789 0")
    account_number = "".join(c for c in account_number if c.isdigit())
    # Take first 18 digits if extra check digit was included
    if len(account_number) > 18:
        account_number = account_number[:18]
    if account_number == "000000000000000000":
        account_number = UNKNOWN_ACCOUNT

    bank_name = raw.get("bank_name", "Unknown")
    if bank_name == "Unknown":
        bank_name = UNKNOWN_BANK

    # Keep best-effort CLABE (18 digits even if checksum fails) rather than zeroing out
    if not validate_clabe(account_number):
        account_number = UNKNOWN_ACCOUNT
    elif not verify_clabe_checksum(account_number):
        _logger().warning(
            "CLABE %s has invalid checksum but keeping as best-effort", account_number
        )

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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def postprocess(extractor, file_path: Path, raw_result: dict) -> dict:
    """Full postprocessing pipeline: CLABE retry + field normalization."""
    _logger().info("Postprocessor input: %s", raw_result)
    result = retry_bank_statement_clabe(extractor, file_path, raw_result)
    _logger().info("After CLABE retry: %s", result)
    final = apply_bank_statement_postprocessing(result)
    _logger().info("After normalization: %s", final)
    return final
