"""Anonymization utilities for PII data.

Provides tokenization, masking, and pseudonymization functions to protect
personally identifiable information when exporting data for evaluation or analysis.
"""

import hashlib
import re


def tokenize_clabe(clabe: str) -> str:
    """Replace CLABE with a non-reversible token preserving format (18 digits)."""
    if not clabe or not re.match(r"^\d{18}$", clabe):
        return "000000000000000000"
    digest = hashlib.sha256(clabe.encode()).hexdigest()
    # Convert hex to digits, take first 18
    numeric = "".join(str(int(c, 16) % 10) for c in digest[:18])
    return numeric


def mask_rfc(rfc: str) -> str:
    """Mask RFC preserving first 4 and last 3 characters.

    Example: ABCD123456XYZ -> ABCD******XYZ
    """
    if not rfc or len(rfc) < 7:
        return "***RFC_ENMASCARADO***"
    return rfc[:4] + "*" * (len(rfc) - 7) + rfc[-3:]


def mask_curp(curp: str) -> str:
    """Mask CURP preserving first 4 and last 2 characters.

    Example: ABCD123456HDFRRL01 -> ABCD************01
    """
    if not curp or len(curp) < 6:
        return "***CURP_ENMASCARADO***"
    return curp[:4] + "*" * (len(curp) - 6) + curp[-2:]


def pseudonymize_name(name: str, salt: str = "") -> str:
    """Replace a name with a deterministic pseudonym.

    Same name + salt always produces the same pseudonym, enabling
    consistency across records without revealing the real name.
    """
    if not name:
        return "TITULAR_ANONIMO"
    digest = hashlib.sha256((name.strip().upper() + salt).encode()).hexdigest()[:8]
    return f"TITULAR_{digest.upper()}"


def anonymize_extraction_fields(fields: dict, salt: str = "") -> dict:
    """Anonymize all PII fields in an extraction result.

    Applies the appropriate anonymization technique to each field type:
    - Owner/titular names: pseudonymization
    - CLABE/account numbers: tokenization
    - Bank names: preserved (semi-public information)
    """
    if not fields:
        return {}

    anonymized = {}
    for key, value in fields.items():
        if not isinstance(value, str):
            anonymized[key] = value
            continue

        key_lower = key.lower()
        if "clabe" in key_lower or "account" in key_lower or "cuenta" in key_lower:
            anonymized[key] = tokenize_clabe(value) if re.match(r"^\d{18}$", value) else value
        elif "titular" in key_lower or "owner" in key_lower or "nombre" in key_lower:
            anonymized[key] = pseudonymize_name(value, salt)
        elif "rfc" in key_lower:
            anonymized[key] = mask_rfc(value)
        elif "curp" in key_lower:
            anonymized[key] = mask_curp(value)
        else:
            anonymized[key] = value

    return anonymized
