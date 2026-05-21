from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth.dependencies import get_current_user
from app.auth.premium import _is_premium
from app.schemas.subscriptions import CheckoutRequest, CheckoutResponse, SubscriptionStatusOut
from app.services.stripe_service import (
    create_checkout_session, process_checkout_complete, cancel_subscription,
    TIER_PRICES,
)

router = APIRouter()


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    req: CheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    if req.tier not in TIER_PRICES:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {req.tier}. Options: {list(TIER_PRICES.keys())}")
    session = create_checkout_session(req.tier, current_user.id)
    return CheckoutResponse(**session)


@router.post("/webhook")
def stripe_webhook(
    event: dict,
    db: Session = Depends(get_db),
):
    """Mock webhook: process checkout.session.completed events.
    In mock mode, accepts {"type": "checkout.session.completed", "user_id": N, "tier": "..."}
    """
    if event.get("type") != "checkout.session.completed":
        return {"status": "ignored"}

    user_id = event.get("user_id")
    tier = event.get("tier")
    if not user_id or not tier:
        raise HTTPException(status_code=400, detail="Missing user_id or tier")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = process_checkout_complete(tier)
    user.subscription_tier = result["subscription_tier"]
    user.subscription_expires = result["subscription_expires"]
    db.commit()

    return {"status": "ok", "tier": tier}


@router.get("/status", response_model=SubscriptionStatusOut)
def get_status(current_user: User = Depends(get_current_user)):
    return SubscriptionStatusOut(
        tier=current_user.subscription_tier,
        expires=current_user.subscription_expires,
        is_active=_is_premium(current_user),
    )


@router.post("/cancel")
def cancel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = cancel_subscription()
    current_user.subscription_tier = result["subscription_tier"]
    current_user.subscription_expires = result["subscription_expires"]
    db.commit()
    return {"status": "cancelled", "tier": "free"}
