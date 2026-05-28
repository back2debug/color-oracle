import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    valid_api_keys: str = ""
    environment: str = "development"

    @property
    def api_keys(self) -> List[str]:
        raw = self.valid_api_keys or os.environ.get("COLOR_ORACLE_API_KEY", "")
        return [k.strip() for k in raw.split(",") if k.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
