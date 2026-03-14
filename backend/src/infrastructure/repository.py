from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domain.entities import ApiCallResult, ExtractorConfigData, ExtractorConfigVersionData
from src.infrastructure.models import (
    ApiCallLog,
    ExtractionLog,
    ExtractorConfig,
    ExtractorConfigVersion,
    TestExtractionLog,
)


class ExtractionRepository:
    def __init__(self, session: Session):
        self.session = session

    def _base_query(self, extractor_config_id: int | None = None):
        q = self.session.query(ExtractionLog)
        if extractor_config_id is not None:
            q = q.filter(ExtractionLog.extractor_config_id == extractor_config_id)
        return q

    def get_all_paginated(
        self, page: int, page_size: int, extractor_config_id: int | None = None
    ) -> tuple[list[ExtractionLog], int]:
        q = self._base_query(extractor_config_id)
        total = q.count()
        offset = (page - 1) * page_size
        logs = q.order_by(ExtractionLog.timestamp.desc()).offset(offset).limit(page_size).all()
        return logs, total

    def get_by_id(self, log_id: int) -> ExtractionLog | None:
        return self.session.query(ExtractionLog).filter(ExtractionLog.id == log_id).first()

    def create(self, log_entry: ExtractionLog) -> ExtractionLog:
        self.session.add(log_entry)
        self.session.commit()
        self.session.refresh(log_entry)
        return log_entry

    def count_total(self, extractor_config_id: int | None = None) -> int:
        q = self.session.query(func.count(ExtractionLog.id))
        if extractor_config_id is not None:
            q = q.filter(ExtractionLog.extractor_config_id == extractor_config_id)
        return q.scalar() or 0

    def count_corrections(
        self, extractor_config_id: int | None = None
    ) -> tuple[int, dict[str, int], int]:
        """Returns (any_corrected_count, {field: correction_count}, total)."""
        q = self._base_query(extractor_config_id)
        total = q.count()
        field_corrections: dict[str, int] = {}
        any_corrected = 0

        for log in q.yield_per(500):
            corrected = log.corrected_fields
            if any(corrected.values()):
                any_corrected += 1
            for field_name, was_corrected in corrected.items():
                if field_name not in field_corrections:
                    field_corrections[field_name] = 0
                if was_corrected:
                    field_corrections[field_name] += 1

        return any_corrected, field_corrections, total

    def count_this_week(self, extractor_config_id: int | None = None) -> int:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        q = self.session.query(func.count(ExtractionLog.id)).filter(
            ExtractionLog.timestamp >= week_ago
        )
        if extractor_config_id is not None:
            q = q.filter(ExtractionLog.extractor_config_id == extractor_config_id)
        return q.scalar() or 0


