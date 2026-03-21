from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://preprank:preprank@localhost:5432/preprank"
    secret_key: str = "change-me"
    environment: str = "development"
    monte_carlo_runs: int = 10_000
    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_premium_monthly: str = ""
    stripe_price_season_pass: str = ""
    stripe_price_annual: str = ""
    # Apple IAP
    apple_shared_secret: str = ""
    apple_verify_url: str = "https://buy.itunes.apple.com/verifyReceipt"
    apple_sandbox_url: str = "https://sandbox.itunes.apple.com/verifyReceipt"
    # Google Play
    google_play_credentials_json: str = ""  # path to service account JSON
    # Firebase Cloud Messaging
    fcm_credentials_json: str = ""  # path to Firebase service account JSON

    model_config = {"env_file": ".env"}


settings = Settings()
