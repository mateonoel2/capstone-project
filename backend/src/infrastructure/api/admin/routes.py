from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.infrastructure.auth import AdminDep
from src.infrastructure.database import get_db
from src.infrastructure.repository import UserRepository

router = APIRouter(prefix="/admin", tags=["admin"])

DbDep = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    github_username: str
    role: str = "user"


class UpdateUserRequest(BaseModel):
    role: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    github_id: int | None
    github_username: str
    email: str | None
    avatar_url: str | None
    role: str
    is_active: bool


@router.get("/users", response_model=list[UserResponse])
async def list_users(admin: AdminDep, db: DbDep):
    repo = UserRepository(db)
    users = repo.get_all()
    return [
        UserResponse(
            id=u.id,
            github_id=u.github_id,
            github_username=u.github_username,
            email=u.email,
            avatar_url=u.avatar_url,
            role=u.role,
            is_active=u.is_active,
        )
        for u in users
    ]


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(request: CreateUserRequest, admin: AdminDep, db: DbDep):
    repo = UserRepository(db)
    existing = repo.get_by_github_username(request.github_username)
    if existing:
        raise HTTPException(status_code=409, detail="El usuario ya existe")
    if request.role not in ("user", "admin", "guest"):
        raise HTTPException(status_code=400, detail="Rol inválido")
    user = repo.create(request.github_username, request.role)
    return UserResponse(
        id=user.id,
        github_id=user.github_id,
        github_username=user.github_username,
        email=user.email,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
    )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, request: UpdateUserRequest, admin: AdminDep, db: DbDep):
    repo = UserRepository(db)
    fields = {}
    if request.role is not None:
        if request.role not in ("user", "admin", "guest"):
            raise HTTPException(status_code=400, detail="Rol inválido")
        fields["role"] = request.role
    if request.is_active is not None:
        fields["is_active"] = request.is_active
    if not fields:
        raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
    user = repo.update(user_id, **fields)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserResponse(
        id=user.id,
        github_id=user.github_id,
        github_username=user.github_username,
        email=user.email,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
    )


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, admin: AdminDep, db: DbDep):
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    repo = UserRepository(db)
    success = repo.delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado exitosamente"}
