# Latest Updates

## New Features Added

### 1. Sidebar Navigation ✅
- Added a dark sidebar with navigation
- Two pages: "Extract PDF" and "Dashboard"
- Active state highlighting
- Professional layout with sticky sidebar

### 2. Bank Name Select Dropdown ✅
- Replaced text input with dropdown select
- Backend endpoint: `GET /extraction/banks`
- Returns 91 Mexican banks from BANK_DICT_KUSHKI
- Banks sorted alphabetically
- Includes bank codes for future use

### 3. Dashboard Page (Phase 2 Placeholder) ✅
- Created `/dashboard` route
- Metric cards showing:
  - Total Extractions
  - Corrections Made
  - Accuracy Rate
  - This Week's activity
- Placeholder content explaining Phase 2 features
- Professional UI matching extraction page

### 4. PDF Viewer Improvements ✅
- Zoom In/Out controls (50% - 300%)
- Rotate button (90° increments)
- Current zoom percentage display
- Better scrolling for full document visibility
- Icons for all controls

### 5. Backend Bug Fixes ✅
- Fixed SQLAlchemy session error
- Proper session management with refresh
- Added rollback on errors
- Try-finally blocks for cleanup

## File Changes

### New Files
- `frontend/components/sidebar.tsx` - Navigation sidebar
- `frontend/components/ui/select.tsx` - Select dropdown component
- `frontend/app/dashboard/page.tsx` - Dashboard page
- `project/application/constants.py` - Bank dictionary

### Modified Files
- `frontend/app/layout.tsx` - Added sidebar to layout
- `frontend/app/page.tsx` - Bank select + useEffect for banks
- `frontend/components/pdf-viewer.tsx` - Zoom and rotate controls
- `frontend/lib/api.ts` - Added getBanks() function
- `project/application/api/extraction.py` - Banks endpoint + session fix

## API Endpoints

### New
```
GET /extraction/banks
Response: { "banks": [{ "name": "...", "code": "..." }] }
```

### Fixed
```
POST /extraction/submit
- Fixed session management
- Proper error handling
```

## How to Use

### Backend
```bash
cd project
python scripts/run_api.py
```

### Frontend
```bash
cd frontend
npm run dev
```

### Navigation
- Click "Extract PDF" in sidebar to upload and extract
- Click "Dashboard" to view Phase 2 placeholder
- Use zoom controls on PDF viewer
- Select bank from dropdown (91 options)

## Database
The SQLite database at `project/data/extractions.db` now properly stores:
- Original extracted values
- User corrections
- Correction flags per field
- No more session errors!

## Next Steps (Phase 2)

To implement the full dashboard:
1. Add endpoint to fetch extraction logs
2. Calculate accuracy metrics
3. Build data table with filtering
4. Add charts for trends
5. Export functionality

## Testing

1. Upload a PDF bank statement
2. Verify bank dropdown shows all 91 banks
3. Use zoom controls on PDF
4. Select bank from dropdown
5. Submit form
6. Check database for entry
7. Navigate to Dashboard page

