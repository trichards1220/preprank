"""Mock Stripe integration. Replace with real Stripe API calls later.

Tiers:
- free: rankings, scores, basic team pages
- premium_monthly: $4.99/mo — projections, What's At Stake, scenario builder
- season_pass: $14.99/season — same as premium, locked to one sport season
- annual: $29.99/year — all premium, all sports
"""
from datetime import datetime, timedelta, timezone


TIER_PRICES = {
    "premium_monthly": {"price": 4.99, "duration_days": 30, "name": "Premium Monthly"},
    "season_pass": {"price": 14.99, "duration_days": 120, "name": "Season Pass"},
    "annual": {"price": 29.99, "duration_days": 365, "name": "Annual"},
}


def create_checkout_session(tier: str, user_id: int) -> dict:
    """Mock: returns a fake checkout session. In prod, creates Stripe checkout."""
    if tier not in TIER_PRICES:
        raise ValueError(f"Invalid tier: {tier}")
    info = TIER_PRICES[tier]
    return {
        "session_id": f"mock_cs_{user_id}_{tier}",
        "url": f"http://localhost:3001/checkout/success?tier={tier}",
        "tier": tier,
        "price": info["price"],
        "name": info["name"],
    }


def process_checkout_complete(tier: str) -> dict:
    """Mock: returns subscription details after successful checkout."""
    if tier not in TIER_PRICES:
        raise ValueError(f"Invalid tier: {tier}")
    info = TIER_PRICES[tier]
    now = datetime.now(timezone.utc)
    return {
        "subscription_tier": tier,
        "subscription_expires": now + timedelta(days=info["duration_days"]),
    }


def cancel_subscription() -> dict:
    """Mock: cancels subscription."""
    return {
        "subscription_tier": "free",
        "subscription_expires": None,
    }
