"""
EMR Spark job (the OLD way for scalable processing).

This is the same NYC taxi pipeline run as a plain PySpark application — the kind
of script a data engineer would submit to an EMR cluster (or, here, EMR
Serverless for the cheapest possible managed Spark). There is no Glue, no
SageMaker SDK, nothing studio-specific: just `spark-submit` and the standard
DataFrame API. That is the teaching contrast — in the NEW way (Unified Studio)
you run this very logic from a managed notebook against the same engines, without
hand-rolling the cluster/app, submit, and log-plumbing you see here.

Submitted with entryPointArguments: [trips_path, zones_path, output_path].
The shared module is shipped via --py-files (see emr_serverless_submit.py).
"""

import sys

from pyspark.sql import SparkSession

from taxi_transforms import build_pipeline


def main() -> None:
    trips_path, zones_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

    # On EMR the SparkSession is created the standard way; the cluster/app
    # provides the executors.
    spark = (
        SparkSession.builder.appName("nyc-taxi-emr-pipeline").getOrCreate()
    )

    # Identical pipeline to the Visual ETL, notebook, and Data Wrangler demos.
    result = build_pipeline(spark, trips_path, zones_path)

    count = result.count()
    print(f"[emr] transformed row count = {count}")
    result.show(5, truncate=False)

    (
        result.write.mode("overwrite")
        .partitionBy("pickup_date")
        .parquet(output_path)
    )
    print(f"[emr] wrote results to {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
