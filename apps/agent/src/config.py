from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    backend_base_url: str = Field(default="http://api:8000", alias="BACKEND_BASE_URL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
