# Frontend Setup Guide

This guide will help you set up and run the complete Bank Statement Extraction application with both backend and frontend.

## Quick Start

### 1. Backend Setup

First, ensure the backend API is running:

```bash
cd project

python scripts/run_api.py
```

The backend will start on http://localhost:8000

You can verify it's running by visiting:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 2. Frontend Setup

In a new terminal, navigate to the frontend directory and install dependencies:

```bash
cd frontend

npm install
```

### 3. Run Frontend

Start the development server:

```bash
npm run dev
```

The frontend will start on http://localhost:3000

## Complete Application Flow

1. **Backend** (http://localhost:8000):
   - Handles PDF extraction using Claude AI
   - Stores extraction logs in SQLite database
   - Provides REST API endpoints

2. **Frontend** (http://localhost:3000):
   - Modern UI for uploading PDFs
   - Side-by-side PDF viewer and form
   - Data verification and correction interface
   - Submits verified data back to backend

## Database

The SQLite database is automatically created at:
```
project/data/extractions.db
```

It stores:
- Original extracted values
- User-corrected final values
- Correction flags for accuracy tracking
- Timestamps and filenames

## Database Schema

```sql
CREATE TABLE extraction_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    filename TEXT,
    extracted_owner TEXT,
    extracted_bank_name TEXT,
    extracted_account_number TEXT,
    final_owner TEXT,
    final_bank_name TEXT,
    final_account_number TEXT,
    owner_corrected BOOLEAN,
    bank_name_corrected BOOLEAN,
    account_number_corrected BOOLEAN
);
```

## Accessing the Database

You can query the database directly using SQLite:

```bash
cd project/data
sqlite3 extractions.db

# Example queries:
SELECT * FROM extraction_logs;
SELECT COUNT(*) FROM extraction_logs WHERE owner_corrected = 1;
SELECT * FROM extraction_logs ORDER BY timestamp DESC LIMIT 10;
```

## Environment Requirements

### Backend
- Python 3.8+
- All dependencies from `project/requirements.txt`
- ANTHROPIC_API_KEY in `.env` file

### Frontend
- Node.js 18+
- npm/yarn/pnpm

## Troubleshooting

### Backend Issues

**Issue**: Import errors
```bash
# Solution: Ensure you're in the project directory
cd project
python -m pip install -r requirements.txt
```

**Issue**: Claude API errors
```bash
# Solution: Check your .env file has ANTHROPIC_API_KEY
cat project/.env | grep ANTHROPIC_API_KEY
```

### Frontend Issues

**Issue**: npm permission errors
```bash
# Solution: Try using a different package manager
npm install --legacy-peer-deps
# or
yarn install
# or
pnpm install
```

**Issue**: PDF not displaying
```bash
# Solution: Ensure react-pdf is properly installed
cd frontend
npm install react-pdf --force
```

**Issue**: CORS errors
```bash
# Solution: Backend already has CORS enabled for all origins
# Check that backend is running on port 8000
```

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- Frontend: Automatic on file save
- Backend: Automatic with `reload=True` in uvicorn

### Debugging

**Backend**:
```python
# Add print statements or use the FastAPI docs UI
# Visit http://localhost:8000/docs to test endpoints
```

**Frontend**:
```javascript
// Use browser DevTools console
// Check Network tab for API calls
// React DevTools for component state
```

### Testing the Flow

1. Use a sample PDF from `project/data/processed/pdfs/test_sample/`
2. Upload it through the frontend
3. Verify extraction results
4. Make a correction to one field
5. Submit the form
6. Check the database to confirm the log was created

```bash
# Quick database check
cd project/data
sqlite3 extractions.db "SELECT filename, owner_corrected, bank_name_corrected, account_number_corrected FROM extraction_logs ORDER BY timestamp DESC LIMIT 1;"
```

## Production Deployment

### Backend
```bash
cd project
pip install -r requirements.txt
python scripts/run_api.py
# or use gunicorn for production:
gunicorn application.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend
```bash
cd frontend
npm run build
npm start
# or deploy to Vercel, Netlify, etc.
```

## Next Steps (Phase 2)

After the extraction page is working, Phase 2 will add:
- Dashboard page showing all extractions
- Accuracy metrics and charts
- Filtering and search capabilities
- Data export functionality

## Support

For issues specific to:
- **Extraction logic**: Check `project/src/extraction/`
- **API endpoints**: Check `project/application/api/`
- **Frontend UI**: Check `frontend/components/`
- **Database**: Check `project/application/database.py`

