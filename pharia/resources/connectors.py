from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Unpack
from typing import overload

from pharia.models import Connector
from pharia.models import ConnectorFilesListResponse
from pharia.models import ConnectorListResponse
from pharia.models import CreateConnectorInput
from pharia.models import RunListResponse
from pharia.models import create_connector_to_api
from pharia.resources.base import gather_with_limit


if TYPE_CHECKING:
    from pharia.client import Client


@dataclass
class ConnectorFiles:
    """Operations for /connectors/{connectorId}/files endpoints."""

    client: "Client"
    connector_id: str

    async def list(self, page: int = 0, size: int = 100) -> ConnectorFilesListResponse:
        """List files associated with this connector."""
        params = {"page": page, "size": size}
        return await self.client.request(
            "GET", f"/connectors/{self.connector_id}/files", params=params
        )


@dataclass
class ConnectorRuns:
    """Operations for /connectors/{connectorId}/runs endpoints."""

    client: "Client"
    connector_id: str

    async def list(self, page: int = 0, size: int = 100, status: str = "") -> RunListResponse:
        """List runs for this connector."""
        params = {"page": page, "size": size, **({} if not status else {"status": status})}
        return await self.client.request(
            "GET", f"/connectors/{self.connector_id}/runs", params=params
        )


@dataclass
class ConnectorResource:
    """Instance-level operations for a single connector."""

    client: "Client"
    connector_id: str

    @property
    def files(self) -> ConnectorFiles:
        """Access files for this connector."""
        return ConnectorFiles(client=self.client, connector_id=self.connector_id)

    @property
    def runs(self) -> ConnectorRuns:
        """Access runs for this connector."""
        return ConnectorRuns(client=self.client, connector_id=self.connector_id)

    async def get(self) -> Connector:
        """Retrieve this connector."""
        return await self.client.request("GET", f"/connectors/{self.connector_id}")

    async def delete(self) -> None:
        """Delete this connector."""
        await self.client.request("DELETE", f"/connectors/{self.connector_id}")


@dataclass
class BatchConnectorResource:
    """Batch operations for multiple connectors."""

    client: "Client"
    connector_ids: list[str]

    async def get(self, concurrency: int = 10) -> list[Connector]:
        """Retrieve multiple connectors concurrently."""
        coros = [self.client.request("GET", f"/connectors/{cid}") for cid in self.connector_ids]
        return await gather_with_limit(coros, concurrency)

    async def delete(self, concurrency: int = 10) -> None:
        """Delete multiple connectors concurrently."""
        coros = [self.client.request("DELETE", f"/connectors/{cid}") for cid in self.connector_ids]
        await gather_with_limit(coros, concurrency)


@dataclass
class Connectors:
    """Collection-level operations for /connectors endpoints."""

    client: "Client"

    @overload
    def __call__(self, id: str, /) -> ConnectorResource: ...

    @overload
    def __call__(self, *ids: str) -> BatchConnectorResource: ...

    def __call__(self, *ids: str) -> ConnectorResource | BatchConnectorResource:
        """Access a connector or batch of connectors by ID(s)."""
        if len(ids) == 1:
            return ConnectorResource(client=self.client, connector_id=ids[0])
        return BatchConnectorResource(client=self.client, connector_ids=list(ids))

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
    ) -> ConnectorListResponse:
        """List connectors with pagination and filters."""
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

    async def create(self, **connector_data: Unpack[CreateConnectorInput]) -> Connector:
        """Create a new connector."""
        payload = create_connector_to_api(connector_data)
        return await self.client.request("POST", "/connectors", json=payload)
