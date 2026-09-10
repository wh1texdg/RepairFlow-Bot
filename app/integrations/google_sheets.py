import asyncio
import logging
from functools import partial

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetsService:
    HEADERS = [
        "ID", "Date", "Client", "Phone", "Object Type", "Repair Type",
        "Area", "City", "Address", "Budget", "Start Date", "Status",
    ]

    def __init__(self, credentials_json: dict | None, sheet_id: str):
        self.credentials_json = credentials_json
        self.sheet_id = sheet_id

    def _append_blocking(self, values: list):
        credentials = service_account.Credentials.from_service_account_info(
            self.credentials_json,
            scopes=SCOPES,
        )
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
        return (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.sheet_id,
                range="A:L",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [values]},
            )
            .execute()
        )

    async def append_request(self, request, client) -> None:
        if not self.credentials_json or not self.sheet_id:
            logger.info("Google Sheets is not configured; skipping request %s", request.id)
            return

        values = [
            request.id,
            request.created_at.isoformat() if request.created_at else "",
            client.name or "",
            client.phone or "",
            request.object_type,
            request.repair_type,
            float(request.area),
            request.city,
            request.address,
            float(request.budget),
            request.desired_start_date.isoformat(),
            request.status.value,
        ]

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, partial(self._append_blocking, values))

    async def resync_request(self, request, client) -> None:
        await self.append_request(request, client)
