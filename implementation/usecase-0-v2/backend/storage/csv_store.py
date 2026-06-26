import csv
from pathlib import Path
from typing import Any

from backend.storage.base import StorageService
from backend.storage.schema import DEFAULT_SHEET_TABS


class CsvStore(StorageService):
    def __init__(self, data_dir: str | Path, table_map: dict[str, str] | None = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.table_map = table_map or DEFAULT_SHEET_TABS

    def append_row(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        rows = self.list_rows(table)
        headers = self._headers(rows, row)
        rows.append({key: _stringify(row.get(key, "")) for key in headers})
        self._write_rows(table, headers, rows)
        return rows[-1]

    def list_rows(self, table: str) -> list[dict[str, Any]]:
        path = self._path(table)
        if not path.exists():
            return []
        with path.open("r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def find_by_id(self, table: str, id_field: str, id_value: str) -> dict[str, Any] | None:
        for row in self.list_rows(table):
            if row.get(id_field) == id_value:
                return row
        return None

    def update_by_id(
        self,
        table: str,
        id_field: str,
        id_value: str,
        updates: dict[str, Any],
    ) -> dict[str, Any] | None:
        rows = self.list_rows(table)
        if not rows:
            return None

        updated_row = None
        headers = self._headers(rows, updates)
        for row in rows:
            for header in headers:
                row.setdefault(header, "")
            if row.get(id_field) == id_value:
                row.update({key: _stringify(value) for key, value in updates.items()})
                updated_row = row

        if updated_row is None:
            return None
        self._write_rows(table, headers, rows)
        return updated_row

    def _path(self, table: str) -> Path:
        file_name = self.table_map.get(table, table)
        return self.data_dir / f"{file_name}.csv"

    def _headers(self, rows: list[dict[str, Any]], row: dict[str, Any]) -> list[str]:
        headers: list[str] = []
        for existing in rows:
            for key in existing.keys():
                if key not in headers:
                    headers.append(key)
        for key in row.keys():
            if key not in headers:
                headers.append(key)
        return headers

    def _write_rows(self, table: str, headers: list[str], rows: list[dict[str, Any]]) -> None:
        path = self._path(table)
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key, "") for key in headers})


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)

