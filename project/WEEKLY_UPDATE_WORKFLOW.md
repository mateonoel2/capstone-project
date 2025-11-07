# Weekly Bank Accounts Update Workflow

## Overview

Simple 3-step workflow to process bank account data for extraction experiments.

## Complete Workflow (3 Steps)

### 1. Upload Bank Accounts Data

```bash
python scripts/upload_bank_accounts.py
```

**What it does:**

- Backs up the old `bank_accounts_downloaded.csv` (if exists)
- Reads and **automatically cleans** the new `bank accounts-Grid view.csv`:
  - Fixes multi-row records (embedded newlines)
  - Normalizes whitespace
  - Ensures proper CSV formatting
- Shows how many records were added/removed
- Saves cleaned version as `bank_accounts_downloaded.csv`

**Output:**

- Backup: `data/raw/backups/bank_accounts_downloaded_YYYYMMDD_HHMMSS.csv`
- Updated: `data/raw/bank_accounts_downloaded.csv` (cleaned)

---

### 2. Download Bank Statements

```bash
python src/preprocessing/download_statements.py
```

**What it does:**

- Downloads files from URLs in the CSV
- **Automatically detects and filters** file types:
  - ✅ **Accepted:** PDF, JPG, PNG, GIF, WEBP, BMP, TIFF, HEIC
  - ⊘ **Skipped:** Excel (.xlsx), Word (.docx), ZIP files, executables
- Handles existing files (won't re-download)
- Updates CSV with download status

**Can run in background:**

```bash
python src/preprocessing/download_statements.py > download_log.txt 2>&1 &
```

---

### 3. Process Accounts (Filter & Prepare)

```bash
python scripts/process_accounts.py
```

**What it does:**

**Step 1: Filter by validation**

- Validates 18-digit CLABE numbers
- Validates RFC/CURP formats
- Removes duplicate CLABEs
- Cleans embedded newlines

**Step 2: Filter to PDFs only**

- Keeps only accounts with valid PDF files
- Copies PDFs to `data/processed/pdfs/bank_statements/`
- Creates final clean CSV

**Output:**

- `data/processed/pdfs/bank_accounts_filtered.csv` (accounts with PDFs)
- `data/processed/pdfs/bank_statements/` (PDF files)

---

### 4. Run Extraction Experiments (Optional)

```bash
# Test with a few files
python scripts/run_extraction.py --parser regex --limit 10

# Run on all files
python scripts/run_extraction.py --parser regex

# Compare both parsers
python scripts/run_extraction.py --parser all
```

**Available parsers:**

- `regex` - Pattern-based extraction (fast)
- `llama` - LLM-based extraction (accurate, requires API keys)
- `all` - Compare both parsers

---

## File Type Handling

### Supported File Types

The downloader now properly detects and handles:

| Type        | Extensions                                       | Status                     |
| ----------- | ------------------------------------------------ | -------------------------- |
| PDF         | `.pdf`                                           | ✅ Accepted                |
| Images      | `.jpg`, `.png`, `.gif`, `.webp`, `.bmp`, `.tiff` | ✅ Accepted                |
| HEIC        | `.heic`                                          | ✅ Accepted (Apple format) |
| Office      | `.xlsx`, `.docx`                                 | ⊘ Skipped                  |
| Archives    | `.zip`                                           | ⊘ Skipped                  |
| Executables | `.exe`                                           | ⊘ Skipped                  |
| Unknown     | `.bin`                                           | ⚠️ Kept for review         |

### Cleanup Existing .bin Files

If you have existing `.bin` files from previous downloads:

```bash
python src/preprocessing/cleanup_bin_files.py
```

This will:

- Detect actual file type
- Convert to proper extension (if supported)
- Delete unsupported files (Office docs, executables)

---

## Data Validation

### Bank Names

All bank names must match **BANK_DICT_KUSHKI** exactly:

- BBVA MEXICO, SANTANDER, BANAMEX, BANORTE, HSBC, SCOTIABANK
- AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX
- And 70+ more...

The schema automatically validates and normalizes bank names.

### Document Validation

- **RFC:**
  - Person: `^[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}$` (e.g., `OEEF970812PY1`)
  - Company: `^[A-ZÑ&]{3}\d{6}[A-Z0-9]{3}$` (e.g., `STE080926CA0`)
- **CURP:** `^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d$` (e.g., `FOMJ870825MDGLRH01`)
- **CLABE:** Exactly 18 digits (e.g., `012180015788025831`)

---

## Quick Commands

```bash
# 1. Upload new data
python scripts/upload_bank_accounts.py

# 2. Download statements
python src/preprocessing/download_statements.py

# 3. Process accounts
python scripts/process_accounts.py

# 4. Run experiments (optional)
python scripts/run_extraction.py --parser regex --limit 5
```

**Or run all at once:**

```bash
python scripts/upload_bank_accounts.py && \
python src/preprocessing/download_statements.py && \
python scripts/process_accounts.py
```

---

## Directory Structure

```
data/
├── raw/
│   ├── bank accounts-Grid view.csv     # Weekly export from Airtable
│   ├── bank_accounts_downloaded.csv    # Cleaned, working version
│   ├── backups/                         # Timestamped backups
│   └── bank_statements/                 # All downloaded files
│
├── processed/
│   ├── bank_accounts_filtered.csv      # All valid accounts
│   └── pdfs/
│       ├── bank_accounts_filtered.csv  # Only accounts with PDFs
│       └── bank_statements/            # Valid PDF files only
│
└── results/
    ├── bank_extraction_*.csv           # Extraction results
    └── logs/                            # Experiment logs
```

---

## Troubleshooting

### Issue: Multi-row records in CSV

**Solution:** The `update_bank_accounts.py` script now automatically fixes this.

### Issue: .bin files appearing

**Solution:** Run `python src/preprocessing/cleanup_bin_files.py` to identify and handle them.

### Issue: Download stuck or failing

**Solution:**

1. Stop the process
2. Re-run `python scripts/download_statements.py` - it will resume from where it stopped
3. Check network connection and Airtable URLs

### Issue: Files already exist error

**Solution:** The downloader skips existing files automatically.

---

## Notes

- **Backups:** All old files are automatically backed up with timestamps
- **Idempotent:** All scripts can be re-run safely - they handle existing data
- **CSV Cleaning:** Embedded newlines are automatically removed
- **File Detection:** Uses magic bytes, not just file extensions
