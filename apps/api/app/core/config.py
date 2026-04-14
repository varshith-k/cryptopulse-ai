from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = Field(default="CryptoPulse AI", alias="PROJECT_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="cryptopulse", alias="POSTGRES_DB")
    postgres_user: str = Field(default="cryptopulse", alias="POSTGRES_USER")
    postgres_password: str = Field(default="cryptopulse", alias="POSTGRES_PASSWORD")
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    kafka_broker: str = Field(default="localhost:29092", alias="KAFKA_BROKER")
    jwt_secret: str = Field(default="change-me-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    api_cors_origins: str = Field(default="http://localhost:5173", alias="API_CORS_ORIGINS")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
