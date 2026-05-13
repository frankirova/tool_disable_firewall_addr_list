"""Google Sheets adapter — reads client entries from a spreadsheet."""

from __future__ import annotations

from google.oauth2 import service_account
from googleapiclient.discovery import build

from refactor.core.models import SheetEntry
from refactor.core.interfaces import SheetReader
from refactor.core.config import config

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetsReader(SheetReader):
    """Reads IP → client-name mappings from a Google Sheet."""

    async def read_entries(self, spreadsheet_name: str) -> list[SheetEntry]:
        creds = service_account.Credentials.from_service_account_file(
            config.sheets_credentials_path, scopes=SCOPES,
        )
        service = build("sheets", "v4", credentials=creds)
        sheet_api = service.spreadsheets()

        result = sheet_api.values().get(
            spreadsheetId=config.spreadsheet_id,
            range=spreadsheet_name,
        ).execute()

        values = result.get("values", [])
        if not values or len(values) < 2:
            return []

        headers = values[0]
        rows = values[1:]

        return [
            SheetEntry(ip=row[headers.index("ip")], name=row[headers.index("nombre")])
            for row in rows
        ]
