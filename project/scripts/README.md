# Scripts

## Main Workflow (2 Scripts)

### 1. `upload_bank_accounts.py`

**Purpose:** Upload and clean new data from Airtable export

```bash
python scripts/upload_bank_accounts.py
```

- Input: `data/raw/bank accounts-Grid view.csv` (from Airtable)
- Output: `data/raw/bank_accounts_downloaded.csv` (cleaned)
- Backs up old file automatically
- Fixes embedded newlines and formatting issues

---

### 2. `process_accounts.py`

**Purpose:** Filter, validate, and prepare final dataset

```bash
python scripts/process_accounts.py
```

**Step 1: Validate**

- CLABE: 18 digits
- RFC/CURP: Correct format
- Remove duplicates

**Step 2: Filter to PDFs**

- Keep only accounts with PDF files
- Copy PDFs to processed folder

**Output:**

- `data/processed/pdfs/bank_accounts_filtered.csv`
- `data/processed/pdfs/bank_statements/` (PDFs only)

---

## Complete Workflow

```bash
# 1. Upload new data from Airtable
python scripts/upload_bank_accounts.py

# 2. Download statements (in src/preprocessing)
python src/preprocessing/download_statements.py

# 3. Process and filter accounts
python scripts/process_accounts.py
```

**Or run all at once:**

```bash
python scripts/upload_bank_accounts.py && \
python src/preprocessing/download_statements.py && \
python scripts/process_accounts.py
```

---

## Other Scripts

### `run_extraction.py`

Run extraction experiments on PDFs

```bash
# Test with 10 files
python scripts/run_extraction.py --parser regex --limit 10

# Full run
python scripts/run_extraction.py --parser regex

# Compare both parsers
python scripts/run_extraction.py --parser all
```

---

## Supporting Tools (in `src/preprocessing/`)

- `download_statements.py` - Download bank statement files
- `cleanup_bin_files.py` - Fix misdetected file types
- `file_downloader.py` - Core download functionality
- `file_validator.py` - File validation utilities
- `data_cleaner.py` - Data cleaning utilities
