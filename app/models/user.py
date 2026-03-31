from sqlalchemy import String,Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from datetime import datetime,timezone


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)


class UserToken(Base):
    """
    Representa la tabla 'user_tokens' encargada de almacenar los hashes
    de los refresh tokens activos para cada usuario.
    """
    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Relación con el usuario: si el usuario se elimina, sus tokens también
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        index=True
    )
    
    # El hash SHA256 tiene 64 caracteres
    token_hash: Mapped[str] = mapped_column(String(64), index=True)
    
    # Útil para auditoría o limpieza de tokens antiguos
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc)
    )
