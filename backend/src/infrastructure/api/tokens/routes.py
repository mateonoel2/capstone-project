import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.infrastructure.auth import UserDep, generate_api_token, hash_token
from src.infrastructure.database import get_db
from src.infrastructure.repository import ApiTokenRepository

router = APIRouter(prefix="/tokens", tags=["tokens"])


class CreateTokenRequest(BaseModel):
    name: str
    expires_at: datetime | None = None


class TokenResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime | None
    expires_at: datetime | None
    last_used_at: datetime | None
    is_revoked: bool


class CreateTokenResponse(BaseModel):
    token: str
    id: uuid.UUID
    name: str
    expires_at: datetime | None


@router.post("", response_model=CreateTokenResponse)
def create_token(
    body: CreateTokenRequest,
    user: UserDep,
    db: Session = Depends(get_db),
):
    if user.role == "guest":
        raise HTTPException(
            status_code=403,
            detail="Los invitados no pueden crear tokens API",
        )
    plaintext = generate_api_token()
    token_hash = hash_token(plaintext)
    repo = ApiTokenRepository(db)
    api_token = repo.create(
        user_id=user.id,
        name=body.name,
        token_hash=token_hash,
        expires_at=body.expires_at,
    )
    return CreateTokenResponse(
        token=plaintext,
        id=api_token.id,
        name=api_token.name,
        expires_at=api_token.expires_at,
    )


@router.get("", response_model=list[TokenResponse])
def list_tokens(
    user: UserDep,
    db: Session = Depends(get_db),
):
    repo = ApiTokenRepository(db)
    tokens = repo.get_by_user(user.id)
    return [
        TokenResponse(
            id=t.id,
            name=t.name,
            created_at=t.created_at,
            expires_at=t.expires_at,
            last_used_at=t.last_used_at,
            is_revoked=t.is_revoked,
        )
        for t in tokens
    ]


@router.delete("/{token_id}")
def revoke_token(
    token_id: uuid.UUID,
    user: UserDep,
    db: Session = Depends(get_db),
):
    repo = ApiTokenRepository(db)
    revoked = repo.revoke(token_id, user.id)
    if not revoked:
        raise HTTPException(status_code=404, detail="Token no encontrado")
    return {"detail": "Token revocado"}
