from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ExtractionLog(Base):
    __tablename__ = "extraction_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    filename = Column(String, nullable=False)

    extracted_owner = Column(String, default="")
    extracted_bank_name = Column(String, default="")
    extracted_account_number = Column(String, default="")

    final_owner = Column(String, default="")
    final_bank_name = Column(String, default="")
    final_account_number = Column(String, default="")

    owner_corrected = Column(Boolean, default=False)
    bank_name_corrected = Column(Boolean, default=False)
    account_number_corrected = Column(Boolean, default=False)


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
