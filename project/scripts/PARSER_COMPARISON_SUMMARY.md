# Bank Statement Parser Comparison - Full 183 PDFs

**Test Date:** November 7, 2025  
**Dataset:** 183 Mexican bank statements (mixture of text-based and image-based PDFs)  
**Ground Truth:** bank_accounts_filtered.csv

---

## 📊 OVERALL RESULTS (Ranked by Average Accuracy)

### With OCR Fallback (UPDATED - Nov 7, 2025)

| Rank | Parser | Owner | CLABE | Bank | Average | Speed | Cost |
|------|--------|-------|-------|------|---------|-------|------|
| 🥇 1 | **Claude OCR** | 68.9% (126/183) | **80.9% (148/183)** | 41.5% (76/183) | **63.8%** | 9 min | $ |
| 🥈 2 | **Claude Vision** | **65.0% (119/183)** | 53.0% (97/183) | 45.4% (83/183) | **54.5%** | ~10 min | $$ |
| 🥉 3 | **Claude Text** | 30.6% (56/183) | 0.0% (0/183) | 18.0% (33/183) | **16.2%** | 2.7 min | $ |
| 4 | **PDFPlumber + OCR** | 3.8% (7/183) | 0.0% (0/183) | 33.9% (62/183) | **12.6%** | 4.2 min | FREE |
| 5 | **Regex + OCR** | 2.2% (4/183) | 0.0% (0/183) | 34.4% (63/183) | **12.2%** | 4.0 min | FREE |
| 6 | **Hybrid** | 2.2% (4/183) | 0.0% (0/183) | 13.1% (24/183) | **5.1%** | ~25 sec | FREE* |

\* Hybrid was using PDFPlumber fallback (Ollama not running)

### Without OCR Fallback (Original Results)

| Rank | Parser | Owner | CLABE | Bank | Average | Speed |
|------|--------|-------|-------|------|---------|-------|
| 1 | **PDFPlumber** | 2.2% (4/183) | 0.0% (0/183) | 13.1% (24/183) | **5.1%** | 23 sec |
| 2 | **Regex** | 0.5% (1/183) | 0.0% (0/183) | 13.7% (25/183) | **4.7%** | 10 sec |

---

## 🏆 KEY FINDINGS

### 1. **Winner: Claude OCR (Tesseract + Claude Haiku)**
- ✅ **Best CLABE extraction**: 80.9% (148/183) - The most critical field!
- ✅ **Best Owner extraction**: 68.9% (126/183)
- ✅ **Cheapest paid option**: Free OCR + Claude Text API
- ✅ **Processed ALL PDFs**: 183/183 successful (0 errors)
- ✅ **Handles both text and image PDFs**
- ⏱️ **Reasonable speed**: 9 minutes for 183 PDFs (~3s per PDF)

### 2. **Runner-up: Claude Vision**
- ✅ Good all-around performance (54.5% average)
- ✅ Best Owner extraction (65.0%)
- ✅ Handles image PDFs well
- ❌ More expensive (Vision API costs ~3x text API)
- ❌ Lower CLABE accuracy (53% vs 80.9%)

### 3. **OCR Fallback: Major improvement for free parsers!**
- **Regex + OCR**: 4.7% → 12.2% (2.6x improvement!)
  - Bank extraction jumped from 13.7% to 34.4% (+150%)
  - Speed increased from 10s to 4 min (due to OCR on 60% of PDFs)
- **PDFPlumber + OCR**: 5.1% → 12.6% (2.5x improvement!)
  - Bank extraction jumped from 13.1% to 33.9% (+160%)
  - Speed increased from 23s to 4.2 min
- **Still 0% CLABE**: Regex patterns can't interpret OCR'd text as well as LLMs

### 4. **Why LLMs dominate: Text interpretation matters**
- **Claude models** extract CLABEs from messy OCR text: 80.9% (OCR), 53% (Vision)
- **Regex patterns** fail on OCR artifacts: 0% CLABE despite having the text
- OCR text has spacing issues, formatting errors, and artifacts that break regex
- LLMs can understand context and fix OCR errors

---

## 📈 DETAILED BREAKDOWN

### CLABE Extraction (Most Critical Field)
1. **Claude OCR**: 80.9% ⭐⭐⭐⭐⭐
2. Claude Vision: 53.0%
3. ALL OTHERS: 0.0%

**Winner: Claude OCR by a huge margin!**

### Owner/Titular Extraction
1. **Claude OCR**: 68.9% ⭐⭐⭐⭐
2. Claude Vision: 65.0%
3. Claude Text: 30.6%
4. Others: <3%

### Bank Name Extraction
1. Claude Vision: 45.4%
2. **Claude OCR**: 41.5%
3. Claude Text: 18.0%
4. Others: ~13%

---

## 💰 COST ANALYSIS

### Per PDF Cost Estimates (approximate)

| Parser | Cost per PDF | Cost for 183 PDFs |
|--------|--------------|-------------------|
| Regex | $0 | $0 |
| PDFPlumber | $0 | $0 |
| Hybrid | $0* | $0* |
| **Claude Text** | ~$0.001 | ~$0.18 |
| **Claude OCR** | ~$0.001 | ~$0.18 |
| **Claude Vision** | ~$0.003-0.005 | ~$0.55-0.90 |

