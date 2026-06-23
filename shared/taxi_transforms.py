"""
Canonical NYC Taxi transformation pipeline — SINGLE SOURCE OF TRUTH.

This module defines the ONE pipeline (~14 transformations) that every demo in the
series implements. Whether the learner sees it in Data Wrangler (low-code GUI),
Unified Studio Visual ETL (Glue canvas), EMR Spark, or a Unified Studio notebook,
the *logic* is identical — only the tool changes. That is the whole pedagogical
point of the series: "here is this join in Data Wrangler... here is the same join
in Visual ETL... here it is in EMR."

It uses ONLY the standard PySpark DataFrame API (no GlueContext, no SageMaker
SDK), so the exact same function runs unchanged on:
  - AWS Glue (Visual ETL backing job)
  - EMR Serverless
  - A Unified Studio / Studio notebook Spark session
  - Local PySpark (for cheap offline testing)

Dataset: NYC TLC Yellow Taxi trips (one month, Parquet) + the taxi zone lookup
(CSV). Both are open data from the official NYC TLC CloudFront distribution.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


# Payment type codes come from the TLC data dictionary. Mapping the integer code
# to a human label is a classic "categorical encode / map values" transform that
# every tool in the series exposes a little differently.
PAYMENT_TYPE_LABELS = {
    1: "Credit card",
    2: "Cash",
    3: "No charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided trip",
}


def build_pipeline(spark: SparkSession, trips_path: str, zones_path: str) -> DataFrame:
    """Read raw taxi data and return the cleaned, enriched, analytics-ready frame.

    Each numbered block below is ONE transformation a learner can point at and
    reproduce in any of the four tools. Keep them small and independently
    demoable — during teaching you show a slice, not the whole script.
    """

    # ------------------------------------------------------------------ source
    # T0. Read the two sources. Trips is columnar Parquet; the zone lookup is a
    #     small CSV with a header. In a visual tool these are the two "Source"
    #     nodes on the canvas.
    trips = spark.read.parquet(trips_path)
    zones = (
        spark.read.option("header", "true").option("inferSchema", "true").csv(zones_path)
    )

    # T1. Standardize column names. Raw TLC columns are inconsistently cased
    #     (tpep_pickup_datetime, PULocationID...). Rename to snake_case so every
    #     downstream step — and every tool — refers to the same names.
    trips = (
        trips.withColumnRenamed("tpep_pickup_datetime", "pickup_ts")
        .withColumnRenamed("tpep_dropoff_datetime", "dropoff_ts")
        .withColumnRenamed("PULocationID", "pu_location_id")
        .withColumnRenamed("DOLocationID", "do_location_id")
        .withColumnRenamed("RatecodeID", "rate_code_id")
        .withColumnRenamed("Airport_fee", "airport_fee")
    )

    # T2. Drop rows missing the fields the whole pipeline depends on. (In Data
    #     Wrangler this is "Handle missing → Drop rows"; in Visual ETL it is a
    #     "Drop Null Fields" / Filter node.)
    trips = trips.dropna(
        subset=["pickup_ts", "dropoff_ts", "pu_location_id", "do_location_id"]
    )

    # T3. Derive trip duration in minutes from the two timestamps. Feature
    #     engineering from datetime columns.
    #     NOTE: we use unix_timestamp() rather than casting the timestamp column
    #     directly to long. Newer Spark (3.4+, e.g. EMR 7.x) reads these Parquet
    #     timestamps as TIMESTAMP_NTZ and forbids a direct cast-to-long, while
    #     older Glue Spark 3.3 allowed it. unix_timestamp() works on both — a
    #     real cross-engine portability lesson worth calling out in class.
    trips = trips.withColumn(
        "trip_duration_min",
        (F.unix_timestamp("dropoff_ts") - F.unix_timestamp("pickup_ts")) / 60.0,
    )

    # T4. Filter out impossible / outlier durations (negative clocks, multi-hour
    #     GPS glitches). Range filter on a numeric column.
    trips = trips.filter(
        (F.col("trip_duration_min") >= 1) & (F.col("trip_duration_min") <= 120)
    )

    # T5. Filter out non-positive / absurd distances.
    trips = trips.filter(
        (F.col("trip_distance") > 0) & (F.col("trip_distance") < 100)
    )

    # T6. Keep only revenue trips — positive fare and total. Removes voided and
    #     test records.
    trips = trips.filter(
        (F.col("fare_amount") > 0) & (F.col("total_amount") > 0)
    )

    # T7. Derive average speed (mph). Demonstrates a calculation that combines
    #     two engineered/!raw columns.
    trips = trips.withColumn(
        "trip_speed_mph",
        F.col("trip_distance") / (F.col("trip_duration_min") / 60.0),
    )

    # T8. Drop physically implausible speeds (data-quality filter on the derived
    #     column from T7 — order matters, a nice teaching point).
    trips = trips.filter(
        (F.col("trip_speed_mph") > 0) & (F.col("trip_speed_mph") < 80)
    )

    # T9. Extract calendar features from the pickup timestamp: hour of day,
    #     day-of-week name, and the plain date (used later for partitioning).
    trips = (
        trips.withColumn("pickup_hour", F.hour("pickup_ts"))
        .withColumn("pickup_dow", F.date_format("pickup_ts", "EEEE"))
        .withColumn("pickup_date", F.to_date("pickup_ts"))
    )

    # T10. Map the payment_type integer code to a readable label. Build the CASE
    #      expression from the shared dictionary so the mapping is identical
    #      everywhere.
    label_col = F.lit("Unknown")
    for code, label in PAYMENT_TYPE_LABELS.items():
        label_col = F.when(F.col("payment_type") == code, F.lit(label)).otherwise(
            label_col
        )
    trips = trips.withColumn("payment_label", label_col)

    # T11. Compute tip percentage of fare. (tip_amount is only reliably recorded
    #      for card payments, which makes for a good teaching caveat.)
    trips = trips.withColumn(
        "tip_pct",
        F.when(
            F.col("fare_amount") > 0,
            F.round(F.col("tip_amount") / F.col("fare_amount") * 100, 2),
        ).otherwise(F.lit(0.0)),
    )

    # T12. Bucket the trip distance into categorical bands. Classic "bin / group
    #      a numeric column" transform.
    trips = trips.withColumn(
        "trip_distance_bucket",
        F.when(F.col("trip_distance") < 2, "short")
        .when(F.col("trip_distance") < 5, "medium")
        .when(F.col("trip_distance") < 10, "long")
        .otherwise("very_long"),
    )

    # T13. Flag airport trips. Combines a fee column and the rate code (2 = JFK)
    #      into a single boolean feature.
    trips = trips.withColumn(
        "is_airport_trip",
        (F.coalesce(F.col("airport_fee"), F.lit(0)) > 0) | (F.col("rate_code_id") == 2),
    )

    # T14. Enrich with human-readable locations by JOINING the zone lookup twice
    #      — once for pickup, once for dropoff. This is the headline "join two
    #      datasets" step every tool demonstrates.
    pu_zones = zones.select(
        F.col("LocationID").alias("pu_location_id"),
        F.col("Borough").alias("pickup_borough"),
        F.col("Zone").alias("pickup_zone"),
    )
    do_zones = zones.select(
        F.col("LocationID").alias("do_location_id"),
        F.col("Borough").alias("dropoff_borough"),
        F.col("Zone").alias("dropoff_zone"),
    )
    enriched = trips.join(pu_zones, on="pu_location_id", how="left").join(
        do_zones, on="do_location_id", how="left"
    )

    # T15. Final projection: keep the analytics-ready columns in a sensible order
    #      and drop the raw intermediates. (In a visual tool this is the final
    #      "Change Schema" / "Select Fields" node before the target.)
    final = enriched.select(
        "pickup_ts",
        "dropoff_ts",
        "pickup_date",
        "pickup_hour",
        "pickup_dow",
        "passenger_count",
        "trip_distance",
        "trip_distance_bucket",
        "trip_duration_min",
        "trip_speed_mph",
        "pickup_borough",
        "pickup_zone",
        "dropoff_borough",
        "dropoff_zone",
        "is_airport_trip",
        "payment_label",
        "fare_amount",
        "tip_amount",
        "tip_pct",
        "total_amount",
    )

    return final


def add_ml_label(df: DataFrame) -> DataFrame:
    """Optional T16 used by the ML modules (Feature Store / Training / Tuning).

    Adds a binary target `high_tip` (1 when the rider tipped > 20% of fare). This
    turns the cleaned dataset into a supervised classification problem reused by
    the training, tuning, and deployment demos downstream.
    """
    return df.withColumn(
        "high_tip", (F.col("tip_pct") > 20).cast("int")
    )
