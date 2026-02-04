from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


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
    # Individual keys (Legacy/Manual)
    gemini_api_key: str = ""
    gemini_api_key_2: str = ""
    gemini_api_key_3: str = ""
    
    # NEW: Comma-separated list for easy rotation (GEMINI_API_KEYS)
    gemini_api_keys: str = "" 
    
    @property
    def gemini_api_key_list(self) -> List[str]:
        """Get list of available API keys for rotation."""
        # 1. Try plural key string first (from GEMINI_API_KEYS env var)
        if self.gemini_api_keys:
            keys = [k.strip() for k in self.gemini_api_keys.split(",") if k.strip()]
            if keys:
                return keys
                
        # 2. Fallback to individual keys
        keys = [self.gemini_api_key, self.gemini_api_key_2, self.gemini_api_key_3]
        return [k for k in keys if k]  # Filter empty strings
    
    # Google Vision (OCR)
    google_cloud_project: str = ""


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
