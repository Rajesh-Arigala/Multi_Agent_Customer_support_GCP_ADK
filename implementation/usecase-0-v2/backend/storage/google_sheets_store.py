from typing import Any

from backend.storage.base import StorageService
from backend.storage.schema import DEFAULT_SHEET_TABS


class GoogleSheetsStore(StorageService):
    def __init__(
        self,
        spreadsheet_id: str,
        table_map: dict[str, str] | None = None,
        credentials=None,
    ):
        self.spreadsheet_id = spreadsheet_id
        self.table_map = table_map or DEFAULT_SHEET_TABS
        self.service = self._build_service(credentials)

    def append_row(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        sheet = self._sheet_name(table)
        headers = self._headers(sheet)
        if not headers:
            headers = list(row.keys())
            self._set_headers(sheet, headers)
        else:
            missing = [key for key in row.keys() if key not in headers]
            if missing:
                headers.extend(missing)
                self._set_headers(sheet, headers)

        values = [[_stringify(row.get(header, "")) for header in headers]]
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        ).execute()
        return {header: values[0][index] for index, header in enumerate(headers)}

    def list_rows(self, table: str) -> list[dict[str, Any]]:
        sheet = self._sheet_name(table)
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet}!A:ZZ",
        ).execute()
        values = result.get("values", [])
        if not values:
            return []
        headers = values[0]
        rows = []
        for value_row in values[1:]:
            row = {}
            for index, header in enumerate(headers):
                row[header] = value_row[index] if index < len(value_row) else ""
            rows.append(row)
        return rows

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
        sheet = self._sheet_name(table)
        headers = self._headers(sheet)
        if not headers or id_field not in headers:
            return None

        rows = self.list_rows(table)
        for index, row in enumerate(rows, start=2):
            if row.get(id_field) == id_value:
                missing = [key for key in updates.keys() if key not in headers]
                if missing:
                    headers.extend(missing)
                    self._set_headers(sheet, headers)
                    row = {**row, **{key: "" for key in missing}}
                row.update({key: _stringify(value) for key, value in updates.items()})
                values = [[row.get(header, "") for header in headers]]
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet}!A{index}",
                    valueInputOption="USER_ENTERED",
                    body={"values": values},
                ).execute()
                return row
        return None

    def _build_service(self, credentials):
        try:
            import google.auth
            from googleapiclient.discovery import build
        except ImportError as error:
            raise RuntimeError(
                "GoogleSheetsStore requires google-api-python-client and google-auth."
            ) from error

        if credentials is None:
            credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
        return build("sheets", "v4", credentials=credentials)

    def _sheet_name(self, table: str) -> str:
        return self.table_map.get(table, table)

    def _headers(self, sheet: str) -> list[str]:
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet}!1:1",
        ).execute()
        values = result.get("values", [])
        return values[0] if values else []

    def _set_headers(self, sheet: str, headers: list[str]) -> None:
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet}!1:1",
            valueInputOption="USER_ENTERED",
            body={"values": [headers]},
        ).execute()


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)

