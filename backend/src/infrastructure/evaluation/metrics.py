from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import pdfplumber


def check_pdf_text_extraction(pdf_path: Path) -> Dict[str, object]:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_chars = 0
            total_pages = len(pdf.pages)

            for page in pdf.pages[:3]:
                text = page.extract_text()
                if text:
                    total_chars += len(text.strip())

            has_text = total_chars > 100
            avg_chars_per_page = total_chars / min(3, total_pages) if total_pages > 0 else 0

            return {
                "has_readable_text": has_text,
                "total_chars": total_chars,
                "avg_chars_per_page": avg_chars_per_page,
                "total_pages": total_pages,
                "quality": "good"
                if avg_chars_per_page > 500
                else ("medium" if avg_chars_per_page > 100 else "poor"),
            }
    except Exception as e:
        return {
            "has_readable_text": False,
            "total_chars": 0,
            "avg_chars_per_page": 0,
            "total_pages": 0,
            "quality": "error",
            "error": str(e),
        }


def strip_accents(text: str) -> str:
    """Remove Unicode accents: é→e, ó→o, etc."""
    import unicodedata

    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_legal_entity(text: str) -> str:
    """Normalize legal entity suffixes: A.C. → AC, S.C. → SC, etc."""
    import re

    # Remove dots from abbreviations (A.C. → AC, S.C. → SC, S.A. → SA)
    result = re.sub(r"\b([A-Z])\.\s*([A-Z])\.?\b", r"\1\2", text)
    # Handle S.A. DE C.V. → SA DE CV
    result = re.sub(r"\bS\.?\s*A\.?\s*DE\s*C\.?\s*V\.?\b", "SA DE CV", result)
    # Remove remaining standalone dots and extra commas
    result = re.sub(r"(?<!\d)\.(?!\d)", "", result)
    result = result.replace(",", "")
    # Collapse multiple spaces
    result = re.sub(r"\s+", " ", result).strip()
    return result


def normalize_text(text: str) -> str:
    if not text or text == "Unknown":
        return ""
    result = text.upper().strip().replace("  ", " ")
    result = strip_accents(result)
    result = normalize_legal_entity(result)
    return result


def validate_clabe(predicted: str, actual: str) -> Tuple[bool, str]:
    pred_norm = predicted.strip()
    actual_norm = actual.strip()

    if pred_norm == "000000000000000000":
        return False, "default_value"

    if pred_norm == actual_norm:
        return True, "exact_match"

    if len(pred_norm) != 18 or len(actual_norm) != 18:
        return False, "invalid_length"

    matching_digits = sum(1 for p, a in zip(pred_norm, actual_norm) if p == a)
    if matching_digits >= 16:
        return True, "partial_match"

    return False, "no_match"


def validate_owner(predicted: str, actual: str) -> Tuple[bool, str]:
    from difflib import SequenceMatcher

    pred_norm = normalize_text(predicted)
    actual_norm = normalize_text(actual)

    if not pred_norm or pred_norm == "UNKNOWN":
        return False, "not_extracted"

    if pred_norm == actual_norm:
        return True, "exact_match"

    # Word overlap check (≥70% of actual words present in prediction)
    pred_words = set(pred_norm.split())
    actual_words = set(actual_norm.split())

    if actual_words and len(pred_words & actual_words) / len(actual_words) >= 0.7:
        return True, "partial_match"

    # Fuzzy similarity fallback (handles remaining formatting differences)
    similarity = SequenceMatcher(None, pred_norm, actual_norm).ratio()
    if similarity >= 0.85:
        return True, "fuzzy_match"

    return False, "no_match"


def validate_bank(predicted: str, actual: str) -> Tuple[bool, str]:
    pred_norm = normalize_text(predicted)
    actual_norm = normalize_text(actual)

    if not pred_norm or pred_norm == "UNKNOWN":
        return False, "not_extracted"

    if pred_norm == actual_norm:
        return True, "exact_match"

    bank_aliases = {
        "BBVA MEXICO": ["BBVA", "BANCOMER"],
        "BANAMEX": ["CITIBANAMEX", "CITI"],
        "BMONEX": ["MONEX"],
        "BAJIO": ["BANBAJIO", "BANCO DEL BAJIO"],
    }

    for standard_name, aliases in bank_aliases.items():
        if actual_norm == standard_name:
            if pred_norm in aliases or any(alias in pred_norm for alias in aliases):
                return True, "alias_match"
        if pred_norm == standard_name:
            if actual_norm in aliases or any(alias in actual_norm for alias in aliases):
                return True, "alias_match"

    return False, "no_match"


def calculate_metrics(results_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> Dict:
    merged = pd.merge(
        results_df,
        ground_truth_df[["downloaded_file", "Owner", "CLABE", "banco"]],
        on="downloaded_file",
        how="inner",
        suffixes=("_pred", "_actual"),
    )

    metrics = {
        "total_files": len(merged),
        "owner": {"correct": 0, "incorrect": 0, "not_extracted": 0},
        "clabe": {"correct": 0, "incorrect": 0, "not_extracted": 0},
        "bank": {"correct": 0, "incorrect": 0, "not_extracted": 0},
    }

    for _, row in merged.iterrows():
        owner_correct, owner_type = validate_owner(str(row.get("owner", "")), str(row["Owner"]))
        clabe_correct, clabe_type = validate_clabe(
            str(row.get("account_number", "")), str(row["CLABE"])
        )
        bank_correct, bank_type = validate_bank(str(row.get("bank_name", "")), str(row["banco"]))

        metrics["owner"][
            "correct"
            if owner_correct
            else ("not_extracted" if owner_type == "not_extracted" else "incorrect")
        ] += 1
        metrics["clabe"][
            "correct"
            if clabe_correct
            else ("not_extracted" if clabe_type == "default_value" else "incorrect")
        ] += 1
        metrics["bank"][
            "correct"
            if bank_correct
            else ("not_extracted" if bank_type == "not_extracted" else "incorrect")
        ] += 1

    for field in ["owner", "clabe", "bank"]:
        total = metrics["total_files"]
        correct = metrics[field]["correct"]
        metrics[field]["precision"] = (correct / total * 100) if total > 0 else 0
        metrics[field]["recall"] = metrics[field]["precision"]
        metrics[field]["f1_score"] = metrics[field]["precision"]

    return metrics
