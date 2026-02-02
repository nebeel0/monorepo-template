from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "myapp"
    APP_PORT: int = 8000
    IS_LOCAL: bool = True
    DEBUG: bool = False

    # Database
    DB_URL: str = "postgresql+asyncpg://myapp:myapp_dev@localhost:5434/myapp_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6381/0"

    # Auth
    SECRET: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_LIFETIME_SECONDS: int = 3600

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
