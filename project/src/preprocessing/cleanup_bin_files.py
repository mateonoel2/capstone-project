import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.preprocessing.file_downloader import FileDownloader


def main():
    project_root = Path(__file__).parent.parent
    statements_dir = project_root / "data" / "raw" / "bank_statements"

    bin_files = list(statements_dir.glob("*.bin"))

    if not bin_files:
        print("No .bin files found!")
        return

    print("=" * 60)
    print(f"Found {len(bin_files)} .bin files")
    print("=" * 60)

    downloader = FileDownloader(output_dir=statements_dir)

    converted = 0
    skipped = 0
    unknown = 0

    for bin_file in bin_files:
        print(f"\nChecking: {bin_file.name}")

        detected_type = downloader.detect_file_type_from_content(bin_file)

        if detected_type and detected_type.startswith("skip_"):
            file_type = detected_type.replace("skip_", "")
            print(f"  → Unsupported type: {file_type}")
            bin_file.unlink()
            print(f"  ✓ Deleted")
            skipped += 1

        elif detected_type:
            base_name = bin_file.stem
            new_file = bin_file.parent / f"{base_name}{detected_type}"
            bin_file.rename(new_file)
            print(f"  → Detected as: {detected_type}")
            print(f"  ✓ Renamed to: {new_file.name}")
            converted += 1

        else:
            print(f"  ⚠ Unknown type, keeping as .bin")
            unknown += 1

    print("\n" + "=" * 60)
    print("Cleanup Summary")
    print("=" * 60)
    print(f"Converted: {converted}")
    print(f"Deleted (unsupported): {skipped}")
    print(f"Unknown (kept as .bin): {unknown}")
    print(f"Total processed: {len(bin_files)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
