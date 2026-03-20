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

    model_config = {"env_file": ".env"}


settings = Settings()
