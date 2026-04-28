from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User


async def register_user(
    db: AsyncSession,
    *,
    first_name: str,
    last_name: str,
    login: str,
    password: str,
    is_manager: bool,
) -> User:
    existing = await db.scalar(select(User).where(User.login == login))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login already exists")

    user = User(
        first_name=first_name,
        last_name=last_name,
        login=login,
        password_hash=hash_password(password),
        is_manager=is_manager,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, *, login: str, password: str) -> tuple[str, str]:
    user = await db.scalar(select(User).where(User.login == login))
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    subject = {"sub": str(user.id)}
    access = create_access_token(subject)
    refresh = create_refresh_token(subject)
    return access, refresh


async def change_password(
    db: AsyncSession,
    *,
    user: User,
    old_password: str,
    new_password: str,
) -> None:
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")

    user.password_hash = hash_password(new_password)
    db.add(user)
    await db.commit()


async def refresh_access_token(*, refresh_token: str) -> str:
    from app.core.security import decode_token

    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    return create_access_token({"sub": str(sub)})

