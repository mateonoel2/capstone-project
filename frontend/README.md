# Bank Statement Extraction Frontend

A Next.js frontend application for extracting and verifying bank account information from PDF statements. This application provides a modern, user-friendly interface for uploading PDF bank statements, viewing them side-by-side with extracted data, making corrections, and submitting verified results.

## Features

- **PDF Upload**: Drag-and-drop or click to upload PDF bank statements
- **Side-by-Side View**: View the PDF document alongside the extraction form
- **Real-time Extraction**: Automatic extraction using Claude AI when a PDF is uploaded
- **Data Verification**: Edit and correct extracted information before submission
- **Change Tracking**: Visual indicators show which fields have been modified from the original extraction
- **Data Logging**: All extractions and corrections are logged in the backend database for accuracy tracking

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **PDF Viewer**: react-pdf
- **Icons**: Lucide React

## Prerequisites

- Node.js 18+ 
- npm, yarn, or pnpm
- Backend API running on http://localhost:8000

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

## Development

Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Building for Production

```bash
npm run build
npm run start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx             # Main extraction page
│   └── globals.css          # Global styles and CSS variables
├── components/
│   ├── ui/                  # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── label.tsx
│   ├── file-upload.tsx      # Drag-and-drop file upload component
│   └── pdf-viewer.tsx       # PDF document viewer
├── lib/
│   ├── api.ts               # API client for backend communication
│   ├── utils.ts             # Utility functions (cn helper)
│   └── pdf-worker.ts        # PDF.js worker configuration
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.mjs
```

## API Integration

The frontend communicates with the backend API using two main endpoints:

### 1. Extract from PDF
- **Endpoint**: `POST /extraction/pdf`
- **Purpose**: Upload a PDF and receive extracted data
- **Response**: `{ owner, bank_name, account_number }`

### 2. Submit Extraction
- **Endpoint**: `POST /extraction/submit`
- **Purpose**: Submit verified data with correction tracking
- **Payload**:
  ```json
  {
    "filename": "statement.pdf",
    "extracted_owner": "Original Name",
    "extracted_bank_name": "Original Bank",
    "extracted_account_number": "123456",
    "final_owner": "Corrected Name",
    "final_bank_name": "Corrected Bank",
    "final_account_number": "123456"
  }
  ```

## Environment Variables

Create a `.env.local` file to customize the API URL:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Usage Flow

1. **Upload**: User uploads a PDF bank statement
2. **Extract**: Backend automatically extracts owner, bank name, and account number
3. **Review**: User reviews the extracted data while viewing the PDF
4. **Correct**: User edits any incorrect fields (highlighted in yellow)
5. **Submit**: User submits the verified data
6. **Log**: Backend logs both original and corrected data for accuracy tracking

## Visual Indicators

- **Yellow Border**: Field has been modified from the original extraction
- **Yellow Text**: Shows the original extracted value for comparison
- **Yellow Banner**: Indicates that changes have been made to the data
- **Loading States**: Spinners during extraction and submission
- **Success/Error Messages**: Clear feedback for all operations

## Keyboard & Accessibility

- Form inputs are fully keyboard accessible
- Proper ARIA labels for screen readers
- Focus states for all interactive elements
- Semantic HTML structure

## Future Enhancements (Phase 2)

- Dashboard page with extraction metrics
- Accuracy statistics and charts
- Filterable extraction history
- Export functionality for logged data
- User authentication

## Troubleshooting

### PDF Not Loading
- Ensure react-pdf is properly installed
- Check browser console for PDF.js worker errors
- Verify the PDF file is not corrupted

### API Connection Errors
- Confirm backend is running on http://localhost:8000
- Check CORS settings in backend
- Verify network requests in browser DevTools

### Build Errors
- Clear `.next` directory: `rm -rf .next`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run lint`

## License

Part of the Bank Statement Extraction capstone project.
