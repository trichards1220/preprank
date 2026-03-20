"""Stripe webhook handler for subscription management.

Handles:
- checkout.session.completed: new subscription created
- customer.subscription.updated: plan change, renewal
- customer.subscription.deleted: cancellation
- invoice.payment_failed: payment failure
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.users import User

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Stripe subscription price ID -> our tier mapping
PRICE_TO_TIER = {
    # Configure these in .env or settings once Stripe products are created
    "price_premium_monthly": "premium_monthly",
    "price_season_pass": "season_pass",
    "price_annual": "annual",
}


def _verify_stripe_signature(payload: bytes, sig_header: str) -> dict:
    """Verify Stripe webhook signature and return the event object."""
    try:
        import stripe
        stripe.api_key = settings.stripe_secret_key
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
        return event
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Stripe SDK not installed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook signature verification failed: {e}",
        )


async def _get_user_by_stripe_id(
    stripe_customer_id: str, db: AsyncSession
) -> User | None:
    result = await db.execute(
        select(User).where(User.stripe_customer_id == stripe_customer_id)
    )
    return result.scalar_one_or_none()


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    event = _verify_stripe_signature(payload, sig_header)
    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        # New subscription — link Stripe customer to our user
        customer_id = data.get("customer")
        client_ref = data.get("client_reference_id")  # our user.id, set at checkout
        if customer_id and client_ref:
            result = await db.execute(
                select(User).where(User.id == int(client_ref))
            )
            user = result.scalar_one_or_none()
            if user:
                user.stripe_customer_id = customer_id
                # Determine tier from the subscription
                sub_id = data.get("subscription")
                if sub_id:
                    import stripe
                    stripe.api_key = settings.stripe_secret_key
                    sub = stripe.Subscription.retrieve(sub_id)
                    price_id = sub["items"]["data"][0]["price"]["id"]
                    user.subscription_tier = PRICE_TO_TIER.get(price_id, "premium_monthly")
                    period_end = sub.get("current_period_end")
                    if period_end:
                        user.subscription_expires = datetime.fromtimestamp(
                            period_end, tz=timezone.utc
                        )
                await db.commit()

    elif event_type == "customer.subscription.updated":
        customer_id = data.get("customer")
        user = await _get_user_by_stripe_id(customer_id, db)
        if user:
            price_id = data["items"]["data"][0]["price"]["id"]
            user.subscription_tier = PRICE_TO_TIER.get(price_id, user.subscription_tier)
            period_end = data.get("current_period_end")
            if period_end:
                user.subscription_expires = datetime.fromtimestamp(
                    period_end, tz=timezone.utc
                )
            status_val = data.get("status")
            if status_val in ("past_due", "unpaid"):
                # Keep the tier but mark as expiring
                pass
            await db.commit()

    elif event_type == "customer.subscription.deleted":
        customer_id = data.get("customer")
        user = await _get_user_by_stripe_id(customer_id, db)
        if user:
            user.subscription_tier = "free"
            user.subscription_expires = None
            await db.commit()

    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        user = await _get_user_by_stripe_id(customer_id, db)
        if user:
            # Don't immediately downgrade — Stripe retries.
            # Could send a notification here.
            pass

    return {"status": "ok"}
