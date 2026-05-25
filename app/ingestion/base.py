from abc import ABC
from abc import abstractmethod
from pathlib import Path

from app.domain.imports import RawTransaction


class BankAdapter(ABC):
    """
    Base adapter contract for bank file ingestion.
    """

    @property
    @abstractmethod
    def bank_id(self) -> str:
        pass

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """
        Determines if this adapter can process the file.
        """
        pass

    @abstractmethod
    def extract_raw_transactions(
        self,
        file_path: Path,
        import_file_id: str,
    ) -> list[RawTransaction]:
        """
        Extracts raw transactions from the source file.
        """
        pass