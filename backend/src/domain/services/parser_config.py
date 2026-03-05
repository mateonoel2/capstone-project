from src.domain.entities import ParserConfigData
from src.infrastructure.models import ParserConfig, ParserConfigVersion
from src.infrastructure.repository import ParserConfigRepository


class ParserConfigService:
    def __init__(self, repository: ParserConfigRepository):
        self.repository = repository

    def get_all(self) -> list[ParserConfig]:
        return self.repository.get_all()

    def get_by_id(self, config_id: int) -> ParserConfig | None:
        return self.repository.get_by_id(config_id)

    def get_default(self) -> ParserConfig | None:
        return self.repository.get_default()

    def create(self, data: ParserConfigData) -> ParserConfig:
        if data.is_default:
            self._clear_default()
        return self.repository.create(data)

    def update(self, config_id: int, data: ParserConfigData) -> ParserConfig | None:
        if data.is_default:
            self._clear_default(exclude_id=config_id)
        return self.repository.update(config_id, data)

    def delete(self, config_id: int) -> bool:
        return self.repository.delete(config_id)

    def get_versions(self, config_id: int) -> list[ParserConfigVersion]:
        return self.repository.get_versions(config_id)

    def _clear_default(self, exclude_id: int | None = None) -> None:
        for config in self.repository.get_all():
            if config.is_default and config.id != exclude_id:
                config.is_default = False
