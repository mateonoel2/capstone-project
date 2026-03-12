import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Protocol

import pandas as pd

from src.core.logger import setup_logger


class Extractor(Protocol):
    def extract_file(self, file_path: Path) -> Any: ...


class ExperimentRunner:
    def __init__(self, experiment_name: str, output_dir: Path):
        self.experiment_name = experiment_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger(
            f"experiment_{experiment_name}", log_dir=self.output_dir / "logs"
        )

        self.results = []
        self.errors = []

    def run_experiment(
        self, extractor: Extractor, file_paths: List[Path], extractor_name: str
    ) -> pd.DataFrame:
        self.logger.info(f"Starting experiment: {self.experiment_name}")
        self.logger.info(f"Extractor: {extractor_name}")
        self.logger.info(f"Files to process: {len(file_paths)}")

        start_time = datetime.now()

        for i, file_path in enumerate(file_paths, 1):
            self.logger.info(f"Processing {i}/{len(file_paths)}: {file_path.name}")

            try:
                result = extractor.extract_file(file_path)

                result_dict = {
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "extractor": extractor_name,
                    "owner": result.owner,
                    "account_number": result.account_number,
                    "bank_name": result.bank_name,
                    "status": "success",
                    "error": None,
                }

                self.results.append(result_dict)
                self.logger.info(f"Success: {result.owner} - {result.bank_name}")

            except Exception as e:
                error_dict = {
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "extractor": extractor_name,
                    "owner": None,
                    "account_number": None,
                    "bank_name": None,
                    "status": "error",
                    "error": str(e),
                }

                self.results.append(error_dict)
                self.errors.append(error_dict)
                self.logger.error(f"Error: {str(e)}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.logger.info(f"Experiment completed in {duration:.2f} seconds")
        self.logger.info(f"Successful: {len(self.results) - len(self.errors)}")
        self.logger.info(f"Errors: {len(self.errors)}")

        df_results = pd.DataFrame(self.results)
        self._save_results(df_results, extractor_name)

        return df_results

    def _save_results(self, df: pd.DataFrame, extractor_name: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        csv_path = self.output_dir / f"{self.experiment_name}_{extractor_name}_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        self.logger.info(f"Results saved to: {csv_path}")

        summary = {
            "experiment_name": self.experiment_name,
            "extractor": extractor_name,
            "timestamp": timestamp,
            "total_files": len(df),
            "successful": len(df[df["status"] == "success"]),
            "errors": len(df[df["status"] == "error"]),
            "unique_banks": df["bank_name"].nunique(),
            "unique_owners": df["owner"].nunique(),
        }

        json_path = (
            self.output_dir / f"{self.experiment_name}_{extractor_name}_{timestamp}_summary.json"
        )
        with open(json_path, "w") as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Summary saved to: {json_path}")

    def compare_extractors(
        self, extractors: Dict[str, Extractor], file_paths: List[Path]
    ) -> pd.DataFrame:
        all_results = []

        for extractor_name, extractor in extractors.items():
            self.logger.info(f"\n{'=' * 60}")
            self.logger.info(f"Running extractor: {extractor_name}")
            self.logger.info(f"{'=' * 60}")

            results = self.run_experiment(extractor, file_paths, extractor_name)
            all_results.append(results)

        combined_df = pd.concat(all_results, ignore_index=True)

        comparison_path = self.output_dir / f"{self.experiment_name}_comparison.csv"
        combined_df.to_csv(comparison_path, index=False)
        self.logger.info(f"Comparison results saved to: {comparison_path}")

        return combined_df
