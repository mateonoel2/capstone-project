from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class ExtractorConfig(Base):
    __tablename__ = "extractor_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    prompt = Column(Text, nullable=False)
    model = Column(String(100), nullable=False, default="claude-haiku-4-5-20251001")
    output_schema = Column(JSON, nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ExtractorConfigVersion(Base):
    __tablename__ = "extractor_config_versions"

    id = Column(Integer, primary_key=True, index=True)
    extractor_config_id = Column(Integer, ForeignKey("extractor_configs.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)
    model = Column(String(100), nullable=False)
    output_schema = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ExtractionLog(Base):
    __tablename__ = "extraction_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    filename = Column(String, nullable=False)

    extracted_fields = Column(JSON, default=dict)
    final_fields = Column(JSON, default=dict)

    extractor_config_id = Column(Integer, ForeignKey("extractor_configs.id"), nullable=True)
    extractor_config_version_id = Column(
        Integer, ForeignKey("extractor_config_versions.id"), nullable=True
    )

    @hybrid_property
    def corrected_fields(self) -> dict[str, bool]:
        extracted = self.extracted_fields or {}
        final = self.final_fields or {}
        all_keys = set(extracted.keys()) | set(final.keys())
        return {k: str(extracted.get(k, "")) != str(final.get(k, "")) for k in all_keys}

    @hybrid_property
    def has_any_correction(self) -> bool:
        return any(self.corrected_fields.values())


class ApiCallLog(Base):
    __tablename__ = "api_call_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    model = Column(String, nullable=False)
    success = Column(Boolean, nullable=False)
    error_type = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    response_time_ms = Column(Float, nullable=False)
    filename = Column(String, nullable=True)
    extractor_config_id = Column(Integer, ForeignKey("extractor_configs.id"), nullable=True)
    extractor_config_version_id = Column(
        Integer, ForeignKey("extractor_config_versions.id"), nullable=True
    )
