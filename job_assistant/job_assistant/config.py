"""Application configuration using Pydantic Settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root is the job_assistant/ directory containing run.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
LOG_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "applications.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    log_level: str = "INFO"

    # Embedding model (local, free)
    embedding_model: str = "all-MiniLM-L6-v2"

    # RAG settings
    chroma_collection: str = "robbie_forest_kb"
    rag_top_k: int = 5

    # Scraper settings
    request_timeout: int = 15


settings = Settings()
