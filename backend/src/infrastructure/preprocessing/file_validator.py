from pathlib import Path
from typing import Dict, List

import pypdf


class FileValidator:
    VALID_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}

    @staticmethod
    def is_valid_extension(file_path: Path) -> bool:
        return file_path.suffix.lower() in FileValidator.VALID_EXTENSIONS

    @staticmethod
    def is_pdf_readable(file_path: Path) -> bool:
        if file_path.suffix.lower() != '.pdf':
            return False

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                if len(pdf_reader.pages) == 0:
                    return False
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()
                return True
        except Exception:
            return False

    @staticmethod
    def get_file_size(file_path: Path) -> int:
        return file_path.stat().st_size

    @staticmethod
    def is_file_size_valid(file_path: Path, min_size: int = 1024, max_size: int = 50*1024*1024) -> bool:
        size = FileValidator.get_file_size(file_path)
        return min_size <= size <= max_size

    @classmethod
    def validate_file(cls, file_path: Path) -> Dict[str, object]:
        result = {
            'file_path': str(file_path),
            'exists': file_path.exists(),
            'valid_extension': False,
            'valid_size': False,
            'readable': False,
            'errors': []
        }

        if not result['exists']:
            result['errors'].append('File does not exist')
            return result

        result['valid_extension'] = cls.is_valid_extension(file_path)
        if not result['valid_extension']:
            result['errors'].append(f'Invalid extension: {file_path.suffix}')

        result['valid_size'] = cls.is_file_size_valid(file_path)
        if not result['valid_size']:
            size = cls.get_file_size(file_path)
            result['errors'].append(f'Invalid size: {size} bytes')

        if file_path.suffix.lower() == '.pdf':
            result['readable'] = cls.is_pdf_readable(file_path)
            if not result['readable']:
                result['errors'].append('PDF is not readable or corrupted')
        else:
            result['readable'] = True

        return result

    @classmethod
    def validate_directory(cls, directory: Path) -> List[Dict[str, object]]:
        results = []
        for file_path in directory.glob('*'):
            if file_path.is_file():
                validation = cls.validate_file(file_path)
                results.append(validation)
        return results
