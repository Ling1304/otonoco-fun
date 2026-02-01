"""
Application configuration settings.
Loads environment variables for Supabase, Weaviate, and SEC API.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    database_url: str
    
    # Weaviate Configuration
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: Optional[str] = None
    
    # Gemini Configuration (for both RAG and Weaviate embeddings)
    gemini_api_key: str = ""
    
    # SEC API Configuration
    sec_api_user_agent: str = "RegulatoryExplorer/1.0"
    sec_api_email: str = "contact@example.com"
    
    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

