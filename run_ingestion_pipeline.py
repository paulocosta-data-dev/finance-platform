import argparse

from app.pipelines.ingestion_pipeline import (
    run_ingestion_pipeline,
)


parser = argparse.ArgumentParser()

parser.add_argument(
    "--force-reprocess",
    action="store_true",
)

parser.add_argument(
    "--rebuild-bronze",
    action="store_true",
)

args = parser.parse_args()

run_ingestion_pipeline(
    force_reprocess=(
        args.force_reprocess
    ),
    rebuild_bronze=(
        args.rebuild_bronze
    ),
)