"""Subscription management endpoints.

Handles:
- Creating Stripe checkout sessions for web/mobile
- Retrieving subscription status
- Creating Stripe billing portal sessions for plan changes
- Apple App Store receipt validation
- Google Play receipt validation
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.users import User
from app.auth import get_current_user
from app.schemas.schemas import (
    SubscriptionStatusOut, CheckoutSessionOut, BillingPortalOut,
    AppleReceiptRequest, GoogleReceiptRequest, ReceiptValidationOut,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

PLANS = {
    "premium_monthly": {
        "name": "Premium Monthly",
        "price": 5.99,
        "interval": "month",
        "mode": "subscription",
    },
    "season_pass": {
        "name": "Season Pass",
        "price": 24.99,
        "interval": None,
        "mode": "payment",
    },
    "annual": {
        "name": "Annual",
        "price": 49.99,
        "interval": "year",
        "mode": "subscription",
    },
}

TIER_TO_PRICE = {
    "premium_monthly": lambda: settings.stripe_price_premium_monthly,
    "season_pass": lambda: settings.stripe_price_season_pass,
    "annual": lambda: settings.stripe_price_annual,
}

# Apple product ID -> our tier
APPLE_PRODUCT_TIERS = {
    "com.preprank.premium_monthly": "premium_monthly",
    "com.preprank.season_pass": "season_pass",
    "com.preprank.annual": "annual",
}

# Google Play product ID -> our tier
GOOGLE_PRODUCT_TIERS = {
    "preprank_premium_monthly": "premium_monthly",
    "preprank_season_pass": "season_pass",
    "preprank_annual": "annual",
}


@router.get("/status", response_model=SubscriptionStatusOut)
async def get_subscription_status(user: User = Depends(get_current_user)):
    """Get current subscription status including plan details."""
    plan = PLANS.get(user.subscription_tier)
    is_active = user.subscription_tier != "free"
    if is_active and user.subscription_expires:
        is_active = user.subscription_expires > datetime.now(timezone.utc)

    return SubscriptionStatusOut(
        tier=user.subscription_tier,
        plan_name=plan["name"] if plan else "Free",
        is_active=is_active,
        expires_at=user.subscription_expires,
        stripe_customer_id=user.stripe_customer_id,
    )


@router.get("/plans")
async def list_plans():
    """List available subscription plans."""
    return [
        {
            "tier": tier,
            "name": info["name"],
            "price": info["price"],
            "interval": info["interval"],
            "features": _plan_features(tier),
        }
        for tier, info in PLANS.items()
    ]


@router.post("/checkout", response_model=CheckoutSessionOut)
async def create_checkout_session(
    tier: str,
    success_url: str = "preprank://subscription/success",
    cancel_url: str = "preprank://subscription/cancel",
    user: User = Depends(get_current_user),
):
    """Create a Stripe Checkout session for a subscription or one-time purchase."""
    if tier not in TIER_TO_PRICE:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")

    stripe.api_key = settings.stripe_secret_key
    price_id = TIER_TO_PRICE[tier]()
    if not price_id:
        raise HTTPException(status_code=500, detail=f"Stripe price not configured for {tier}")

    plan = PLANS[tier]

    # Create or reuse Stripe customer
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"preprank_user_id": str(user.id)},
        )
        customer_id = customer.id
    else:
        customer_id = user.stripe_customer_id

    session_params = {
        "customer": customer_id,
        "client_reference_id": str(user.id),
        "line_items": [{"price": price_id, "quantity": 1}],
        "mode": plan["mode"],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": {"tier": tier, "user_id": str(user.id)},
    }

    session = stripe.checkout.Session.create(**session_params)

    return CheckoutSessionOut(
        session_id=session.id,
        url=session.url,
    )


@router.post("/billing-portal", response_model=BillingPortalOut)
async def create_billing_portal(
    return_url: str = "preprank://settings",
    user: User = Depends(get_current_user),
):
    """Create a Stripe Billing Portal session for managing subscription."""
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription to manage")

    stripe.api_key = settings.stripe_secret_key
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=return_url,
    )
    return BillingPortalOut(url=session.url)


# ── Apple App Store IAP Validation ──────────────────────────

@router.post("/validate/apple", response_model=ReceiptValidationOut)
async def validate_apple_receipt(
    body: AppleReceiptRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate an Apple App Store receipt and activate the subscription."""
    receipt_data = body.receipt_data
    payload = {
        "receipt-data": receipt_data,
        "password": settings.apple_shared_secret,
        "exclude-old-transactions": True,
    }

    # Try production first, fall back to sandbox
    async with httpx.AsyncClient() as client:
        resp = await client.post(settings.apple_verify_url, json=payload)
        result = resp.json()

        # Status 21007 = sandbox receipt sent to production
        if result.get("status") == 21007:
            resp = await client.post(settings.apple_sandbox_url, json=payload)
            result = resp.json()

    apple_status = result.get("status", -1)
    if apple_status != 0:
        raise HTTPException(
            status_code=400,
            detail=f"Apple receipt validation failed (status {apple_status})",
        )

    # Extract the latest receipt info
    latest_receipt = result.get("latest_receipt_info", [])
    if not latest_receipt:
        # One-time purchase (season pass)
        in_app = result.get("receipt", {}).get("in_app", [])
        latest_receipt = in_app

    if not latest_receipt:
        raise HTTPException(status_code=400, detail="No purchase found in receipt")

    # Find the most recent transaction
    latest = max(latest_receipt, key=lambda x: int(x.get("purchase_date_ms", "0")))
    product_id = latest.get("product_id", "")
    expires_ms = latest.get("expires_date_ms")

    tier = APPLE_PRODUCT_TIERS.get(product_id)
    if not tier:
        raise HTTPException(status_code=400, detail=f"Unknown product: {product_id}")

    user.subscription_tier = tier
    if expires_ms:
        user.subscription_expires = datetime.fromtimestamp(
            int(expires_ms) / 1000, tz=timezone.utc
        )
    else:
        # One-time purchase — 5 months
        user.subscription_expires = datetime.now(timezone.utc) + timedelta(days=150)

    await db.commit()

    return ReceiptValidationOut(
        valid=True,
        tier=tier,
        expires_at=user.subscription_expires,
    )


