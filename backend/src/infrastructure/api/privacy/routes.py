"""Privacy endpoints: consent management, data deletion, audit logs, and anonymized export."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.infrastructure.auth import AdminDep, UserDep
from src.infrastructure.database import get_db
from src.infrastructure.repository import (
    AuditLogRepository,
    DataConsentRepository,
    DataRetentionRepository,
)

router = APIRouter(prefix="/privacy", tags=["privacy"])

DbDep = Annotated[Session, Depends(get_db)]


# --- Consent Management (ARCO compliance) ---


class ConsentRequest(BaseModel):
    consent_type: str
    policy_version: str = "1.0"


class ConsentResponse(BaseModel):
    id: int
    consent_type: str
    granted: bool
    granted_at: str | None
    revoked_at: str | None
    policy_version: str

    model_config = {"from_attributes": True}


@router.get("/consents")
def get_my_consents(user: UserDep, db: DbDep) -> list[ConsentResponse]:
    repo = DataConsentRepository(db)
    consents = repo.get_active_consents(user.id)
    return [
        ConsentResponse(
            id=c.id,
            consent_type=c.consent_type,
            granted=c.granted,
            granted_at=str(c.granted_at) if c.granted_at else None,
            revoked_at=str(c.revoked_at) if c.revoked_at else None,
            policy_version=c.policy_version,
        )
        for c in consents
    ]


@router.post("/consents", status_code=201)
def grant_consent(body: ConsentRequest, user: UserDep, db: DbDep) -> ConsentResponse:
    repo = DataConsentRepository(db)
    consent = repo.grant(user.id, body.consent_type, body.policy_version)

    audit = AuditLogRepository(db)
    audit.create(
        action="consent_granted",
        resource_type="consent",
        resource_id=str(consent.id),
        user_id=user.id,
        details=f"type={body.consent_type}, version={body.policy_version}",
    )

    return ConsentResponse(
        id=consent.id,
        consent_type=consent.consent_type,
        granted=consent.granted,
        granted_at=str(consent.granted_at) if consent.granted_at else None,
        revoked_at=None,
        policy_version=consent.policy_version,
    )


@router.delete("/consents/{consent_type}")
def revoke_consent(consent_type: str, user: UserDep, db: DbDep):
    repo = DataConsentRepository(db)
    revoked = repo.revoke(user.id, consent_type)
    if not revoked:
        raise HTTPException(status_code=404, detail="Consentimiento activo no encontrado")

    audit = AuditLogRepository(db)
    audit.create(
        action="consent_revoked",
        resource_type="consent",
        user_id=user.id,
        details=f"type={consent_type}",
    )

    return {"detail": "Consentimiento revocado exitosamente"}


# --- Data Deletion (Right to Erasure / ARCO Cancellation) ---


class DeletionResponse(BaseModel):
    extraction_logs_deleted: int
    test_logs_deleted: int


@router.delete("/my-data")
def delete_my_data(user: UserDep, db: DbDep) -> DeletionResponse:
    """Delete all personal extraction data for the current user (ARCO Cancellation)."""
    retention = DataRetentionRepository(db)
    extractions = retention.delete_user_extraction_data(user.id)
    tests = retention.delete_user_test_data(user.id)

    audit = AuditLogRepository(db)
    audit.create(
        action="user_data_deleted",
        resource_type="user",
        resource_id=str(user.id),
        user_id=user.id,
        details=f"extraction_logs={extractions}, test_logs={tests}",
    )

    return DeletionResponse(extraction_logs_deleted=extractions, test_logs_deleted=tests)


@router.delete("/retention/expired", dependencies=[Depends(AdminDep)])
def purge_expired_data(db: DbDep, admin: AdminDep) -> dict:
    """Purge data older than the 5-year retention period (admin only)."""
    retention = DataRetentionRepository(db)
    deleted = retention.delete_expired_data()

    audit = AuditLogRepository(db)
    audit.create(
        action="retention_purge",
        resource_type="system",
        user_id=admin.id,
        details=f"records_deleted={deleted}",
    )

    return {"detail": f"Se eliminaron {deleted} registros expirados"}


# --- Audit Logs (admin only) ---


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    resource_type: str
    resource_id: str | None
    details: str | None
    ip_address: str | None
    timestamp: str | None

    model_config = {"from_attributes": True}


@router.get("/audit-logs")
def get_audit_logs(admin: AdminDep, db: DbDep) -> list[AuditLogResponse]:
    repo = AuditLogRepository(db)
    logs = repo.get_all()
    return [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            ip_address=log.ip_address,
            timestamp=str(log.timestamp) if log.timestamp else None,
        )
        for log in logs
    ]
