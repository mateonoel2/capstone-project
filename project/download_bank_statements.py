import pandas as pd
import requests
import os
from pathlib import Path
import re
from urllib.parse import urlparse, unquote
import time


def sanitize_filename(filename):
    if pd.isna(filename) or not filename:
        return "Unknown"
    filename = str(filename)
    filename = re.sub(r'[^\w\s\-.]', '_', filename)
    filename = filename.replace(' ', '_')
    return filename[:200]


def extract_filename_from_url(url):
    parsed = urlparse(url)
    path = unquote(parsed.path)
    
    filename_match = re.search(r'/([^/]+\.(pdf|jpg|jpeg|png)).*', url, re.IGNORECASE)
    if filename_match:
        return filename_match.group(1)
    
    parts = path.split('/')
    if parts:
        return parts[-1]
    
    return "unknown_file.pdf"


def detect_file_type_from_content(filepath):
    with open(filepath, 'rb') as f:
        header = f.read(12)
    
    if header.startswith(b'%PDF'):
        return '.pdf'
    elif header.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    elif header.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
        return '.gif'
    elif header[0:4] == b'RIFF' and header[8:12] == b'WEBP':
        return '.webp'
    elif header.startswith(b'BM'):
        return '.bmp'
    elif header.startswith(b'II*\x00') or header.startswith(b'MM\x00*'):
        return '.tiff'
    else:
        return None


def download_file(url, output_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"  Downloading... (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(output_path)
            print(f"  ✓ Downloaded successfully ({file_size:,} bytes)")
            return True
            
        except Exception as e:
            print(f"  ✗ Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"  ✗ Failed after {max_retries} attempts")
                return False


def download_bank_statements():
    csv_path = 'data/bank accounts-Grid view.csv'
    output_dir = 'data/bank_statements'
    
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(csv_path)
    
    df['downloaded_file'] = ''
    df['download_status'] = ''
    
    print(f"\n{'='*80}")
    print(f"Bank Statement Downloader")
    print(f"{'='*80}\n")
    print(f"Total rows: {len(df)}")
    print(f"Output directory: {output_dir}\n")
    
    downloaded_count = 0
    skipped_count = 0
    failed_count = 0
    
    for idx, row in df.iterrows():
        try:
            row_num = idx + 2
            nickname = row.get('Nickname', 'Unknown')
            school = row.get('Colegio', 'Unknown')
            caratula_value = row.get('Caratula', '')
            
            if pd.isna(nickname):
                nickname = 'Unknown'
            if pd.isna(school):
                school = 'Unknown'
            
            print(f"[{row_num}/{len(df)+1}] {nickname} - {school}")
            
            if pd.isna(caratula_value) or caratula_value == '':
                print(f"  ⊘ No file URL found")
                df.at[idx, 'download_status'] = 'no_url'
                skipped_count += 1
                print()
                continue
            
            url_match = re.search(r'https://[^\s\)]+', str(caratula_value))
            if not url_match:
                print(f"  ⊘ Could not extract URL from: {caratula_value[:50]}...")
                df.at[idx, 'download_status'] = 'invalid_url'
                skipped_count += 1
                print()
                continue
            
            url = url_match.group(0)
            
            safe_nickname = sanitize_filename(nickname)
            safe_school = sanitize_filename(school)
            
            temp_filename = f"row{row_num:03d}_{safe_nickname}_temp"
            temp_path = os.path.join(output_dir, temp_filename)
            
            original_filename = extract_filename_from_url(url)
            url_extension = os.path.splitext(original_filename)[1]
            
            final_filename_with_url_ext = f"row{row_num:03d}_{safe_nickname}{url_extension}"
            final_path = os.path.join(output_dir, final_filename_with_url_ext)
            
            if os.path.exists(final_path):
                print(f"  ⊙ Already exists: {final_filename_with_url_ext}")
                df.at[idx, 'downloaded_file'] = final_filename_with_url_ext
                df.at[idx, 'download_status'] = 'already_exists'
                skipped_count += 1
                print()
                continue
            
            final_filename_base = f"row{row_num:03d}_{safe_nickname}"
            existing_files = [f for f in os.listdir(output_dir) if f.startswith(final_filename_base) and not f.endswith('_temp')]
            if existing_files:
                print(f"  ⊙ Already exists: {existing_files[0]}")
                df.at[idx, 'downloaded_file'] = existing_files[0]
                df.at[idx, 'download_status'] = 'already_exists'
                skipped_count += 1
                print()
                continue
        
            print(f"  → Downloading...")
            success = download_file(url, temp_path)
            
            if success:
                detected_ext = detect_file_type_from_content(temp_path)
                
                if detected_ext:
                    final_filename = f"row{row_num:03d}_{safe_nickname}{detected_ext}"
                    print(f"  → Detected file type: {detected_ext}")
                elif url_extension:
                    final_filename = final_filename_with_url_ext
                    print(f"  → Using URL extension: {url_extension}")
                else:
                    final_filename = f"row{row_num:03d}_{safe_nickname}.bin"
                    print(f"  ⚠ Could not detect file type, saving as .bin")
                
                final_path = os.path.join(output_dir, final_filename)
                os.rename(temp_path, final_path)
                print(f"  ✓ Saved as: {final_filename}")
                
                df.at[idx, 'downloaded_file'] = final_filename
                df.at[idx, 'download_status'] = 'success'
                downloaded_count += 1
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                df.at[idx, 'download_status'] = 'failed'
                failed_count += 1
            
            print()
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ✗ Unexpected error: {str(e)}")
            df.at[idx, 'download_status'] = 'error'
            failed_count += 1
            print()
    
    output_csv = 'data/bank_accounts_with_files.csv'
    df.to_csv(output_csv, index=False)
    
    print(f"\n{'='*80}")
    print(f"Download Summary")
    print(f"{'='*80}")
    print(f"✓ Downloaded: {downloaded_count}")
    print(f"⊙ Skipped (already exists): {skipped_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Total processed: {len(df)}")
    print(f"\n✓ Updated CSV saved to: {output_csv}")
    print(f"✓ Files saved to: {output_dir}/")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    download_bank_statements()

