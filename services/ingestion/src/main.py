from src.config import settings


def main() -> None:
    print("CryptoPulse ingestion services are available:")
    print(f"- Binance stream topic: {settings.market_topic}")
    print(f"- Tracked pairs: {', '.join(settings.tracked_pair_list)}")
    print("- Run `python src/binance_stream.py` for real-time Binance ingestion")
    print("- Run `python src/coingecko_backfill.py` for historical/reference backfill")


if __name__ == "__main__":
    main()
