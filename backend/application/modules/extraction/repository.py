from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from application.modules.extraction.entities import ExtractionLog


class ExtractionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_paginated(self, page: int, page_size: int) -> tuple[list[ExtractionLog], int]:
        total = self.session.query(func.count(ExtractionLog.id)).scalar() or 0
        offset = (page - 1) * page_size
        logs = (
            self.session.query(ExtractionLog)
            .order_by(ExtractionLog.timestamp.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return logs, total

    def get_by_id(self, log_id: int) -> ExtractionLog | None:
        return self.session.query(ExtractionLog).filter(ExtractionLog.id == log_id).first()

    def create(self, log_entry: ExtractionLog) -> ExtractionLog:
        self.session.add(log_entry)
        self.session.commit()
        self.session.refresh(log_entry)
        return log_entry

    def count_total(self) -> int:
        return self.session.query(func.count(ExtractionLog.id)).scalar() or 0

    def count_with_field_correction(self, field: str) -> int:
        filter_map = {
            "owner": ExtractionLog.owner_corrected,
            "bank_name": ExtractionLog.bank_name_corrected,
            "account_number": ExtractionLog.account_number_corrected,
        }
        return (
            self.session.query(func.count(ExtractionLog.id)).filter(filter_map[field]).scalar() or 0
        )

    def count_with_any_correction(self) -> int:
        return (
            self.session.query(func.count(ExtractionLog.id))
            .filter(
                (ExtractionLog.owner_corrected)
                | (ExtractionLog.bank_name_corrected)
                | (ExtractionLog.account_number_corrected)
            )
            .scalar()
            or 0
        )

    def count_this_week(self) -> int:
        week_ago = datetime.utcnow() - timedelta(days=7)
        return (
            self.session.query(func.count(ExtractionLog.id))
            .filter(ExtractionLog.timestamp >= week_ago)
            .scalar()
            or 0
        )
