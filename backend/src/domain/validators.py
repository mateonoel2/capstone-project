import re

from src.domain.constants import CLABE_LENGTH, UNKNOWN_ACCOUNT

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


def validate_clabe(clabe: str) -> bool:
    if not clabe or clabe == UNKNOWN_ACCOUNT:
        return False
    return bool(re.match(rf"^\d{{{CLABE_LENGTH}}}$", clabe))
