import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from src.experiments.experiment_runner import ExperimentRunner
from src.utils.file_utils import get_pdf_files


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run bank statement extraction")
    parser.add_argument(
        "--parser",
        type=str,
        choices=[
            "regex",
            "pdfplumber",
            "layoutlm",
            "hybrid",
            "claude",
            "claude_vision",
            "claude_ocr",
            "all",
        ],
        default="pdfplumber",
        help=(
            "Parser to use: regex, pdfplumber, layoutlm, hybrid, claude, "
            "claude_vision, claude_ocr, or all"
        ),
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

    if args.parser == "regex":
        print("\nRunning Regex extraction...")
        from src.extraction.regex_parser import RegexParser

        regex_parser = RegexParser()
        experiment.run_experiment(regex_parser, pdf_files, "regex_parser")

    elif args.parser == "pdfplumber":
        print("\nRunning PDFPlumber extraction...")
        from src.extraction.pdfplumber_parser import PDFPlumberParser

        pdfplumber_parser = PDFPlumberParser()
        experiment.run_experiment(pdfplumber_parser, pdf_files, "pdfplumber_parser")

    elif args.parser == "layoutlm":
        print("\nRunning LayoutLM extraction...")
        from src.extraction.layoutlm_parser import LayoutLMParser

        layoutlm_parser = LayoutLMParser()
        experiment.run_experiment(layoutlm_parser, pdf_files, "layoutlm_parser")

    elif args.parser == "hybrid":
        print("\nRunning Hybrid (PDFPlumber + Ollama) extraction...")
        from src.extraction.hybrid_parser import HybridParser

        hybrid_parser = HybridParser()
        experiment.run_experiment(hybrid_parser, pdf_files, "hybrid_parser")

    elif args.parser == "claude":
        print("\nRunning Claude (Haiku) extraction...")
        from src.extraction.claude_parser import ClaudeParser

        claude_parser = ClaudeParser()
        experiment.run_experiment(claude_parser, pdf_files, "claude_parser")

    elif args.parser == "claude_vision":
        print("\nRunning Claude Vision (Haiku) extraction...")
        from src.extraction.claude_vision_parser import ClaudeVisionParser

        claude_vision_parser = ClaudeVisionParser()
        experiment.run_experiment(claude_vision_parser, pdf_files, "claude_vision_parser")

    elif args.parser == "claude_ocr":
        print("\nRunning Claude with OCR (Tesseract + Haiku) extraction...")
        from src.extraction.claude_ocr_parser import ClaudeOCRParser

        claude_ocr_parser = ClaudeOCRParser()
        experiment.run_experiment(claude_ocr_parser, pdf_files, "claude_ocr_parser")

    elif args.parser == "all":
        print("\nRunning comparison of all parsers...")
        from src.extraction.claude_parser import ClaudeParser
        from src.extraction.pdfplumber_parser import PDFPlumberParser
        from src.extraction.regex_parser import RegexParser

        parsers = {
            "regex_parser": RegexParser(),
            "pdfplumber_parser": PDFPlumberParser(),
            "claude_parser": ClaudeParser(),
        }
        experiment.compare_parsers(parsers, pdf_files)

    print("\n✓ Extraction complete!")


if __name__ == "__main__":
    main()
