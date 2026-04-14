from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kafka_broker: str = Field(default="localhost:29092", alias="KAFKA_BROKER")
    market_topic: str = Field(default="market.ticks.raw", alias="MARKET_TOPIC")
    postgres_url: str = Field(
        default="postgresql://cryptopulse:cryptopulse@localhost:5432/cryptopulse",
        alias="STREAMING_POSTGRES_URL",
    )
    coingecko_base_url: str = Field(
        default="https://api.coingecko.com/api/v3",
        alias="COINGECKO_BASE_URL",
    )
    consumer_group: str = Field(
        default="cryptopulse-indicator-processor",
        alias="STREAMING_CONSUMER_GROUP",
    )
    poll_timeout_ms: int = Field(default=5000, alias="STREAMING_POLL_TIMEOUT_MS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
