from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.core.logger import get_logger
from src.domain.schemas import BankAccount

logger = get_logger(__name__)


class BaseExtractor(ABC):
    @abstractmethod
    def extract_file(self, file_path: Path) -> BankAccount:
        pass

    def extract_multiple(self, file_paths: List[Path]) -> List[BankAccount]:
        results = []
        for file_path in file_paths:
            try:
                result = self.extract_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error("Error extracting %s: %s", file_path, e)
        return results
