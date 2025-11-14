import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.preprocessing.file_validator import FileValidator


class TestFileValidator:
    def test_valid_extension(self):
        assert FileValidator.is_valid_extension(Path("test.pdf"))
        assert FileValidator.is_valid_extension(Path("test.jpg"))
        assert not FileValidator.is_valid_extension(Path("test.txt"))

    def test_valid_extensions_list(self):
        assert ".pdf" in FileValidator.VALID_EXTENSIONS
        assert ".jpg" in FileValidator.VALID_EXTENSIONS
        assert ".txt" not in FileValidator.VALID_EXTENSIONS
