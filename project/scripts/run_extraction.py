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
        choices=["llama", "regex", "all"],
        default="llama",
        help="Parser to use: llama, regex, or all",
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

    if args.parser == "llama":
        print("\nRunning LlamaParse extraction...")
        from src.extraction.llama_parser import LlamaParser

        llama_parser = LlamaParser()
        experiment.run_experiment(llama_parser, pdf_files, "llama_parser")

    elif args.parser == "regex":
        print("\nRunning Regex extraction...")
        from src.extraction.regex_parser import RegexParser

        regex_parser = RegexParser()
        experiment.run_experiment(regex_parser, pdf_files, "regex_parser")

    elif args.parser == "all":
        print("\nRunning comparison of all parsers...")
        from src.extraction.llama_parser import LlamaParser
        from src.extraction.regex_parser import RegexParser

        parsers = {"llama_parser": LlamaParser(), "regex_parser": RegexParser()}
        experiment.compare_parsers(parsers, pdf_files)

    print("\n✓ Extraction complete!")


if __name__ == "__main__":
    main()
