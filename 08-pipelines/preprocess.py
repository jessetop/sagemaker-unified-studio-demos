"""
Pipeline step 1 — data ingestion + cleanup (runs as a SageMaker Processing job).

Reads the raw NYC taxi parquet from the input channel, cleans it, engineers a
small FIXED feature set, builds the `high_tip` label, samples, and writes
headerless train/validation/test CSVs (label first column) to the output
channels. A fixed schema (no one-hot) keeps the columns deterministic so the
downstream Clarify steps can declare headers reliably.

SageMaker Processing contract:
  input  : /opt/ml/processing/input        (raw trips parquet)
  outputs: /opt/ml/processing/output/{train,validation,test}
"""

import os

import pandas as pd

IN_DIR = "/opt/ml/processing/input"
OUT = "/opt/ml/processing/output"

# Fixed, deterministic schema (label first) — shared with build_pipeline.py headers.
LABEL = "high_tip"
FEATURES = [
    "trip_distance",
    "trip_duration_min",
    "trip_speed_mph",
    "pickup_hour",
    "passenger_count",
    "fare_amount",
    "is_airport_trip",
]


def main() -> None:
    # Read only the raw columns we need (parquet files mounted into the input dir).
    files = [os.path.join(IN_DIR, f) for f in os.listdir(IN_DIR) if f.endswith(".parquet")]
    cols = [
        "tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance",
        "passenger_count", "fare_amount", "tip_amount", "payment_type",
        "RatecodeID", "Airport_fee",
    ]
    df = pd.concat([pd.read_parquet(f, columns=cols) for f in files], ignore_index=True)
    print(f"raw rows: {len(df):,}")

    # Cleanup + feature engineering (pandas mirror of the shared pipeline).
    df = df.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime"])
    dur = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60.0
    df["trip_duration_min"] = dur
    df = df[(df["trip_duration_min"] >= 1) & (df["trip_duration_min"] <= 120)]
    df = df[(df["trip_distance"] > 0) & (df["trip_distance"] < 100)]
    df = df[(df["fare_amount"] > 0)]
    df["trip_speed_mph"] = df["trip_distance"] / (df["trip_duration_min"] / 60.0)
    df = df[(df["trip_speed_mph"] > 0) & (df["trip_speed_mph"] < 80)]
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["is_airport_trip"] = ((df["Airport_fee"].fillna(0) > 0) | (df["RatecodeID"] == 2)).astype(int)

    # Label: among CARD payments (tip reliably recorded), did they tip > 20%?
    df = df[df["payment_type"] == 1]
    df["tip_pct"] = (df["tip_amount"] / df["fare_amount"] * 100).where(df["fare_amount"] > 0, 0)
    df[LABEL] = (df["tip_pct"] > 20).astype(int)

    df = df[[LABEL] + FEATURES].dropna()
    if len(df) > 150_000:
        df = df.sample(n=150_000, random_state=42)
    print(f"clean rows: {len(df):,} | positive rate: {df[LABEL].mean():.3f}")

    n = len(df)
    parts = {
        "train": df.iloc[: int(0.70 * n)],
        "validation": df.iloc[int(0.70 * n) : int(0.85 * n)],
        "test": df.iloc[int(0.85 * n) :],
    }
    for name, part in parts.items():
        d = os.path.join(OUT, name)
        os.makedirs(d, exist_ok=True)
        # Headerless, label first — the SageMaker built-in / Clarify convention.
        part.to_csv(os.path.join(d, f"{name}.csv"), index=False, header=False)
        print(f"wrote {name}: {len(part):,} rows")


if __name__ == "__main__":
    main()
