"""Saari settings ek jagah. Values `.env` se aati hain (`.env.example` dekho).

Istemal:
    from mailonix.config import get_settings
    s = get_settings()
    s.database_url
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://mailonix:mailonix@127.0.0.1:5433/mailonix?gssencmode=disable"

    # Gateway
    smtp_listen_host: str = "127.0.0.1"
    smtp_listen_port: int = Field(default=2525, ge=1, le=65535)
    scan_timeout_seconds: float = Field(default=10.0, gt=0)
    data_dir: Path = Path("./data")
    lab_trust_xclient: bool = False   # default band; lab mein .env se true

    # Checks
    checks_config: Path = Path("config/checks.toml")   # har check ki values
    disabled_checks: str = ""                           # comma se alag naam, maslan "intent,links"

    @property
    def disabled_check_names(self) -> frozenset[str]:
        return frozenset(n.strip() for n in self.disabled_checks.split(",") if n.strip())

    # Adapters
    ti_mode: Literal["live", "mock", "hybrid"] = "mock"
    delivery: Literal["mailpit", "gmail"] = "mailpit"
    mailpit_smtp_host: str = "localhost"
    mailpit_smtp_port: int = Field(default=1025, ge=1, le=65535)


@lru_cache
def get_settings() -> Settings:
    return Settings()
