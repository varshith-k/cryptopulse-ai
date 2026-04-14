from datetime import UTC, datetime
from random import uniform


def build_seed_event(symbol: str) -> dict[str, object]:
    return {
        "symbol": symbol,
        "price_usd": round(uniform(100, 70000), 2),
        "percent_change_24h": round(uniform(-8, 8), 2),
        "observed_at": datetime.now(UTC).isoformat(),
    }


def main() -> None:
    symbols = ["BTC", "ETH", "SOL"]
    events = [build_seed_event(symbol) for symbol in symbols]
    print("CryptoPulse ingestion scaffold produced events:")
    for event in events:
        print(event)


if __name__ == "__main__":
    main()

