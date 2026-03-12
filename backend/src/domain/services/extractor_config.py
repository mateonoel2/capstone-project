from src.domain.entities import ExtractorConfigData
from src.infrastructure.models import ExtractorConfig, ExtractorConfigVersion
from src.infrastructure.repository import ExtractorConfigRepository


class ExtractorConfigService:
    def __init__(self, repository: ExtractorConfigRepository):
        self.repository = repository

    def get_all(self) -> list[ExtractorConfig]:
        return self.repository.get_all()

    def get_by_id(self, config_id: int) -> ExtractorConfig | None:
        return self.repository.get_by_id(config_id)

    def get_default(self) -> ExtractorConfig | None:
        return self.repository.get_default()

    def create(self, data: ExtractorConfigData) -> ExtractorConfig:
        if data.is_default:
            self._clear_default()
        return self.repository.create(data)

    def update(self, config_id: int, data: ExtractorConfigData) -> ExtractorConfig | None:
        if data.is_default:
            self._clear_default(exclude_id=config_id)
        return self.repository.update(config_id, data)

    def delete(self, config_id: int) -> bool:
        return self.repository.delete(config_id)

    def get_versions(self, config_id: int) -> list[ExtractorConfigVersion]:
        return self.repository.get_versions(config_id)

    def _clear_default(self, exclude_id: int | None = None) -> None:
        for config in self.repository.get_all():
            if config.is_default and config.id != exclude_id:
                config.is_default = False
