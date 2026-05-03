from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    backend_base_url: str = Field(default="http://api:8000", alias="BACKEND_BASE_URL")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        alias="GROQ_BASE_URL",
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        alias="GROQ_MODEL",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
