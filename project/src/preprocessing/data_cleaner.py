from pathlib import Path
from typing import Dict, List

import pandas as pd


class DataCleaner:
    def __init__(self):
        self.cleaning_report = []

    def clean_bank_accounts_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()
        initial_rows = len(df_clean)

        df_clean = self._remove_duplicates(df_clean)
        df_clean = self._normalize_column_names(df_clean)
        df_clean = self._clean_text_columns(df_clean)
        df_clean = self._handle_missing_values(df_clean)

        final_rows = len(df_clean)
        self.cleaning_report.append(
            {
                "step": "overall",
                "initial_rows": initial_rows,
                "final_rows": final_rows,
                "removed_rows": initial_rows - final_rows,
            }
        )

        return df_clean

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        initial_rows = len(df)
        df_clean = df.drop_duplicates()
        removed = initial_rows - len(df_clean)

        if removed > 0:
            self.cleaning_report.append({"step": "remove_duplicates", "removed_rows": removed})

        return df_clean

    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.strip().str.lower().str.replace(" ", "_")
        return df_clean

    def _clean_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()
        text_columns = df_clean.select_dtypes(include=["object"]).columns

        for col in text_columns:
            df_clean[col] = df_clean[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        return df_clean

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()
        missing_counts = df_clean.isnull().sum()

        for col, count in missing_counts.items():
            if count > 0:
                self.cleaning_report.append(
                    {
                        "step": "missing_values",
                        "column": col,
                        "missing_count": count,
                        "percentage": (count / len(df_clean)) * 100,
                    }
                )

        return df_clean

    def clean_extracted_results(self, results: List[Dict]) -> pd.DataFrame:
        df = pd.DataFrame(results)

        if "account_number" in df.columns:
            df = df[df["account_number"].str.match(r"^\d{18}$", na=False)]

        if "owner" in df.columns:
            df = df[df["owner"].notna() & (df["owner"] != "Unknown")]

        if "bank_name" in df.columns:
            df = df[df["bank_name"].notna() & (df["bank_name"] != "Unknown")]

        return df

    def get_cleaning_report(self) -> pd.DataFrame:
        if not self.cleaning_report:
            return pd.DataFrame()
        return pd.DataFrame(self.cleaning_report)

    def save_report(self, output_path: Path):
        report_df = self.get_cleaning_report()
        if not report_df.empty:
            report_df.to_csv(output_path, index=False)
