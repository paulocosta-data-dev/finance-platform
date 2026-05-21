from app.pipelines.ingestion_pipeline import (
    run_ingestion_pipeline,
)


run_ingestion_pipeline(
    force_reprocess=False,
    rebuild_bronze=False,
)