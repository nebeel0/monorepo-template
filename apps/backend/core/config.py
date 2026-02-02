from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "myapp"
    APP_PORT: int = 8000
    IS_LOCAL: bool = True
    DEBUG: bool = False

    # Databases
    APP_DB_URL: str = "postgresql+asyncpg://myapp:myapp_dev@localhost:5434/myapp_app_db"
    USERS_DB_URL: str = "postgresql+asyncpg://myapp:myapp_dev@localhost:5435/myapp_users_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6381/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Auth
    SECRET: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_LIFETIME_SECONDS: int = 3600

    # OAuth (Google)
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
