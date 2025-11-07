import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from src.preprocessing.file_downloader import FileDownloader


def main():
    load_dotenv()

    csv_path = project_root / "data" / "raw" / "bank_accounts_downloaded.csv"
    output_dir = project_root / "data" / "raw" / "bank_statements"

    print(f"Reading accounts from: {csv_path}")
    print(f"Downloading to: {output_dir}\n")

    downloader = FileDownloader(output_dir=output_dir)

    df_results = downloader.download_from_csv(csv_path)

    df_results.to_csv(csv_path, index=False)

    print(f"\n✓ Updated CSV saved to: {csv_path}")
    print(f"✓ Files saved to: {output_dir}/")


if __name__ == "__main__":
    main()
