import argparse

from app.pipelines.normalization_pipeline import (
    run_normalization_pipeline,
)


parser = argparse.ArgumentParser()

parser.add_argument(
    "--rebuild-silver",
    action="store_true",
)

args = parser.parse_args()

run_normalization_pipeline(
    rebuild_silver=(
        args.rebuild_silver
    ),
)