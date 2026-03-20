"""Create Stripe products and prices for PrepRank subscription tiers.

Usage:
    STRIPE_SECRET_KEY=sk_test_... python -m scripts.setup_stripe

Creates:
- Product: PrepRank Premium
- Price: Premium Monthly ($5.99/month recurring)
- Price: Season Pass ($24.99 one-time)
- Price: Annual ($49.99/year recurring)

Prints the price IDs to add to .env.
"""

import os
import sys

import stripe


def main():
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
    if not stripe.api_key:
        print("Set STRIPE_SECRET_KEY environment variable")
        sys.exit(1)

    print("Creating PrepRank Stripe products and prices...\n")

    # Create product
    product = stripe.Product.create(
        name="PrepRank Premium",
        description="Louisiana high school sports power rankings, predictions, and analytics",
        metadata={"app": "preprank"},
    )
    print(f"Product created: {product.id}")

    # Premium Monthly — $5.99/month recurring
    price_monthly = stripe.Price.create(
        product=product.id,
        unit_amount=599,
        currency="usd",
        recurring={"interval": "month"},
        metadata={"tier": "premium_monthly"},
        lookup_key="preprank_premium_monthly",
    )
    print(f"Premium Monthly: {price_monthly.id} ($5.99/month)")

    # Season Pass — $24.99 one-time
    price_season = stripe.Price.create(
        product=product.id,
        unit_amount=2499,
        currency="usd",
        metadata={"tier": "season_pass"},
        lookup_key="preprank_season_pass",
    )
    print(f"Season Pass:     {price_season.id} ($24.99 one-time)")

    # Annual — $49.99/year recurring
    price_annual = stripe.Price.create(
        product=product.id,
        unit_amount=4999,
        currency="usd",
        recurring={"interval": "year"},
        metadata={"tier": "annual"},
        lookup_key="preprank_annual",
    )
    print(f"Annual:          {price_annual.id} ($49.99/year)")

    print(f"\n--- Add to .env ---")
    print(f"STRIPE_PRICE_PREMIUM_MONTHLY={price_monthly.id}")
    print(f"STRIPE_PRICE_SEASON_PASS={price_season.id}")
    print(f"STRIPE_PRICE_ANNUAL={price_annual.id}")


if __name__ == "__main__":
    main()
