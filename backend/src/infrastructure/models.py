from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
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
