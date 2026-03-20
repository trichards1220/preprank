"""Stripe webhook handler for subscription lifecycle management.

Handles:
- checkout.session.completed: new subscription — link Stripe customer, activate tier
- invoice.paid: successful payment — extend/confirm subscription period
- invoice.payment_failed: payment failure — flag for retry, don't immediately downgrade
- customer.subscription.updated: plan change, renewal, or status transition
- customer.subscription.deleted: cancellation — downgrade to free
"""

from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.users import User

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _price_to_tier() -> dict[str, str]:
    """Build price ID -> tier mapping from settings."""
    mapping = {}
    if settings.stripe_price_premium_monthly:
        mapping[settings.stripe_price_premium_monthly] = "premium_monthly"
    if settings.stripe_price_season_pass:
        mapping[settings.stripe_price_season_pass] = "season_pass"
    if settings.stripe_price_annual:
        mapping[settings.stripe_price_annual] = "annual"
    return mapping


def _verify_stripe_signature(payload: bytes, sig_header: str) -> dict:
    """Verify Stripe webhook signature and return the event object."""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
        return event
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid signature: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {e}",
        )


async def _get_user_by_stripe_id(customer_id: str, db: AsyncSession) -> User | None:
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    return result.scalar_one_or_none()


def _resolve_tier(price_id: str) -> str:
    """Resolve a Stripe price ID to our subscription tier."""
    return _price_to_tier().get(price_id, "premium_monthly")


def _timestamp_to_dt(ts: int | None) -> datetime | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc)


async def _sync_subscription(user: User, subscription_data: dict, db: AsyncSession):
    """Sync subscription state from Stripe data to user record."""
    sub_status = subscription_data.get("status", "")
    items = subscription_data.get("items", {}).get("data", [])
    price_id = items[0]["price"]["id"] if items else ""
    period_end = subscription_data.get("current_period_end")

    if sub_status in ("active", "trialing"):
        user.subscription_tier = _resolve_tier(price_id)
        user.subscription_expires = _timestamp_to_dt(period_end)
    elif sub_status in ("past_due", "unpaid"):
        # Keep tier but mark the expiration — Stripe is retrying payment
        user.subscription_expires = _timestamp_to_dt(period_end)
    elif sub_status in ("canceled", "incomplete_expired"):
        user.subscription_tier = "free"
        user.subscription_expires = None

    await db.commit()


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    stripe.api_key = settings.stripe_secret_key
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    event = _verify_stripe_signature(payload, sig_header)
    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        client_ref = data.get("client_reference_id")  # our user.id
        mode = data.get("mode", "")

        if not customer_id or not client_ref:
            return {"status": "ok", "detail": "missing customer or client_reference_id"}

        result = await db.execute(select(User).where(User.id == int(client_ref)))
        user = result.scalar_one_or_none()
        if not user:
            return {"status": "ok", "detail": "user not found"}

        user.stripe_customer_id = customer_id

        if mode == "subscription":
            sub_id = data.get("subscription")
            if sub_id:
                sub = stripe.Subscription.retrieve(sub_id)
                await _sync_subscription(user, sub, db)
        elif mode == "payment":
            # One-time payment (season pass)
            line_items = stripe.checkout.Session.list_line_items(data["id"])
            if line_items.data:
                price_id = line_items.data[0].price.id
                user.subscription_tier = _resolve_tier(price_id)
                # Season pass: set expiration ~5 months from now
                from datetime import timedelta
                user.subscription_expires = datetime.now(timezone.utc) + timedelta(days=150)
            await db.commit()

    elif event_type == "invoice.paid":
        customer_id = data.get("customer")
        user = await _get_user_by_stripe_id(customer_id, db)
        if user:
            sub_id = data.get("subscription")
            if sub_id:
                sub = stripe.Subscription.retrieve(sub_id)
                await _sync_subscription(user, sub, db)

    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        user = await _get_user_by_stripe_id(customer_id, db)
        if user:
            # Don't downgrade — Stripe retries. Just log / notify.
            # The subscription.updated event will fire if status changes to past_due.
            pass

    elif event_type == "customer.subscription.updated":
        customer_id = data.get("customer")
        user = await _get_user_by_stripe_id(customer_id, db)
        if user:
            await _sync_subscription(user, data, db)

    elif event_type == "customer.subscription.deleted":
        customer_id = data.get("customer")
        user = await _get_user_by_stripe_id(customer_id, db)
        if user:
            user.subscription_tier = "free"
            user.subscription_expires = None
            await db.commit()

    return {"status": "ok"}
