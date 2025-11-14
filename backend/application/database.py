from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.modules.extraction.entities import Base


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

