from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kafka_broker: str = Field(default="localhost:29092", alias="KAFKA_BROKER")
    market_topic: str = Field(default="market.ticks", alias="MARKET_TOPIC")
    postgres_url: str = Field(
        default="postgresql://cryptopulse:cryptopulse@localhost:5432/cryptopulse",
        alias="REALTIME_POSTGRES_URL",
    )
    consumer_group: str = Field(
        default="cryptopulse-realtime-detector",
        alias="REALTIME_CONSUMER_GROUP",
    )
    poll_timeout_ms: int = Field(default=1000, alias="REALTIME_POLL_TIMEOUT_MS")
    window_size: int = Field(default=60, alias="REALTIME_WINDOW_SIZE")
    z_threshold: float = Field(default=3.0, alias="REALTIME_Z_THRESHOLD")
    min_samples: int = Field(default=10, alias="REALTIME_MIN_SAMPLES")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
