from pathlib import Path
from typing import List

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

from src.core.logger import get_logger

logger = get_logger(__name__)


class OCRProcessor:
    def __init__(self, language: str = "spa+eng"):
        self.language = language

    def has_extractable_text(self, pdf_path: Path, min_chars: int = 100) -> bool:
        import pdfplumber

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_chars = 0
                for page in pdf.pages[:3]:
                    text = page.extract_text()
                    if text:
                        total_chars += len(text.strip())

                return total_chars >= min_chars
        except Exception:
            return False

    def pdf_to_images(self, pdf_path: Path, dpi: int = 300) -> List[Image.Image]:
        try:
            images = convert_from_path(str(pdf_path), dpi=dpi, first_page=1, last_page=3)
            return images
        except Exception as e:
            logger.error("Error converting PDF to images: %s", e)
            return []

    def ocr_image(self, image: Image.Image) -> str:
        try:
            custom_config = r"--oem 3 --psm 1"
            text = pytesseract.image_to_string(image, lang=self.language, config=custom_config)
            return text
        except Exception as e:
            logger.error("Error performing OCR: %s", e)
            return ""

    def ocr_image_with_layout(self, image: Image.Image) -> str:
        try:
            data = pytesseract.image_to_data(
                image, lang=self.language, output_type=pytesseract.Output.DICT
            )

            n_boxes = len(data["text"])
            text_blocks = []

            current_block = []
            last_block_num = -1

            for i in range(n_boxes):
                block_num = data["block_num"][i]
                text = data["text"][i].strip()

                if text:
                    if block_num != last_block_num and current_block:
                        text_blocks.append(" ".join(current_block))
                        current_block = []

                    current_block.append(text)
                    last_block_num = block_num

            if current_block:
                text_blocks.append(" ".join(current_block))

            return "\n".join(text_blocks)
        except Exception as e:
            logger.error("Error performing OCR with layout: %s", e)
            return ""

    def process_pdf(self, pdf_path: Path, preserve_layout: bool = True) -> str:
        if self.has_extractable_text(pdf_path):
            import pdfplumber

            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:3]:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text

        images = self.pdf_to_images(pdf_path)
        if not images:
            return ""

        all_text = []
        for image in images:
            if preserve_layout:
                text = self.ocr_image_with_layout(image)
            else:
                text = self.ocr_image(image)

            if text:
                all_text.append(text)

        return "\n\n".join(all_text)

    def get_document_info(self, pdf_path: Path) -> dict:
        has_text = self.has_extractable_text(pdf_path)

        return {
            "has_extractable_text": has_text,
            "requires_ocr": not has_text,
            "recommended_method": "text_extraction" if has_text else "ocr",
        }
