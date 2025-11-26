from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/jetaide"

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""

    # OAuth - Google
    google_client_id: str = ""
    google_client_secret: str = ""

    # OAuth - Facebook
    facebook_client_id: str = ""
    facebook_client_secret: str = ""

    # App
    secret_key: str = "change-me-in-production"
    backend_url: str = "http://localhost:8005"
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
