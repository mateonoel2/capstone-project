import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from src.core.file_utils import get_pdf_files
from src.infrastructure.evaluation.experiment_runner import ExperimentRunner


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run bank statement extraction")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/processed/pdfs/bank_statements",
        help="Directory containing bank statement files",
    )
    parser.add_argument(
        "--output-dir", type=str, default="data/results", help="Directory to save results"
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files to process")

    args = parser.parse_args()

    input_dir = project_root / args.input_dir
    output_dir = project_root / args.output_dir

    pdf_files = get_pdf_files(input_dir)

    if args.limit:
        pdf_files = pdf_files[: args.limit]

    print(f"\nFound {len(pdf_files)} PDF files")

    experiment = ExperimentRunner(experiment_name="bank_extraction", output_dir=output_dir)

    print("\nRunning StatementParser extraction...")
    from src.infrastructure.parsers.statement_parser import StatementParser

    statement_parser = StatementParser()
    experiment.run_experiment(statement_parser, pdf_files, "statement_parser")

    print("\n✓ Extraction complete!")


if __name__ == "__main__":
    main()
