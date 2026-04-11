from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.payment_link import PaymentLink
from app.schemas.payment_link import PaymentLinkCreate, PaymentLinkResponse
from app.core.logging import app_logger
from uuid import uuid4

router = APIRouter(prefix="/payment-links", tags=["payment-links"])

@router.post("/", response_model=PaymentLinkResponse)
async def create_payment_link(
    data: PaymentLinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    app_logger.info(f"create payment link for user {current_user.id}")
    public_id = str(uuid4())[:8]
    payment_link = PaymentLink(
        user_id=current_user.id,
        title=data.title,
        amount=data.amount,
        currency=data.currency,
        type=data.type,
        public_id=public_id,
        extra_data=data.extra_data or {}
    )
    db.add(payment_link)
    await db.commit()
    await db.refresh(payment_link)
    return payment_link

@router.get("/", response_model=list[PaymentLinkResponse])
async def list_payment_links(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista todos los payment links del usuario autenticado."""
    result = await db.execute(
        select(PaymentLink).where(PaymentLink.user_id == current_user.id)
    )
    links = result.scalars().all()
    return links
