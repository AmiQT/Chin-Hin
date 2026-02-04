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
    
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""  # Legacy (anon key)
    supabase_service_role_key: str = ""  # Service role for backend operations
    
    # Gemini AI
    gemini_api_key: str = ""  # Primary key
    gemini_api_key_2: str = ""  # Fallback key 2
    gemini_api_key_3: str = ""  # Fallback key 3
    
    @property
    def gemini_api_keys(self) -> list:
        """Get list of available API keys for rotation."""
        keys = [self.gemini_api_key]
        if self.gemini_api_key_2:
            keys.append(self.gemini_api_key_2)
        if self.gemini_api_key_3:
            keys.append(self.gemini_api_key_3)
        return [k for k in keys if k]  # Filter empty
    
    # Google Vision (OCR)
    google_cloud_project: str = ""


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
