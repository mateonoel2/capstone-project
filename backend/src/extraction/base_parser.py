import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.extraction.schemas import BankAccount

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    @abstractmethod
    def parse_file(self, file_path: Path) -> BankAccount:
        pass

    def parse_multiple(self, file_paths: List[Path]) -> List[BankAccount]:
        results = []
        for file_path in file_paths:
            try:
                result = self.parse_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error("Error parsing %s: %s", file_path, e)
        return results

