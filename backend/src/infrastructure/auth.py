import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
import requests
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.domain.entities import UserData
from src.infrastructure.database import get_db
from src.infrastructure.repository import UserRepository

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


def create_access_token(user: UserData) -> str:
    payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def validate_github_token(github_access_token: str) -> dict:
    try:
        response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {github_access_token}"},
            timeout=10,
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=502, detail="No se pudo conectar con GitHub para validar el token"
        )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Token de GitHub inválido")
    return response.json()


def get_current_user(
    authorization: Annotated[str, Header()],
    db: Annotated[Session, Depends(get_db)],
) -> UserData:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")

    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    return user


def get_admin_user(user: UserData = Depends(get_current_user)) -> UserData:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
    return user


UserDep = Annotated[UserData, Depends(get_current_user)]
AdminDep = Annotated[UserData, Depends(get_admin_user)]