class ExtractorConfigRepository:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_entity(config: ExtractorConfig) -> ExtractorConfigData:
        return ExtractorConfigData(
            id=config.id,
            name=config.name,
            description=config.description or "",
            prompt=config.prompt,
            model=config.model,
            output_schema=config.output_schema,
            is_default=config.is_default,
            status=config.status,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )

    @staticmethod
    def _version_to_entity(version: ExtractorConfigVersion) -> ExtractorConfigVersionData:
        return ExtractorConfigVersionData(
            id=version.id,
            extractor_config_id=version.extractor_config_id,
            version_number=version.version_number,
            prompt=version.prompt,
            model=version.model,
            output_schema=version.output_schema,
            is_active=version.is_active,
            created_at=version.created_at,
        )

    def get_all(self, status: str | None = None) -> list[ExtractorConfigData]:
        q = self.session.query(ExtractorConfig)
        if status is not None:
            q = q.filter(ExtractorConfig.status == status)
        configs = q.order_by(ExtractorConfig.id).all()
        return [self._to_entity(c) for c in configs]

    def _get_orm_by_id(self, config_id: int) -> ExtractorConfig | None:
        return self.session.query(ExtractorConfig).filter(ExtractorConfig.id == config_id).first()

    def get_by_id(self, config_id: int) -> ExtractorConfigData | None:
        config = self._get_orm_by_id(config_id)
        return self._to_entity(config) if config else None

    def get_default(self) -> ExtractorConfigData | None:
        config = (
            self.session.query(ExtractorConfig).filter(ExtractorConfig.is_default.is_(True)).first()
        )
        return self._to_entity(config) if config else None

    def create(self, data: ExtractorConfigData) -> ExtractorConfigData:
        config = ExtractorConfig(
            name=data.name,
            description=data.description,
            prompt=data.prompt,
            model=data.model,
            output_schema=data.output_schema,
            is_default=data.is_default,
            status=data.status,
        )
        self.session.add(config)
        self.session.commit()
        self.session.refresh(config)
        return self._to_entity(config)

    def update(self, config_id: int, data: ExtractorConfigData) -> ExtractorConfigData | None:
        config = self._get_orm_by_id(config_id)
        if not config:
            return None

        # Create version snapshot before updating
        max_version = (
            self.session.query(func.max(ExtractorConfigVersion.version_number))
            .filter(ExtractorConfigVersion.extractor_config_id == config_id)
            .scalar()
        ) or 0
        version = ExtractorConfigVersion(
            extractor_config_id=config_id,
            version_number=max_version + 1,
            prompt=config.prompt,
            model=config.model,
            output_schema=config.output_schema,
        )
        self.session.add(version)

        config.name = data.name
        config.description = data.description
        config.prompt = data.prompt
        config.model = data.model
        config.output_schema = data.output_schema
        config.is_default = data.is_default
        config.status = data.status

        self.session.commit()
        self.session.refresh(config)

        self._deactivate_incompatible_versions(config_id, data.output_schema)

        return self._to_entity(config)

    def delete(self, config_id: int) -> bool:
        config = self._get_orm_by_id(config_id)
        if not config or config.is_default:
            return False
        # Nullify FK references in logs before deleting
        self.session.query(ExtractionLog).filter(
            ExtractionLog.extractor_config_id == config_id
        ).update(
            {
                ExtractionLog.extractor_config_id: None,
                ExtractionLog.extractor_config_version_id: None,
            }
        )
        self.session.query(ApiCallLog).filter(ApiCallLog.extractor_config_id == config_id).update(
            {
                ApiCallLog.extractor_config_id: None,
                ApiCallLog.extractor_config_version_id: None,
            }
        )
        self.session.query(TestExtractionLog).filter(
            TestExtractionLog.extractor_config_id == config_id
        ).update({TestExtractionLog.extractor_config_id: None})
        self.session.query(ExtractorConfigVersion).filter(
            ExtractorConfigVersion.extractor_config_id == config_id
        ).delete()
        self.session.delete(config)
        self.session.commit()
        return True

    def get_versions(self, config_id: int) -> list[ExtractorConfigVersionData]:
        versions = (
            self.session.query(ExtractorConfigVersion)
            .filter(ExtractorConfigVersion.extractor_config_id == config_id)
            .order_by(ExtractorConfigVersion.version_number.desc())
            .all()
        )
        return [self._version_to_entity(v) for v in versions]

    def get_active_versions(self, config_id: int) -> list[ExtractorConfigVersionData]:
        versions = self._get_active_versions_orm(config_id)
        return [self._version_to_entity(v) for v in versions]

    def _get_active_versions_orm(self, config_id: int) -> list[ExtractorConfigVersion]:
        return (
            self.session.query(ExtractorConfigVersion)
            .filter(
                ExtractorConfigVersion.extractor_config_id == config_id,
                ExtractorConfigVersion.is_active.is_(True),
            )
            .all()
        )

    def set_version_active(
        self, version_id: int, active: bool
    ) -> ExtractorConfigVersionData | None:
        version = (
            self.session.query(ExtractorConfigVersion)
            .filter(ExtractorConfigVersion.id == version_id)
            .first()
        )
        if not version:
            return None
        version.is_active = active
        self.session.commit()
        self.session.refresh(version)
        return self._version_to_entity(version)

    def _deactivate_incompatible_versions(self, config_id: int, schema: dict) -> None:
        current_keys = sorted(schema.get("properties", {}).keys())
        active_versions = self._get_active_versions_orm(config_id)
        for version in active_versions:
            version_keys = sorted(version.output_schema.get("properties", {}).keys())
            if version_keys != current_keys:
                version.is_active = False
        self.session.commit()


class ApiCallRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        call_result: ApiCallResult,
        filename: str | None = None,
        extractor_config_id: int | None = None,
        extractor_config_version_id: int | None = None,
    ) -> ApiCallLog:
        log = ApiCallLog(
            model=call_result.model,
            success=call_result.success,
            error_type=call_result.error_type,
            error_message=call_result.error_message,
            response_time_ms=call_result.response_time_ms,
            filename=filename,
            extractor_config_id=extractor_config_id,
            extractor_config_version_id=extractor_config_version_id,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def count_total(self, extractor_config_id: int | None = None) -> int:
        q = self.session.query(func.count(ApiCallLog.id))
        if extractor_config_id is not None:
            q = q.filter(ApiCallLog.extractor_config_id == extractor_config_id)
        return q.scalar() or 0

    def count_failures(self, extractor_config_id: int | None = None) -> int:
        q = self.session.query(func.count(ApiCallLog.id)).filter(ApiCallLog.success.is_(False))
        if extractor_config_id is not None:
            q = q.filter(ApiCallLog.extractor_config_id == extractor_config_id)
        return q.scalar() or 0

    def count_by_error_type(self, extractor_config_id: int | None = None) -> list[tuple[str, int]]:
        q = self.session.query(ApiCallLog.error_type, func.count(ApiCallLog.id)).filter(
            ApiCallLog.error_type.isnot(None)
        )
        if extractor_config_id is not None:
            q = q.filter(ApiCallLog.extractor_config_id == extractor_config_id)
        return q.group_by(ApiCallLog.error_type).all()

    def avg_response_time_ms(self, extractor_config_id: int | None = None) -> float:
        q = self.session.query(func.avg(ApiCallLog.response_time_ms))
        if extractor_config_id is not None:
            q = q.filter(ApiCallLog.extractor_config_id == extractor_config_id)
        result = q.scalar()
        return round(result, 1) if result else 0.0

    def count_this_week(self, extractor_config_id: int | None = None) -> int:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        q = self.session.query(func.count(ApiCallLog.id)).filter(ApiCallLog.timestamp >= week_ago)
        if extractor_config_id is not None:
            q = q.filter(ApiCallLog.extractor_config_id == extractor_config_id)
        return q.scalar() or 0


class TestExtractionLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        filename: str,
        s3_key: str,
        prompt_snapshot: str,
        model: str,
        output_schema_snapshot: dict,
        extracted_fields: dict | None,
        success: bool,
        response_time_ms: float,
        error_message: str | None = None,
        extractor_config_id: int | None = None,
    ) -> TestExtractionLog:
        log = TestExtractionLog(
            filename=filename,
            s3_key=s3_key,
            extractor_config_id=extractor_config_id,
            prompt_snapshot=prompt_snapshot,
            model=model,
            output_schema_snapshot=output_schema_snapshot,
            extracted_fields=extracted_fields,
            success=success,
            error_message=error_message,
            response_time_ms=response_time_ms,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def get_by_config_id(self, config_id: int) -> list[TestExtractionLog]:
        return (
            self.session.query(TestExtractionLog)
            .filter(TestExtractionLog.extractor_config_id == config_id)
            .order_by(TestExtractionLog.timestamp.desc())
            .all()
        )
