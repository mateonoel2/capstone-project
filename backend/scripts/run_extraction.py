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
        "--parser",
        type=str,
        choices=[
            "claude",
            "claude_vision",
            "claude_ocr",
            "all",
        ],
        default="claude_ocr",
        help="Parser to use: claude, claude_vision, claude_ocr, or all",
    )
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

    if args.parser == "claude":
        print("\nRunning Claude (Haiku) extraction...")
        from src.infrastructure.parsers.claude_text import ClaudeParser

        claude_parser = ClaudeParser()
        experiment.run_experiment(claude_parser, pdf_files, "claude_parser")

    elif args.parser == "claude_vision":
        print("\nRunning Claude Vision (Haiku) extraction...")
        from src.infrastructure.parsers.claude_vision import ClaudeVisionParser

        claude_vision_parser = ClaudeVisionParser()
        experiment.run_experiment(claude_vision_parser, pdf_files, "claude_vision_parser")

    elif args.parser == "claude_ocr":
        print("\nRunning Claude with OCR (Tesseract + Haiku) extraction...")
        from src.infrastructure.parsers.claude_ocr import ClaudeOCRParser

        claude_ocr_parser = ClaudeOCRParser()
        experiment.run_experiment(claude_ocr_parser, pdf_files, "claude_ocr_parser")

    elif args.parser == "all":
        print("\nRunning comparison of all parsers...")
        from src.infrastructure.parsers.claude_ocr import ClaudeOCRParser
        from src.infrastructure.parsers.claude_text import ClaudeParser
        from src.infrastructure.parsers.claude_vision import ClaudeVisionParser

        parsers = {
            "claude_parser": ClaudeParser(),
            "claude_vision_parser": ClaudeVisionParser(),
            "claude_ocr_parser": ClaudeOCRParser(),
        }
        experiment.compare_parsers(parsers, pdf_files)

    print("\n✓ Extraction complete!")


if __name__ == "__main__":
    main()
