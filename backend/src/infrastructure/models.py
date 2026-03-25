from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

from src.infrastructure.encryption import EncryptedJSON

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True, nullable=True, index=True)
    github_username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), nullable=False, default="guest")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime, nullable=True)


class ApiToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(200), nullable=False)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    is_revoked = Column(Boolean, default=False, nullable=False)


class ExtractorConfig(Base):
    __tablename__ = "extractor_configs"
    __table_args__ = (UniqueConstraint("name", "user_id", name="uq_extractor_configs_name_user"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    prompt = Column(Text, nullable=False)
    model = Column(String(100), nullable=False, default="claude-haiku-4-5-20251001")
    output_schema = Column(JSON, nullable=False)
    is_default = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), nullable=False, default="active")
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

    extracted_fields = Column(EncryptedJSON, default=dict)
    final_fields = Column(EncryptedJSON, default=dict)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    extractor_config_id = Column(Integer, ForeignKey("extractor_configs.id"), nullable=True)
    extractor_config_version_id = Column(
        Integer, ForeignKey("extractor_config_versions.id"), nullable=True
    )

    @property
    def corrected_fields(self) -> dict[str, bool]:
        extracted = self.extracted_fields or {}
        final = self.final_fields or {}
        all_keys = set(extracted.keys()) | set(final.keys())
        return {k: str(extracted.get(k, "")) != str(final.get(k, "")) for k in all_keys}

    @property
    def has_any_correction(self) -> bool:
        return any(self.corrected_fields.values())


class TestExtractionLog(Base):
    __tablename__ = "test_extraction_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    extractor_config_id = Column(
        Integer, ForeignKey("extractor_configs.id", ondelete="SET NULL"), nullable=True
    )
    prompt_snapshot = Column(Text, nullable=False)
    model = Column(String(100), nullable=False)
    output_schema_snapshot = Column(JSON, nullable=False)
    extracted_fields = Column(JSON, nullable=True)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    response_time_ms = Column(Float, nullable=False)


class ApiCallLog(Base):
    __tablename__ = "api_call_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
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


class AiUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    """Audit trail for sensitive data access and modifications."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class DataConsent(Base):
    """Tracks user consent for data processing per LFPDPPP/ARCO requirements."""

    __tablename__ = "data_consents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    consent_type = Column(String(100), nullable=False)
    granted = Column(Boolean, nullable=False, default=True)
    granted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    revoked_at = Column(DateTime, nullable=True)
    policy_version = Column(String(20), nullable=False, default="1.0")
