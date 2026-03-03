import pandas as pd

from src.infrastructure.preprocessing.data_cleaner import DataCleaner


class TestDataCleaner:
    def test_remove_duplicates(self):
        df = pd.DataFrame({"name": ["Alice", "Bob", "Alice"], "value": [1, 2, 1]})

        cleaner = DataCleaner()
        df_clean = cleaner._remove_duplicates(df)

        assert len(df_clean) == 2

    def test_normalize_column_names(self):
        df = pd.DataFrame({"First Name": [1, 2], "Last Name": [3, 4]})

        cleaner = DataCleaner()
        df_clean = cleaner._normalize_column_names(df)

        assert "first_name" in df_clean.columns
        assert "last_name" in df_clean.columns
