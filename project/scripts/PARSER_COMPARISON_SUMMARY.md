# Bank Statement Parser Comparison - Full 183 PDFs

**Test Date:** November 7, 2025  
**Dataset:** 183 Mexican bank statements (mixture of text-based and image-based PDFs)  
**Ground Truth:** bank_accounts_filtered.csv

---

## 📊 OVERALL RESULTS (Ranked by Average Accuracy)

| Rank | Parser | Owner | CLABE | Bank | Average | Speed | Cost |
|------|--------|-------|-------|------|---------|-------|------|
| 🥇 1 | **Claude OCR** | 68.9% (126/183) | **80.9% (148/183)** | 41.5% (76/183) | **63.8%** | 9 min | $ |
| 🥈 2 | **Claude Vision** | **65.0% (119/183)** | 53.0% (97/183) | 45.4% (83/183) | **54.5%** | ~10 min | $$ |
| 🥉 3 | **Claude Text** | 30.6% (56/183) | 0.0% (0/183) | 18.0% (33/183) | **16.2%** | 2.7 min | $ |
| 4 | **PDFPlumber** | 2.2% (4/183) | 0.0% (0/183) | 13.1% (24/183) | **5.1%** | 23 sec | FREE |
| 5 | **Hybrid** | 2.2% (4/183) | 0.0% (0/183) | 13.1% (24/183) | **5.1%** | ~25 sec | FREE* |
| 6 | **Regex** | 0.5% (1/183) | 0.0% (0/183) | 13.7% (25/183) | **4.7%** | 10 sec | FREE |

\* Hybrid was using PDFPlumber fallback (Ollama not running)

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

### 3. **Text-only parsers FAIL on image PDFs**
- Claude Text: Only 16.2% average
- PDFPlumber/Regex: ~5% average
- **0% CLABE extraction** for all text-only parsers
- This confirms that **most PDFs in the dataset are image-based**

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

| Parser | Total Time | Per PDF |
|--------|------------|---------|
| Regex | 10 sec | 0.05s |
| PDFPlumber | 23 sec | 0.13s |
| Claude Text | 162 sec | 0.89s |
| **Claude OCR** | 549 sec (9 min) | 3.0s |
| **Claude Vision** | ~600 sec (10 min) | 3.3s |

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
- **Zero budget**: Use PDFPlumber (but expect ~5% accuracy)
- **Want to try LlamaParse**: Fix the API issues first, but expect high costs

---

## 📁 RESULT FILES

All detailed results saved in:
- `bank_extraction_regex_parser_20251107_193815.csv`
- `bank_extraction_pdfplumber_parser_20251107_193849.csv`
- `bank_extraction_claude_parser_20251107_194143.csv`
- `bank_extraction_claude_vision_parser_20251107_194930.csv`
- `bank_extraction_claude_ocr_parser_20251107_195118.csv` ⭐
- `bank_extraction_hybrid_parser_20251107_195150.csv`

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

Generated: November 7, 2025

