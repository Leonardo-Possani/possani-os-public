from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Possani OS API"
    repository_type: str = Field(default="memory", validation_alias="REPOSITORY_TYPE")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/possani_os",
        validation_alias="DATABASE_URL",
    )


settings = Settings()
