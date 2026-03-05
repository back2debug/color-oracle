from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    valid_api_keys: str = "dev-key-local"
    environment: str = "development"

    @property
    def api_keys(self) -> List[str]:
        return [k.strip() for k in self.valid_api_keys.split(",") if k.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
