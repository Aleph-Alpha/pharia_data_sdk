from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Unpack


if TYPE_CHECKING:
    from pharia.client import Client

from pharia.models import Connector
from pharia.models import ConnectorFilesListResponse
from pharia.models import ConnectorListResponse
from pharia.models import CreateConnectorInput
from pharia.models import RunListResponse
from pharia.models import create_connector_to_api


@dataclass
class Connectors:
    """
    Operations for /connectors endpoints.
    """

    client: "Client"

    async def list(
        self,
        page: int = 0,
        size: int = 100,
        stage_id: str = "",
        name: str = "",
        source_provider: str = "",
        connector_mode: str = "",
        created_after: str = "",
        created_before: str = "",
    ) -> "ConnectorListResponse":
        """
        List connectors with pagination and filters.

        Args:
            page: Page number (default: 0)
            size: Page size (default: 100)
            stage_id: Filter by stage ID
            name: Filter by connector name
            source_provider: Filter by source provider (e.g., "sharepoint", "google_drive")
            connector_mode: Filter by connector mode (e.g., "SYNC", "ASYNC")
            created_after: Filter connectors created after this date (ISO 8601)
            created_before: Filter connectors created before this date (ISO 8601)

        Returns:
            ConnectorListResponse with page, size, total, and connectors list
        """
        params = {
            "page": page,
            "size": size,
            **({} if not stage_id else {"stageID": stage_id}),
            **({} if not name else {"name": name}),
            **({} if not source_provider else {"sourceProvider": source_provider}),
            **({} if not connector_mode else {"connectorMode": connector_mode}),
            **({} if not created_after else {"createdAfter": created_after}),
            **({} if not created_before else {"createdBefore": created_before}),
        }

        return await self.client.request("GET", "/connectors", params=params)

    async def create(self, **connector_data: Unpack["CreateConnectorInput"]) -> "Connector":
        """
        Create a new connector.

        Args:
            **connector_data: Connector configuration matching CreateConnectorInput (snake_case)
                - connection_id (required): Connection UUID
                - name (required): Connector name
                - connector_mode (required): Mode ("SYNC" or "ASYNC")
                - stage_id (required): Target stage ID
                - source (required): Source configuration with type and configuration
                - destination: Destination configuration
                - transformation_context: Transformation context with parameters

        Returns:
            Created Connector object

        Example:
            connector = await client.connectors.create(
                connection_id="conn-uuid",
                name="SharePoint Sync",
                connector_mode="SYNC",
                stage_id="stage-uuid",
                source={
                    "type": "sharepoint",
                    "configuration": {
                        "driveId": "drive-123",
                        "folderId": "folder-456",
                        "fileIds": ["file1", "file2"]
                    }
                }
            )
        """
        # Convert snake_case to camelCase for API (without mutating input)
        payload = create_connector_to_api(connector_data)
        return await self.client.request("POST", "/connectors", json=payload)

    async def get(self, connector_id: str) -> "Connector":
        """
        Get a connector by ID.

        Args:
            connector_id: The connector ID

        Returns:
            Connector object
        """
        return await self.client.request("GET", f"/connectors/{connector_id}")

    async def delete(self, connector_id: str) -> None:
        """
        Delete a connector.

        Args:
            connector_id: The connector ID
        """
        await self.client.request("DELETE", f"/connectors/{connector_id}")

    async def list_files(
        self, connector_id: str, page: int = 0, size: int = 100
    ) -> "ConnectorFilesListResponse":
        """
        List files associated with a connector.

        Args:
            connector_id: The connector ID
            page: Page number (default: 0)
            size: Page size (default: 100)

        Returns:
            ConnectorFilesListResponse with page, size, total, and files list
        """
        params = {"page": page, "size": size}
        return await self.client.request("GET", f"/connectors/{connector_id}/files", params=params)

    async def list_runs(
        self, connector_id: str, page: int = 0, size: int = 100, status: str = ""
    ) -> "RunListResponse":
        """
        List runs for a connector.

        Args:
            connector_id: The connector ID
            page: Page number (default: 0)
            size: Page size (default: 100)
            status: Filter by run status (e.g., "PENDING", "RUNNING", "COMPLETED", "FAILED")

        Returns:
            RunListResponse with page, size, total, and runs list
        """
        params = {"page": page, "size": size, **({} if not status else {"status": status})}
        return await self.client.request("GET", f"/connectors/{connector_id}/runs", params=params)
