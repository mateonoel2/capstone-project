import re
import shutil
import sys
from pathlib import Path

import pandas as pd

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


RFC_PERSON_PATTERN = r"^[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}$"
RFC_COMPANY_PATTERN = r"^[A-ZÑ&]{3}\d{6}[A-Z0-9]{3}$"
CURP_PATTERN = r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d$"
CLABE_LENGTH = 18


def is_valid_rfc(rfc: str) -> bool:
    if not isinstance(rfc, str):
        return False
    rfc_clean = rfc.strip().upper()
    return bool(re.match(RFC_PERSON_PATTERN, rfc_clean)) or bool(
        re.match(RFC_COMPANY_PATTERN, rfc_clean)
    )


def is_valid_curp(curp: str) -> bool:
    if not isinstance(curp, str):
        return False
    curp_clean = curp.strip().upper()
    return bool(re.match(CURP_PATTERN, curp_clean))


def is_valid_clabe(clabe) -> bool:
    if not isinstance(clabe, str) or not clabe or clabe.strip() == "":
        return False
    clabe_clean = clabe.strip()
    return len(clabe_clean) == CLABE_LENGTH and clabe_clean.isdigit()


def filter_by_validation(df: pd.DataFrame) -> pd.DataFrame:
    """Filter by CLABE/RFC/CURP validation and remove duplicates."""

    initial_count = len(df)
    print(f"Initial records: {initial_count}")

    df["CLABE"] = df["CLABE"].fillna("").astype(str)
    df["document_number"] = df["document_number"].fillna("").astype(str)
    df["document_type"] = df["document_type"].fillna("").astype(str)

    valid_clabe_mask = df["CLABE"].apply(is_valid_clabe)
    df = df[valid_clabe_mask]  # type: ignore[assignment]
    print(f"After CLABE validation (18 digits): {len(df)}")

    def is_valid_document(row):
        doc_type = str(row["document_type"]).strip().upper()
        doc_number = row["document_number"]

        if pd.isna(doc_number) or str(doc_number).strip() == "" or str(doc_number) == "nan":
            return False

        if doc_type == "RFC":
            return is_valid_rfc(doc_number)
        elif doc_type == "CURP":
            return is_valid_curp(doc_number)
        else:
            return False

    valid_document_mask = df.apply(is_valid_document, axis=1)
    df = df[valid_document_mask]  # type: ignore[assignment]
    print(f"After RFC/CURP validation: {len(df)}")

    before_dedup = len(df)
    df = df.drop_duplicates(subset=["CLABE"], keep="first")
    print(f"After removing duplicate CLABEs: {len(df)} (removed {before_dedup - len(df)})")

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(
                lambda x: str(x).replace("\n", " ").replace("\r", " ").strip() if pd.notna(x) else x
            )

    print(f"\nTotal records removed: {initial_count - len(df)}")
    print(f"Retention rate: {len(df) / initial_count * 100:.2f}%")

    return df


def filter_by_pdfs(df: pd.DataFrame, statements_dir: Path, output_dir: Path) -> pd.DataFrame:
    """Filter to only accounts with valid PDF files."""

    initial_count = len(df)
    print("\nFiltering to PDF accounts only...")
    print(f"Starting with: {initial_count} validated accounts")

    output_statements_dir = output_dir / "bank_statements"
    output_statements_dir.mkdir(parents=True, exist_ok=True)

    valid_records = []
    pdf_copied_count = 0
    missing_pdf_count = 0

    for idx, row in df.iterrows():
        downloaded_file = row.get("downloaded_file", "")

        if (
            pd.notna(downloaded_file)  # type: ignore[arg-type]
            and str(downloaded_file).strip()
            and str(downloaded_file) != "nan"
        ):
            filename = str(downloaded_file).strip()

            if filename.lower().endswith(".pdf"):
                source_file = statements_dir / filename

                if source_file.exists():
                    dest_file = output_statements_dir / filename
                    shutil.copy2(source_file, dest_file)
                    valid_records.append(row)
                    pdf_copied_count += 1
                else:
                    missing_pdf_count += 1

    valid_df = pd.DataFrame(valid_records)

    print(f"Records with valid PDFs: {len(valid_df)}")
    print(f"PDF files copied: {pdf_copied_count}")
    print(f"Records removed (no PDF): {initial_count - len(valid_df)}")
    if missing_pdf_count > 0:
        print(f"⚠️  Missing PDFs: {missing_pdf_count}")

    return valid_df


def main():
    project_root = Path(__file__).parent.parent

    input_file = project_root / "data" / "raw" / "bank_accounts_downloaded.csv"
    statements_dir = project_root / "data" / "raw" / "bank_statements"
    output_dir = project_root / "data" / "processed" / "pdfs"

    print("=" * 60)
    print("Process Bank Accounts")
    print("=" * 60)
    print(f"\nInput CSV: {input_file}")
    print(f"Statements: {statements_dir}")
    print(f"Output: {output_dir}\n")

    print("-" * 60)
    print("Step 1: Filter by CLABE/RFC/CURP validation")
    print("-" * 60)

    df = pd.read_csv(input_file, quotechar='"', skipinitialspace=True)
    filtered_df = filter_by_validation(df)

    print("\n" + "-" * 60)
    print("Step 2: Filter to PDF accounts only")
    print("-" * 60)

    pdf_df = filter_by_pdfs(filtered_df, statements_dir, output_dir)

    output_csv = output_dir / "bank_accounts_filtered.csv"
    pdf_df.to_csv(output_csv, index=False, quoting=1)

    print(f"\n✓ Output CSV: {output_csv}")
    print(f"✓ Output PDFs: {output_dir / 'bank_statements'}")

    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)
    print(f"\n📊 Final dataset: {len(pdf_df)} accounts with PDFs")
    print("📁 Ready for extraction experiments!")


if __name__ == "__main__":
    main()
