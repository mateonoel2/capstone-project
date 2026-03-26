import uuid
from typing import Protocol

from src.domain.entities import ExtractorConfigData, ExtractorConfigVersionData


class ExtractorConfigRepo(Protocol):
    def get_all(
        self, status: str | None = None, user_id: uuid.UUID | None = None
    ) -> list[ExtractorConfigData]: ...
    def get_by_id(self, config_id: uuid.UUID) -> ExtractorConfigData | None: ...
    def get_default(self) -> ExtractorConfigData | None: ...
    def create(
        self, data: ExtractorConfigData, user_id: uuid.UUID | None = None
    ) -> ExtractorConfigData: ...
    def update(
        self, config_id: uuid.UUID, data: ExtractorConfigData
    ) -> ExtractorConfigData | None: ...
    def delete(self, config_id: uuid.UUID) -> bool: ...
    def get_versions(self, config_id: uuid.UUID) -> list[ExtractorConfigVersionData]: ...


class ExtractorConfigService:
    def __init__(self, repository: ExtractorConfigRepo):
        self.repository = repository

    def get_all(
        self, status: str | None = None, user_id: uuid.UUID | None = None
    ) -> list[ExtractorConfigData]:
        return self.repository.get_all(status=status, user_id=user_id)

    def get_by_id(self, config_id: uuid.UUID) -> ExtractorConfigData | None:
        return self.repository.get_by_id(config_id)

    def get_default(self) -> ExtractorConfigData | None:
        return self.repository.get_default()

    def create(
        self, data: ExtractorConfigData, user_id: uuid.UUID | None = None
    ) -> ExtractorConfigData:
        if data.status == "draft":
            data.is_default = False
        if data.is_default:
            self._clear_default()
        return self.repository.create(data, user_id=user_id)

    def update(self, config_id: uuid.UUID, data: ExtractorConfigData) -> ExtractorConfigData | None:
        if data.status == "draft":
            data.is_default = False
        if data.is_default:
            self._clear_default(exclude_id=config_id)
        return self.repository.update(config_id, data)

    def delete(self, config_id: uuid.UUID) -> bool:
        return self.repository.delete(config_id)

    def get_versions(self, config_id: uuid.UUID) -> list[ExtractorConfigVersionData]:
        return self.repository.get_versions(config_id)

    def _clear_default(self, exclude_id: uuid.UUID | None = None) -> None:
        for config in self.repository.get_all():
            if config.is_default and config.id != exclude_id:
                config.is_default = False
                self.repository.update(config.id, config)
