from enum import verify
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_session, create_async_engine
from sqlalchemy import select
from sqlalchemy.util import deprecated

from app.core.database import DATABASE_URL, get_db
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.dependencies import get_current_user

#Login imports
from passlib.context import CryptContext
from app.core.security import verify_password, create_access_token




router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        email=user.email,
        password=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router .get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
            "id" : current_user.id,
            "email" : current_user.email
            }

@router.post("/login")
async def login(
    user: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    # Buscar usuario
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    db_user = result.scalar_one_or_none()

    # Validar existencia
    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    # Validar password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )
    access_token = create_access_token(
            data={"sub":db_user.email}
    )
    # devolver token al usuario
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
