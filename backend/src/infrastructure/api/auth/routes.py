import uuid
from dataclasses import replace
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.domain.constants import DEFAULT_RECEIPT_EXTRACTOR
from src.domain.services.extractor_config import ExtractorConfigService
from src.domain.services.quota import QuotaService
from src.infrastructure.auth import UserDep, create_access_token, validate_github_token
from src.infrastructure.database import get_db
from src.infrastructure.repository import (
    AiUsageLogRepository,
    ApiCallRepository,
    ExtractorConfigRepository,
    UserRepository,
)

router = APIRouter(prefix="/auth", tags=["auth"])

DbDep = Annotated[Session, Depends(get_db)]


def _create_default_extractor(db: Session, user_id: uuid.UUID) -> None:
    """Crea el extractor default de boletas para un usuario nuevo."""
    repo = ExtractorConfigRepository(db)
    existing = repo.get_all(user_id=user_id)
    if any(c.name == DEFAULT_RECEIPT_EXTRACTOR.name for c in existing):
        return
    service = ExtractorConfigService(repo)
    service.create(replace(DEFAULT_RECEIPT_EXTRACTOR), user_id=user_id)


class LoginRequest(BaseModel):
    github_access_token: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: uuid.UUID
    github_username: str
    email: str | None
    avatar_url: str | None
    role: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: DbDep):
    github_profile = validate_github_token(request.github_access_token)

    github_id = github_profile["id"]
    github_username = github_profile["login"]
    email = github_profile.get("email")
    avatar_url = github_profile.get("avatar_url")

    repo = UserRepository(db)

    # Try by github_id first (returning user), then by username (first login / guest)
    user = repo.get_by_github_id(github_id)
    if not user:
        user = repo.get_by_github_username(github_username)
        if not user:
            # Auto-register as guest
            user = repo.create(github_username=github_username, role="guest")
            _create_default_extractor(db, user.id)
        # First login — fill in github_id and profile info
        repo.update_login_info(user.id, github_id, email, avatar_url)
        user = repo.get_by_id(user.id)
    else:
        # Update last_login and profile info
        repo.update_login_info(user.id, github_id, email, avatar_url)
        user = repo.get_by_id(user.id)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    token = create_access_token(user)

    return LoginResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            github_username=user.github_username,
            email=user.email,
            avatar_url=user.avatar_url,
            role=user.role,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: UserDep):
    return UserResponse(
        id=user.id,
        github_username=user.github_username,
        email=user.email,
        avatar_url=user.avatar_url,
        role=user.role,
    )


@router.get("/usage")
async def get_usage(user: UserDep, db: DbDep):
    quota = QuotaService(
        api_call_repo=ApiCallRepository(db),
        extractor_repo=ExtractorConfigRepository(db),
        ai_usage_repo=AiUsageLogRepository(db),
    )
    return quota.get_usage(user)
