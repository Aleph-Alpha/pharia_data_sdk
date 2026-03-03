from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Unpack
from typing import overload

from pharia.models import CreateDatasetInput
from pharia.models import Dataset
from pharia.models import DatasetListResponse
from pharia.models import UpdateDatasetMetadataInput
from pharia.models import create_dataset_to_api
from pharia.models import update_dataset_metadata_to_api
from pharia.resources.base import gather_with_limit


if TYPE_CHECKING:
    from pharia.client import Client


@dataclass
class DatasetResource:
    """Instance-level operations for a single dataset."""

    client: "Client"
    repository_id: str
    dataset_id: str

    async def get(self, version: str = "") -> Dataset:
        """Retrieve this dataset."""
        params = {**({} if not version else {"version": version})}
        return await self.client.request(
            "GET", f"/repositories/{self.repository_id}/datasets/{self.dataset_id}", params=params
        )

    async def delete(self) -> None:
        """Delete this dataset."""
        await self.client.request(
            "DELETE", f"/repositories/{self.repository_id}/datasets/{self.dataset_id}"
        )

    async def update_metadata(self, **metadata: Unpack[UpdateDatasetMetadataInput]) -> Dataset:
        """Update dataset metadata."""
        payload = update_dataset_metadata_to_api(metadata)
        return await self.client.request(
            "PATCH",
            f"/repositories/{self.repository_id}/datasets/{self.dataset_id}/metadata",
            json=payload,
        )

    async def get_datapoints(self, version: str = "", start: int = 0, end: int = 0) -> Any:
        """Get datapoints from this dataset."""
        params = {
            **({} if not version else {"version": version}),
            **({} if not start else {"start": start}),
            **({} if not end else {"end": end}),
        }
        return await self.client.request(
            "GET",
            f"/repositories/{self.repository_id}/datasets/{self.dataset_id}/datapoints",
            params=params,
        )

    async def update_datapoints(self, datapoints_data: dict) -> Dataset:
        """Update datapoints in this dataset."""
        return await self.client.request(
            "PUT",
            f"/repositories/{self.repository_id}/datasets/{self.dataset_id}/datapoints",
            json=datapoints_data,
        )


@dataclass
class BatchDatasetResource:
    """Batch operations for multiple datasets in a repository."""

    client: "Client"
    repository_id: str
    dataset_ids: list[str]

    async def get(self, concurrency: int = 10) -> list[Dataset]:
        """Retrieve multiple datasets concurrently."""
        coros = [
            self.client.request("GET", f"/repositories/{self.repository_id}/datasets/{did}")
            for did in self.dataset_ids
        ]
        return await gather_with_limit(coros, concurrency)

    async def delete(self, concurrency: int = 10) -> None:
        """Delete multiple datasets concurrently."""
        coros = [
            self.client.request("DELETE", f"/repositories/{self.repository_id}/datasets/{did}")
            for did in self.dataset_ids
        ]
        await gather_with_limit(coros, concurrency)


@dataclass
class RepositoryDatasets:
    """Collection-level operations for datasets in a repository."""

    client: "Client"
    repository_id: str

    @overload
    def __call__(self, id: str, /) -> DatasetResource: ...

    @overload
    def __call__(self, *ids: str) -> BatchDatasetResource: ...

    def __call__(self, *ids: str) -> DatasetResource | BatchDatasetResource:
        """Access a dataset or batch of datasets by ID(s)."""
        if len(ids) == 1:
            return DatasetResource(
                client=self.client, repository_id=self.repository_id, dataset_id=ids[0]
            )
        return BatchDatasetResource(
            client=self.client, repository_id=self.repository_id, dataset_ids=list(ids)
        )

    async def list(
        self,
        page: int = 0,
        size: int = 100,
        label: list[str] | None = None,
        created_after: str = "",
        created_before: str = "",
    ) -> DatasetListResponse:
        """List datasets in this repository."""
        params = {
            "page": page,
            "size": size,
            **({} if not label else {"label": label}),
            **({} if not created_after else {"created_after": created_after}),
            **({} if not created_before else {"created_before": created_before}),
        }
        return await self.client.request(
            "GET", f"/repositories/{self.repository_id}/datasets", params=params
        )

    async def create(self, **dataset_data: Unpack[CreateDatasetInput]) -> Dataset:
        """Create a new dataset in this repository."""
        payload = create_dataset_to_api(dataset_data)
        return await self.client.request(
            "POST", f"/repositories/{self.repository_id}/datasets", json=payload
        )
