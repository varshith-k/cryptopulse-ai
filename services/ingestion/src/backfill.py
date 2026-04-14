from datetime import UTC, datetime
from decimal import Decimal

import psycopg


DATABASE_URL = "postgresql://cryptopulse:cryptopulse@localhost:5432/cryptopulse"


def main() -> None:
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO market_snapshots(symbol, price_usd, percent_change_24h, volume_24h, market_cap, observed_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s),
                    (%s, %s, %s, %s, %s, %s)
                """,
                (
                    "BTC",
                    Decimal("68991.42"),
                    Decimal("3.1200"),
                    Decimal("29100000000.00"),
                    Decimal("1352000000000.00"),
                    datetime.now(UTC),
                    "ETH",
                    Decimal("3588.13"),
                    Decimal("2.4100"),
                    Decimal("15940000000.00"),
                    Decimal("430100000000.00"),
                    datetime.now(UTC),
                ),
            )
        connection.commit()

    print("Backfill complete: inserted sample market snapshots for BTC and ETH.")


if __name__ == "__main__":
    main()
