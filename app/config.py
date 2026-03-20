from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://preprank:preprank@localhost:5432/preprank"
    secret_key: str = "change-me"
    environment: str = "development"
    monte_carlo_runs: int = 10_000

    model_config = {"env_file": ".env"}


settings = Settings()
