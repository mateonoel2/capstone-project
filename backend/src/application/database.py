from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.application.modules.extraction.models import Base


def get_database_path() -> Path:
    db_dir = Path(__file__).parent.parent.parent / "data"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "extractions.db"


database_url = f"sqlite:///{get_database_path()}"
engine = create_engine(database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
