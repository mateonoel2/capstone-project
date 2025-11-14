import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd


def main():
    project_root = Path(__file__).parent.parent
    raw_dir = project_root / "data" / "raw"
    backup_dir = raw_dir / "backups"

    input_file = raw_dir / "bank accounts-Grid view.csv"
    output_file = raw_dir / "bank_accounts_downloaded.csv"

    if not input_file.exists():
        print(f"❌ Error: File not found: {input_file}")
        print("\nPlease export from Airtable as: bank accounts-Grid view.csv")
        return

    print("=" * 60)
    print("Upload Bank Accounts Data")
    print("=" * 60)
    print(f"\nInput:  {input_file.name}")
    print(f"Output: {output_file.name}")

    if output_file.exists():
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"bank_accounts_downloaded_{timestamp}.csv"
        shutil.copy2(output_file, backup_file)
        print(f"\n✓ Backed up old file to: {backup_file.name}")

        old_df = pd.read_csv(output_file)
        old_count = len(old_df)
    else:
        old_count = 0
        print("\nℹ️  No previous file found (first upload)")

    print("\n📥 Reading and cleaning new data...")
    new_df = pd.read_csv(input_file, quotechar='"', skipinitialspace=True)

    for col in new_df.columns:
        if new_df[col].dtype == "object":
            new_df[col] = new_df[col].apply(
                lambda x: str(x).replace("\n", " ").replace("\r", " ").strip() if pd.notna(x) else x
            )

    new_df.to_csv(output_file, index=False, quoting=1)

    print(f"✓ Cleaned and saved: {len(new_df)} records")

    if old_count > 0:
        diff = len(new_df) - old_count
        if diff > 0:
            print(f"✓ Added {diff} new records")
        elif diff < 0:
            print(f"⚠️  Removed {abs(diff)} records")
        else:
            print("✓ Same number of records")

    print("\n" + "=" * 60)
    print("Upload complete!")
    print("=" * 60)
    print("\nNext step: python scripts/download_statements.py")


if __name__ == "__main__":
    main()
