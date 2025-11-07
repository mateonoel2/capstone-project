import re
import time
from pathlib import Path
from typing import Optional
from urllib.parse import unquote, urlparse

import pandas as pd
import requests


class FileDownloader:
    def __init__(self, output_dir: Path, max_retries: int = 3):
        self.output_dir = Path(output_dir)
        self.max_retries = max_retries
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        if pd.isna(filename) or not filename:
            return "Unknown"
        filename = str(filename)
        filename = re.sub(r"[^\w\s\-.]", "_", filename)
        filename = filename.replace(" ", "_")
        return filename[:200]

    @staticmethod
    def extract_filename_from_url(url: str) -> str:
        parsed = urlparse(url)
        path = unquote(parsed.path)

        filename_match = re.search(r"/([^/]+\.(pdf|jpg|jpeg|png)).*", url, re.IGNORECASE)
        if filename_match:
            return filename_match.group(1)

        parts = path.split("/")
        if parts:
            return parts[-1]

        return "unknown_file.pdf"

    @staticmethod
    def detect_file_type_from_content(filepath: Path) -> Optional[str]:
        with open(filepath, "rb") as f:
            header = f.read(12)

        if header.startswith(b"%PDF"):
            return ".pdf"
        elif header.startswith(b"\xff\xd8\xff"):
            return ".jpg"
        elif header.startswith(b"\x89PNG\r\n\x1a\n"):
            return ".png"
        elif header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
            return ".gif"
        elif header[0:4] == b"RIFF" and header[8:12] == b"WEBP":
            return ".webp"
        elif header.startswith(b"BM"):
            return ".bmp"
        elif header.startswith(b"II*\x00") or header.startswith(b"MM\x00*"):
            return ".tiff"
        else:
            return None

    def download_file(self, url: str, output_path: Path) -> bool:
        for attempt in range(self.max_retries):
            try:
                print(f"  Downloading... (attempt {attempt + 1}/{self.max_retries})")
                response = requests.get(url, timeout=30, stream=True)
                response.raise_for_status()

                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                file_size = output_path.stat().st_size
                print(f"  ✓ Downloaded successfully ({file_size:,} bytes)")
                return True

            except Exception as e:
                print(f"  ✗ Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"  ✗ Failed after {self.max_retries} attempts")
                    return False

    def download_from_csv(self, csv_path: Path, url_column: str = "Caratula") -> pd.DataFrame:
        df = pd.read_csv(csv_path)
        df["downloaded_file"] = ""
        df["download_status"] = ""

        print(f"\n{'=' * 80}")
        print("Bank Statement Downloader")
        print(f"{'=' * 80}\n")
        print(f"Total rows: {len(df)}")
        print(f"Output directory: {self.output_dir}\n")

        downloaded_count = 0
        skipped_count = 0
        failed_count = 0

        for idx, row in df.iterrows():
            try:
                row_num = idx + 2
                nickname = row.get("Nickname", "Unknown")
                school = row.get("Colegio", "Unknown")
                caratula_value = row.get(url_column, "")

                if pd.isna(nickname):
                    nickname = "Unknown"
                if pd.isna(school):
                    school = "Unknown"

                print(f"[{row_num}/{len(df) + 1}] {nickname} - {school}")

                if pd.isna(caratula_value) or caratula_value == "":
                    print("  ⊘ No file URL found")
                    df.at[idx, "download_status"] = "no_url"
                    skipped_count += 1
                    print()
                    continue

                url_match = re.search(r"https://[^\s\)]+", str(caratula_value))
                if not url_match:
                    print("  ⊘ Could not extract URL")
                    df.at[idx, "download_status"] = "invalid_url"
                    skipped_count += 1
                    print()
                    continue

                url = url_match.group(0)
                safe_nickname = self.sanitize_filename(nickname)

                temp_filename = f"row{row_num:03d}_{safe_nickname}_temp"
                temp_path = self.output_dir / temp_filename

                original_filename = self.extract_filename_from_url(url)
                url_extension = Path(original_filename).suffix

                final_filename_with_url_ext = f"row{row_num:03d}_{safe_nickname}{url_extension}"
                final_path = self.output_dir / final_filename_with_url_ext

                if final_path.exists():
                    print(f"  ⊙ Already exists: {final_filename_with_url_ext}")
                    df.at[idx, "downloaded_file"] = final_filename_with_url_ext
                    df.at[idx, "download_status"] = "already_exists"
                    skipped_count += 1
                    print()
                    continue

                success = self.download_file(url, temp_path)

                if success:
                    detected_ext = self.detect_file_type_from_content(temp_path)

                    if detected_ext:
                        final_filename = f"row{row_num:03d}_{safe_nickname}{detected_ext}"
                        print(f"  → Detected file type: {detected_ext}")
                    elif url_extension:
                        final_filename = final_filename_with_url_ext
                        print(f"  → Using URL extension: {url_extension}")
                    else:
                        final_filename = f"row{row_num:03d}_{safe_nickname}.bin"
                        print("  ⚠ Could not detect file type, saving as .bin")

                    final_path = self.output_dir / final_filename
                    temp_path.rename(final_path)
                    print(f"  ✓ Saved as: {final_filename}")

                    df.at[idx, "downloaded_file"] = final_filename
                    df.at[idx, "download_status"] = "success"
                    downloaded_count += 1
                else:
                    if temp_path.exists():
                        temp_path.unlink()
                    df.at[idx, "download_status"] = "failed"
                    failed_count += 1

                print()
                time.sleep(0.5)

            except Exception as e:
                print(f"  ✗ Unexpected error: {str(e)}")
                df.at[idx, "download_status"] = "error"
                failed_count += 1
                print()

        print(f"\n{'=' * 80}")
        print("Download Summary")
        print(f"{'=' * 80}")
        print(f"✓ Downloaded: {downloaded_count}")
        print(f"⊙ Skipped: {skipped_count}")
        print(f"✗ Failed: {failed_count}")
        print(f"Total processed: {len(df)}")
        print(f"{'=' * 80}\n")

        return df
