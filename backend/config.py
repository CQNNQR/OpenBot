from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    DATABASE_URL: str | None = "sqlite:///./data/db.sqlite3"
    ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
