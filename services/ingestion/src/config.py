from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kafka_broker: str = Field(default="localhost:29092", alias="KAFKA_BROKER")
    market_topic: str = Field(default="market.ticks.raw", alias="MARKET_TOPIC")
    postgres_url: str = Field(
        default="postgresql://cryptopulse:cryptopulse@localhost:5432/cryptopulse",
        alias="INGESTION_POSTGRES_URL",
    )
    tracked_pairs: str = Field(
        default="btcusdt,ethusdt,solusdt,adausdt",
        alias="TRACKED_PAIRS",
    )
    binance_ws_url: str = Field(
        default="wss://stream.binance.com:9443/stream",
        alias="BINANCE_WS_URL",
    )
    coingecko_base_url: str = Field(
        default="https://api.coingecko.com/api/v3",
        alias="COINGECKO_BASE_URL",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def tracked_pair_list(self) -> list[str]:
        return [item.strip().lower() for item in self.tracked_pairs.split(",") if item.strip()]


settings = Settings()
