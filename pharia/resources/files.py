from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any


if TYPE_CHECKING:
    from pharia.client import Client

from pharia.models import File
from pharia.models import FileListResponse
from pharia.models import PresignedURL


@dataclass
class Files:
    """
    Operations for /stages/{stageID}/files endpoints.
    """

    client: "Client"

    async def list(
        self,
        stage_id: str,
        page: int = 0,
        size: int = 100,
        name: str = "",
        created_after: str = "",
        created_before: str = "",
    ) -> "FileListResponse":
        """
        List files in a stage with pagination and filters.

        Args:
            stage_id: The stage ID
            page: Page number (default: 0)
            size: Page size (default: 100)
            name: Filter by file name
            created_after: Filter files created after this date (ISO 8601)
            created_before: Filter files created before this date (ISO 8601)

        Returns:
            FileListResponse with page, size, total, and files list
        """
        params = {
            "page": page,
            "size": size,
            **({} if not name else {"name": name}),
            **({} if not created_after else {"createdAfter": created_after}),
            **({} if not created_before else {"createdBefore": created_before}),
        }

        return await self.client.request("GET", f"/stages/{stage_id}/files", params=params)

    async def create(self, stage_id: str, file_data: dict) -> "File":
        """
        Upload a file to a stage.

        Args:
            stage_id: The stage ID
            file_data: File data including name, mediaType, etc.

        Returns:
            Created File object
        """
        return await self.client.request("POST", f"/stages/{stage_id}/files", json=file_data)

    async def get(self, stage_id: str, file_id: str) -> bytes:
        """
        Download/stream a file by ID.

        Args:
            stage_id: The stage ID
            file_id: The file ID

        Returns:
            File content as bytes
        """
        return await self.client.request_raw("GET", f"/stages/{stage_id}/files/{file_id}")

    async def update(self, stage_id: str, file_id: str, file_data: dict) -> "File":
        """
        Update a file.

        Args:
            stage_id: The stage ID
            file_id: The file ID
            file_data: Updated file data

        Returns:
            Updated File object
        """
        return await self.client.request(
            "PUT", f"/stages/{stage_id}/files/{file_id}", json=file_data
        )

    async def delete(self, stage_id: str, file_id: str) -> None:
        """
        Delete a file.

        Args:
            stage_id: The stage ID
            file_id: The file ID
        """
        await self.client.request("DELETE", f"/stages/{stage_id}/files/{file_id}")

    async def get_presigned_url(
        self, stage_id: str, file_id: str, ttl: int = 3600
    ) -> "PresignedURL":
        """
        Get a presigned URL for a file.

        Args:
            stage_id: The stage ID
            file_id: The file ID
            ttl: Time to live in seconds (default: 3600)

        Returns:
            PresignedURL object with URL and expiration
        """
        params = {"ttl": ttl}
        return await self.client.request(
            "GET", f"/stages/{stage_id}/files/{file_id}/presigned-url", params=params
        )
