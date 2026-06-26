from abc import ABC, abstractmethod
from typing import Any


class StorageService(ABC):
    @abstractmethod
    def append_row(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        """Append one row and return the stored row."""

    @abstractmethod
    def list_rows(self, table: str) -> list[dict[str, Any]]:
        """Return all rows for a table."""

    @abstractmethod
    def find_by_id(self, table: str, id_field: str, id_value: str) -> dict[str, Any] | None:
        """Find a row by a stable ID field."""

    @abstractmethod
    def update_by_id(
        self,
        table: str,
        id_field: str,
        id_value: str,
        updates: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update a row by ID and return the updated row."""

