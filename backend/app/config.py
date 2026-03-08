from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Pydantic V2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App
    app_name: str = "Chin Hin Employee AI Assistant"
    environment: str = "development"
    debug: bool = True
    dev_mode: bool = True  # Set false for production when real auth ready

    # Azure OpenAI (Azure AI Foundry)
    azure_ai_project_connection_string: Optional[str] = Field(None, alias="AZURE_AI_PROJECT_CONNECTION_STRING")
    azure_openai_api_key: Optional[str] = Field(None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str = ""        # contoh: https://xxxx.openai.azure.com/
    azure_openai_deployment: str = ""      # contoh: gpt-4o-mini
    azure_openai_api_version: str = "2024-02-01"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

