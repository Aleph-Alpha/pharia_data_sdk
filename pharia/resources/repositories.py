from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Unpack


if TYPE_CHECKING:
    from pharia.client import Client

from pharia.models import CreateRepositoryInput
from pharia.models import Repository
from pharia.models import RepositoryListResponse
from pharia.models import create_repository_to_api


@dataclass
class Repositories:
    """
    Operations for /repositories endpoints.
    """

    client: "Client"

    async def list(self, page: int = 0, size: int = 100) -> "RepositoryListResponse":
        """
        List repositories.

        Args:
            page: Page number (default: 0)
            size: Page size (default: 100)

        Returns:
            RepositoryListResponse with page, size, total, and repositories list
        """
        params = {"page": page, "size": size}
        return await self.client.request("GET", "/repositories", params=params)

    async def create(self, **repository_data: Unpack["CreateRepositoryInput"]) -> "Repository":
        """
        Create a new repository.

        Args:
            **repository_data: Repository configuration matching CreateRepositoryInput (snake_case)
                - name (required): Repository name
                - media_type (required): Media type (e.g., "application/jsonl")
                - modality (required): Modality (e.g., "text")
                - schema: Optional JSON schema
                - mutable: Whether the repository is mutable

        Returns:
            Created Repository object

        Example:
            repo = await client.repositories.create(
                name="My Repository",
                media_type="application/jsonl",
                modality="text",
                mutable=True
            )
        """
        # Convert snake_case to camelCase for API (without mutating input)
        payload = create_repository_to_api(repository_data)
        return await self.client.request("POST", "/repositories", json=payload)

    async def get(self, repository_id: str) -> "Repository":
        """
        Get a repository by ID.

        Args:
            repository_id: The repository ID

        Returns:
            Repository object
        """
        return await self.client.request("GET", f"/repositories/{repository_id}")

    async def delete(self, repository_id: str) -> None:
        """
        Delete a repository.

        Args:
            repository_id: The repository ID
        """
        await self.client.request("DELETE", f"/repositories/{repository_id}")
