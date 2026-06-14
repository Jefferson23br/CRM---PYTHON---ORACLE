from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "CRM Piloto"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173"
    cors_origin_regex: str = ""

    oracle_user: str = "crm_user"
    oracle_password: str = ""
    oracle_host: str = "localhost"
    oracle_port: int = 1521
    oracle_service: str = "ORCL"

    smtp_host: str = "smtp.seudominio.com.br"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "CRM Piloto <noreply@example.com>"
    smtp_tls: bool = True

    frontend_url: str = "http://localhost:5173"

    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def cors_origin_regex_pattern(self) -> str | None:
        return self.cors_origin_regex.strip() or None

    @property
    def database_url(self) -> str:
        return (
            f"oracle+oracledb://{self.oracle_user}:{self.oracle_password}"
            f"@{self.oracle_host}:{self.oracle_port}/?service_name={self.oracle_service}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
