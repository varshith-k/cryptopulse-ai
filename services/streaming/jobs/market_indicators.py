from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("cryptopulse-market-indicators")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )


def main() -> None:
    spark = create_spark_session()
    print("Spark session ready for market indicator jobs.")
    spark.stop()


if __name__ == "__main__":
    main()

