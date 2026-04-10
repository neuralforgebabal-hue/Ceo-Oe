"""
CEO AI OS - Core Configuration
Loads all settings from environment with validation.
"""
import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "data" / "logs"
    TEMPLATES_DIR: Path = BASE_DIR.parent / "templates"

    # AI Providers
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "groq"
    AI_MODEL: str = "llama-3.3-70b-versatile"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ceo_os.db"

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Security
    SECRET_KEY: str = "ceo-os-default-secret-change-in-production"
    ENCRYPTION_KEY: Optional[str] = None

    # Scanner
    SCAN_ROOT: str = "~/"
    SCAN_EXCLUDE: str = ".git,node_modules,__pycache__,.venv,venv,.cache,tmp,.npm"

    # System
    DEBUG: bool = False
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # GitHub
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_USERNAME: Optional[str] = None

    # Render
    RENDER_API_KEY: Optional[str] = None

    # Memory
    MEMORY_TTL_DAYS: int = 90
    MAX_AGENTS_CONCURRENT: int = 5

    @property
    def scan_root_path(self) -> Path:
        return Path(self.SCAN_ROOT).expanduser()

    @property
    def excluded_dirs(self) -> List[str]:
        return [d.strip() for d in self.SCAN_EXCLUDE.split(",")]

    def ensure_dirs(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
settings.ensure_dirs()