# ── Google Play IAP Validation ──────────────────────────────

@router.post("/validate/google", response_model=ReceiptValidationOut)
async def validate_google_receipt(
    body: GoogleReceiptRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate a Google Play purchase/subscription token and activate."""
    product_id = body.product_id
    purchase_token = body.purchase_token
    is_subscription = body.is_subscription

    tier = GOOGLE_PRODUCT_TIERS.get(product_id)
    if not tier:
        raise HTTPException(status_code=400, detail=f"Unknown product: {product_id}")

    # Use Google Play Developer API
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            settings.google_play_credentials_json,
            scopes=["https://www.googleapis.com/auth/androidpublisher"],
        )
        service = build("androidpublisher", "v3", credentials=credentials)

        package_name = "com.preprank.app"

        if is_subscription:
            result = service.purchases().subscriptions().get(
                packageName=package_name,
                subscriptionId=product_id,
                token=purchase_token,
            ).execute()

            expiry_ms = int(result.get("expiryTimeMillis", "0"))
            user.subscription_tier = tier
            user.subscription_expires = datetime.fromtimestamp(
                expiry_ms / 1000, tz=timezone.utc
            )
        else:
            result = service.purchases().products().get(
                packageName=package_name,
                productId=product_id,
                token=purchase_token,
            ).execute()

            purchase_state = result.get("purchaseState", -1)
            if purchase_state != 0:  # 0 = purchased
                raise HTTPException(status_code=400, detail="Purchase not completed")

            user.subscription_tier = tier
            user.subscription_expires = datetime.now(timezone.utc) + timedelta(days=150)

        await db.commit()

        return ReceiptValidationOut(
            valid=True,
            tier=tier,
            expires_at=user.subscription_expires,
        )

    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Google Play validation requires google-api-python-client and google-auth",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google Play validation failed: {e}")


def _plan_features(tier: str) -> list[str]:
    if tier == "premium_monthly":
        return [
            "Predictive engine & projected final ratings",
            '"What\'s at stake" game previews',
            "Playoff probability simulator",
            "Push notifications for ranking changes",
            "Historical trends & comparisons",
        ]
    elif tier == "season_pass":
        return [
            "All Premium features for one sport season",
            "4-5 months of access",
            "No auto-renewal",
        ]
    elif tier == "annual":
        return [
            "All Premium features, all sports, all year",
            "Less than $1/week",
            "Best value — save 30% vs monthly",
        ]
    return []
