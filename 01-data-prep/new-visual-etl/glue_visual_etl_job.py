"""
Unified Studio "Visual ETL" backing job (the NEW way).

In SageMaker Unified Studio you build this pipeline on a drag-and-drop canvas:
a Source node for the trips Parquet, a Source node for the zone CSV, transform
nodes (Filter, Derived column, Join, Change Schema...), and a Target node. The
canvas then GENERATES a Glue Spark job exactly like this one.

We keep the heavy transformation logic in the shared `taxi_transforms` module so
the SAME logic the EMR and notebook demos use also backs the visual job. On the
canvas, the equivalent of importing this module is a single "Custom transform"
node; most of the individual steps (Filter, Join, Derived columns) can also be
expressed as their own visual nodes — which is exactly what you demo live.

Job parameters (passed by Unified Studio / Glue as --KEY value):
  --JOB_NAME       (supplied automatically by Glue)
  --trips_path     s3://.../raw/trips/
  --zones_path     s3://.../raw/zones/taxi_zone_lookup.csv
  --output_path    s3://.../processed/visual-etl/
"""

import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

# The shared pipeline is shipped to the job via --extra-py-files, so it is
# importable here just like any local module.
from taxi_transforms import build_pipeline

# Glue injects these arguments; getResolvedOptions parses them from sys.argv.
args = getResolvedOptions(
    sys.argv, ["JOB_NAME", "trips_path", "zones_path", "output_path"]
)

# GlueContext wraps a SparkContext and is what the visual canvas uses under the
# hood. We only need the plain SparkSession from it to run our DataFrame logic.
sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

# ---- The pipeline: identical to every other demo in the series -------------
result = build_pipeline(spark, args["trips_path"], args["zones_path"])

row_count = result.count()  # forces execution; handy to print for the demo
print(f"[visual-etl] transformed row count = {row_count}")
result.show(5, truncate=False)

# Target node: write the analytics-ready table as partitioned Parquet.
(
    result.write.mode("overwrite")
    .partitionBy("pickup_date")
    .parquet(args["output_path"])
)
print(f"[visual-etl] wrote results to {args['output_path']}")

job.commit()
