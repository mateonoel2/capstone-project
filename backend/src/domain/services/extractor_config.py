from typing import Protocol

from src.domain.entities import ExtractorConfigData, ExtractorConfigVersionData


class ExtractorConfigRepo(Protocol):
    def get_all(self) -> list[ExtractorConfigData]: ...
    def get_by_id(self, config_id: int) -> ExtractorConfigData | None: ...
    def get_default(self) -> ExtractorConfigData | None: ...
    def create(self, data: ExtractorConfigData) -> ExtractorConfigData: ...
    def update(self, config_id: int, data: ExtractorConfigData) -> ExtractorConfigData | None: ...
    def delete(self, config_id: int) -> bool: ...
    def get_versions(self, config_id: int) -> list[ExtractorConfigVersionData]: ...


class ExtractorConfigService:
    def __init__(self, repository: ExtractorConfigRepo):
        self.repository = repository

    def get_all(self) -> list[ExtractorConfigData]:
        return self.repository.get_all()

    def get_by_id(self, config_id: int) -> ExtractorConfigData | None:
        return self.repository.get_by_id(config_id)

    def get_default(self) -> ExtractorConfigData | None:
        return self.repository.get_default()

    def create(self, data: ExtractorConfigData) -> ExtractorConfigData:
        if data.is_default:
            self._clear_default()
        return self.repository.create(data)

    def update(self, config_id: int, data: ExtractorConfigData) -> ExtractorConfigData | None:
        if data.is_default:
            self._clear_default(exclude_id=config_id)
        return self.repository.update(config_id, data)

    def delete(self, config_id: int) -> bool:
        return self.repository.delete(config_id)

    def get_versions(self, config_id: int) -> list[ExtractorConfigVersionData]:
        return self.repository.get_versions(config_id)

    def _clear_default(self, exclude_id: int | None = None) -> None:
        for config in self.repository.get_all():
            if config.is_default and config.id != exclude_id:
                config.is_default = False
                self.repository.update(config.id, config)
