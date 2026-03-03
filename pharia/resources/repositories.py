from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Unpack
from typing import overload

from pharia.models import CreateRepositoryInput
from pharia.models import Repository
from pharia.models import RepositoryListResponse
from pharia.models import create_repository_to_api
from pharia.resources.base import gather_with_limit
from pharia.resources.datasets import BatchRepositoryDatasets
from pharia.resources.datasets import RepositoryDatasets


if TYPE_CHECKING:
    from pharia.client import Client


@dataclass
class RepositoryResource:
    """Instance-level operations for a single repository."""

    client: "Client"
    repository_id: str

    @property
    def datasets(self) -> RepositoryDatasets:
        """Access datasets in this repository."""
        return RepositoryDatasets(client=self.client, repository_id=self.repository_id)

    async def get(self) -> Repository:
        """Retrieve this repository."""
        return await self.client.request("GET", f"/repositories/{self.repository_id}")

    async def delete(self) -> None:
        """Delete this repository."""
        await self.client.request("DELETE", f"/repositories/{self.repository_id}")


@dataclass
class BatchRepositoryResource:
    """Batch operations for multiple repositories."""

    client: "Client"
    repository_ids: list[str]

    @property
    def datasets(self) -> BatchRepositoryDatasets:
        """Access datasets across multiple repositories."""
        return BatchRepositoryDatasets(client=self.client, repository_ids=self.repository_ids)

    async def get(self, concurrency: int = 10) -> list[Repository]:
        """Retrieve multiple repositories concurrently."""
        coros = [self.client.request("GET", f"/repositories/{rid}") for rid in self.repository_ids]
        return await gather_with_limit(coros, concurrency)

    async def delete(self, concurrency: int = 10) -> None:
        """Delete multiple repositories concurrently."""
        coros = [
            self.client.request("DELETE", f"/repositories/{rid}") for rid in self.repository_ids
        ]
        await gather_with_limit(coros, concurrency)


@dataclass
class Repositories:
    """Collection-level operations for /repositories endpoints."""

    client: "Client"

    @overload
    def __call__(self, id: str, /) -> RepositoryResource: ...

    @overload
    def __call__(self, *ids: str) -> BatchRepositoryResource: ...

    def __call__(self, *ids: str) -> RepositoryResource | BatchRepositoryResource:
        """Access a repository or batch of repositories by ID(s)."""
        if len(ids) == 1:
            return RepositoryResource(client=self.client, repository_id=ids[0])
        return BatchRepositoryResource(client=self.client, repository_ids=list(ids))

    async def list(self, page: int = 0, size: int = 100) -> RepositoryListResponse:
        """List repositories."""
        params = {"page": page, "size": size}
        return await self.client.request("GET", "/repositories", params=params)

    async def create(self, **repository_data: Unpack[CreateRepositoryInput]) -> Repository:
        """Create a new repository."""
        payload = create_repository_to_api(repository_data)
        return await self.client.request("POST", "/repositories", json=payload)
