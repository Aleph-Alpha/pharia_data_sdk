from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Unpack


if TYPE_CHECKING:
    from pharia.client import Client

from pharia.models import CreateDatasetInput
from pharia.models import Dataset
from pharia.models import DatasetListResponse
from pharia.models import UpdateDatasetMetadataInput
from pharia.models import create_dataset_to_api
from pharia.models import update_dataset_metadata_to_api


@dataclass
class Datasets:
    """
    Operations for /repositories/{repositoryID}/datasets endpoints.
    """

    client: "Client"

    async def list(
        self,
        repository_id: str,
        page: int = 0,
        size: int = 100,
        label: list[str] | None = None,
        created_after: str = "",
        created_before: str = "",
    ) -> "DatasetListResponse":
        """
        List datasets in a repository.

        Args:
            repository_id: The repository ID
            page: Page number (default: 0)
            size: Page size (default: 100)
            label: Filter by labels
            created_after: Filter datasets created after this date
            created_before: Filter datasets created before this date

        Returns:
            DatasetListResponse with page, size, total, and datasets list
        """
        params = {
            "page": page,
            "size": size,
            **({} if not label else {"label": label}),
            **({} if not created_after else {"created_after": created_after}),
            **({} if not created_before else {"created_before": created_before}),
        }

        return await self.client.request(
            "GET", f"/repositories/{repository_id}/datasets", params=params
        )

    async def create(
        self, repository_id: str, **dataset_data: Unpack["CreateDatasetInput"]
    ) -> "Dataset":
        """
        Create a new dataset.

        Args:
            repository_id: The repository ID
            **dataset_data: Dataset configuration matching CreateDatasetInput (snake_case)
                - name: Dataset name
                - metadata: Dataset metadata
                - labels: List of labels
                - total_datapoints: Total number of datapoints
                - license: License information

        Returns:
            Created Dataset object

        Example:
            dataset = await client.datasets.create(
                repository_id="repo-uuid",
                name="Training Dataset",
                labels=["training", "v1"],
                total_datapoints=1000
            )
        """
        # Convert snake_case to camelCase for API (without mutating input)
        payload = create_dataset_to_api(dataset_data)
        return await self.client.request(
            "POST", f"/repositories/{repository_id}/datasets", json=payload
        )

    async def get(self, repository_id: str, dataset_id: str, version: str = "") -> "Dataset":
        """
        Get a dataset by ID.

        Args:
            repository_id: The repository ID
            dataset_id: The dataset ID
            version: Optional specific version to retrieve

        Returns:
            Dataset object
        """
        params = {**({} if not version else {"version": version})}
        return await self.client.request(
            "GET", f"/repositories/{repository_id}/datasets/{dataset_id}", params=params
        )

    async def delete(self, repository_id: str, dataset_id: str) -> None:
        """
        Delete a dataset.

        Args:
            repository_id: The repository ID
            dataset_id: The dataset ID
        """
        await self.client.request("DELETE", f"/repositories/{repository_id}/datasets/{dataset_id}")

    async def update_metadata(
        self, repository_id: str, dataset_id: str, **metadata: Unpack["UpdateDatasetMetadataInput"]
    ) -> "Dataset":
        """
        Update dataset metadata.

        Args:
            repository_id: The repository ID
            dataset_id: The dataset ID
            **metadata: Metadata fields to update matching UpdateDatasetMetadataInput (snake_case)
                - name: Updated dataset name
                - metadata: Updated metadata
                - labels: Updated labels
                - total_datapoints: Updated total datapoints
                - license: Updated license information

        Returns:
            Updated Dataset object
        """
        # Convert snake_case to camelCase for API (without mutating input)
        payload = update_dataset_metadata_to_api(metadata)
        return await self.client.request(
            "PATCH", f"/repositories/{repository_id}/datasets/{dataset_id}/metadata", json=payload
        )

    async def get_datapoints(
        self, repository_id: str, dataset_id: str, version: str = "", start: int = 0, end: int = 0
    ) -> Any:
        """
        Get datapoints from a dataset.

        Args:
            repository_id: The repository ID
            dataset_id: The dataset ID
            version: Optional specific version
            start: Start index (optional)
            end: End index (optional)

        Returns:
            Datapoints (format depends on dataset type)
        """
        params = {
            **({} if not version else {"version": version}),
            **({} if not start else {"start": start}),
            **({} if not end else {"end": end}),
        }
        return await self.client.request(
            "GET", f"/repositories/{repository_id}/datasets/{dataset_id}/datapoints", params=params
        )

    async def update_datapoints(
        self, repository_id: str, dataset_id: str, datapoints_data: dict
    ) -> "Dataset":
        """
        Update datapoints in a dataset.

        Args:
            repository_id: The repository ID
            dataset_id: The dataset ID
            datapoints_data: Datapoints data to update

        Returns:
            Updated Dataset object
        """
        return await self.client.request(
            "PUT",
            f"/repositories/{repository_id}/datasets/{dataset_id}/datapoints",
            json=datapoints_data,
        )
