import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from src.extraction.claude_ocr_parser import ClaudeOCRParser

router = APIRouter(prefix="/extraction", tags=["extraction"])


class ExtractionResponse(BaseModel):
    owner: str
    bank_name: str
    account_number: str


@router.post("/pdf", response_model=ExtractionResponse)
async def extract_from_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = Path(tmp_file.name)

        parser = ClaudeOCRParser()
        result = parser.parse_file(tmp_file_path)

        tmp_file_path.unlink()

        return ExtractionResponse(
            owner="" if result.owner == "Unknown" else result.owner,
            bank_name="" if result.bank_name == "Unknown" else result.bank_name,
            account_number=""
            if result.account_number == "000000000000000000"
            else result.account_number,
        )

    except Exception as e:
        if tmp_file_path.exists():
            tmp_file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
