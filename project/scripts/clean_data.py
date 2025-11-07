import argparse
import sys
from pathlib import Path

import pandas as pd

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from src.preprocessing.data_cleaner import DataCleaner
from src.preprocessing.file_validator import FileValidator


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Clean and validate data")
    parser.add_argument(
        "--input-csv",
        type=str,
        default="data/raw/bank_accounts_downloaded.csv",
        help="Input CSV file to clean",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="data/processed/bank_accounts_clean.csv",
        help="Output cleaned CSV file",
    )
    parser.add_argument("--validate-files", action="store_true", help="Validate downloaded files")
    parser.add_argument(
        "--files-dir",
        type=str,
        default="data/raw/bank_statements",
        help="Directory containing files to validate",
    )

    args = parser.parse_args()

    input_csv = project_root / args.input_csv
    output_csv = project_root / args.output_csv
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print("Data Cleaning Pipeline")
    print(f"{'=' * 60}\n")

    print(f"Reading: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"Initial rows: {len(df)}")

    cleaner = DataCleaner()
    df_clean = cleaner.clean_bank_accounts_csv(df)

    print(f"Final rows: {len(df_clean)}")
    print(f"\nSaving to: {output_csv}")
    df_clean.to_csv(output_csv, index=False)

    report_path = output_csv.parent / "cleaning_report.csv"
    cleaner.save_report(report_path)
    print(f"Cleaning report saved to: {report_path}")

    if args.validate_files:
        print(f"\n{'=' * 60}")
        print("File Validation")
        print(f"{'=' * 60}\n")

        files_dir = project_root / args.files_dir
        print(f"Validating files in: {files_dir}")

        validator = FileValidator()
        validation_results = validator.validate_directory(files_dir)

        df_validation = pd.DataFrame(validation_results)
        validation_csv = output_csv.parent / "file_validation.csv"
        df_validation.to_csv(validation_csv, index=False)

        print("\nValidation Summary:")
        print(f"Total files: {len(validation_results)}")
        print(f"Valid files: {sum(1 for r in validation_results if not r['errors'])}")
        print(f"Invalid files: {sum(1 for r in validation_results if r['errors'])}")
        print(f"\nValidation report saved to: {validation_csv}")

    print(f"\n{'=' * 60}")
    print("✓ Data cleaning complete!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
