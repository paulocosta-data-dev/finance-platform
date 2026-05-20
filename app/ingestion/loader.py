from pathlib import Path

from app.ingestion.adapters.cgd_adapter import CGDAdapter
from app.ingestion.adapters.activo_adapter import ActivoAdapter


class IngestionLoader:

    def __init__(self):

        self.adapters = [
            CGDAdapter(),
            ActivoAdapter(),
        ]

    def discover_files(
        self,
        raw_data_path: str,
    ) -> list[Path]:

        base_path = Path(raw_data_path)

        return [
            file_path
            for file_path in base_path.rglob("*")
            if file_path.is_file()
            and file_path.suffix.lower() in [".xlsx"]
        ]

    def get_adapter_for_file(
        self,
        file_path: Path,
    ):

        for adapter in self.adapters:

            if adapter.can_handle(file_path):
                return adapter

        return None