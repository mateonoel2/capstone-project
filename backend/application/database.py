from datetime import datetime
from pathlib import Path

from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class ExtractionLog(Base):
    __tablename__ = "extraction_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
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


def get_database_path() -> Path:
    db_dir = Path(__file__).parent.parent / "data"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "extractions.db"


def get_engine():
    database_url = f"sqlite:///{get_database_path()}"
    return create_engine(database_url, connect_args={"check_same_thread": False})


def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    return engine


def get_session():
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

