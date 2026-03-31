from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Lógica de autenticación centralizada
from app.core.auth import (
    create_user_access_token,
    create_user_refresh_token,
    store_refresh_token,
    verify_refresh_token,
    decode_refresh_token,
)

from app.core.security import hash_password, verify_password

# Modelos y schemas
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

# Dependencias
from app.core.dependencies import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

# Esquema de seguridad OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login → devuelve access + refresh token y guarda el refresh en DB"""
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    access_token = create_user_access_token(db_user)
    refresh_token = create_user_refresh_token(db_user)

    # Guarda hash del refresh token (single session)
    await store_refresh_token(db, db_user.id, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crea nuevo usuario"""
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado"
        )

    new_user = User(
        email=user.email,
        password=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Obtiene datos del usuario actual"""
    return {
        "id": current_user.id,
        "email": current_user.email
    }


@router.post("/refresh")
async def refresh_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Refresh token → devuelve nuevo access token"""
    payload = decode_refresh_token(token)
    user_id = payload["user_id"]

    if not await verify_refresh_token(db, user_id, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido o revocado"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no identificado"
        )

    new_access_token = create_user_access_token(db_user)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