\* Assuming Ollama runs locally (free)

**Claude OCR provides the best accuracy/cost ratio!**

---

## ⚡ SPEED COMPARISON

| Parser | Total Time | Per PDF | Notes |
|--------|------------|---------|-------|
| Regex (no OCR) | 10 sec | 0.05s | Only works on text PDFs |
| PDFPlumber (no OCR) | 23 sec | 0.13s | Only works on text PDFs |
| **Regex + OCR** | 240 sec (4 min) | 1.3s | OCR on ~60% of PDFs |
| **PDFPlumber + OCR** | 252 sec (4.2 min) | 1.4s | OCR on ~60% of PDFs |
| Claude Text | 162 sec (2.7 min) | 0.89s | Only works on text PDFs |
| **Claude OCR** | 549 sec (9 min) | 3.0s | Works on all PDFs |
| **Claude Vision** | ~600 sec (10 min) | 3.3s | Works on all PDFs |

---

## 🎯 RECOMMENDATION

### **Use Claude OCR Parser for Production**

**Reasons:**
1. ✅ **Best CLABE accuracy** (80.9%) - The most important field for banking
2. ✅ **Best Owner accuracy** (68.9%)
3. ✅ **Most reliable** - 0 errors on 183 PDFs
4. ✅ **Best cost efficiency** - Same price as Claude Text but 4x better accuracy
5. ✅ **Handles all PDF types** - Both text and image-based
6. ✅ **Reasonable speed** - ~3 seconds per PDF

**Architecture:**
```
PDF → Tesseract OCR (FREE, local) → Claude 3.5 Haiku ($) → Extracted Data
```

**When to consider alternatives:**
- **Speed is critical & accuracy < 65% is acceptable**: Use Claude Vision
- **Zero budget & only need bank names**: Use PDFPlumber + OCR (34% bank accuracy, but 0% CLABE)
- **Want to try LlamaParse**: Fix the API issues first, but expect high costs (OCR + LLM double charge)

### **Key Insight: Why Claude OCR Dominates**

The comparison reveals a critical insight: **OCR alone is not enough**. You need intelligent text interpretation:

1. **Free parsers with OCR** (Regex, PDFPlumber):
   - ✅ Can extract text from image PDFs (via Tesseract)
   - ❌ Fail at interpreting messy OCR text (0% CLABE)
   - ❌ Regex patterns break on OCR artifacts (spacing, formatting)
   - Result: 12-13% average accuracy

2. **Claude models with OCR** (Claude OCR, Claude Vision):
   - ✅ Can extract text from image PDFs
   - ✅ Can understand context and fix OCR errors
   - ✅ Extract structured data from messy text
   - Result: 54-64% average accuracy

**The LLM layer is essential for production use.**

---

## 📁 RESULT FILES

### Original Results (without OCR fallback):
- `bank_extraction_regex_parser_20251107_193815.csv` (4.7% avg)
- `bank_extraction_pdfplumber_parser_20251107_193849.csv` (5.1% avg)
- `bank_extraction_hybrid_parser_20251107_195150.csv` (5.1% avg)

### Improved Results (with OCR fallback):
- `bank_extraction_regex_parser_20251107_200430.csv` (12.2% avg, +160%)
- `bank_extraction_pdfplumber_parser_20251107_200914.csv` (12.6% avg, +147%)

### Claude-based Parsers:
- `bank_extraction_claude_parser_20251107_194143.csv` (16.2% avg)
- `bank_extraction_claude_vision_parser_20251107_194930.csv` (54.5% avg)
- `bank_extraction_claude_ocr_parser_20251107_195118.csv` ⭐ (63.8% avg - **WINNER**)

---

## 🔄 NEXT STEPS

1. **Deploy Claude OCR parser** to production
2. **Monitor accuracy** on new PDFs
3. **Fine-tune OCR settings** if needed (language, DPI, layout preservation)
4. **Handle edge cases**:
   - Encrypted PDFs (1 found)
   - Very large images (compression warnings)
   - Multi-page statements
5. **Consider ensemble approach**: Use Claude OCR as primary, fall back to Claude Vision if OCR confidence is low

---

---

## 📊 IMPACT OF OCR FALLBACK

| Parser | Without OCR | With OCR | Improvement |
|--------|-------------|----------|-------------|
| **Regex** | 4.7% | 12.2% | **+160%** |
| **PDFPlumber** | 5.1% | 12.6% | **+147%** |

### What Changed:
- ✅ Bank extraction: ~13% → ~34% (2.6x improvement)
- ✅ Owner extraction: Slight improvement
- ❌ CLABE extraction: Still 0% (regex can't handle OCR artifacts)

### Why CLABE Still Fails:
OCR'd text has issues that break regex patterns:
- Spacing: `123 456 789 012 345 678` instead of `123456789012345678`
- Line breaks: CLABE split across lines
- OCR errors: `0` → `O`, `1` → `l`, etc.
- Context needed: LLMs can find and reconstruct CLABEs, regex cannot

**Conclusion**: Free parsers improved 2.5x with OCR, but still can't match LLM-based parsers for production use.

---

Generated: November 7, 2025
Last Updated: November 7, 2025 (Added OCR fallback analysis)

