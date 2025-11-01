from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Unpack


if TYPE_CHECKING:
    from pharia.client import Client

from pharia.models import CreateSearchStoreInput
from pharia.models import RetentionPolicy
from pharia.models import SearchStore
from pharia.models import SearchStoreListResponse
from pharia.models import UpdateSearchStoreInput
from pharia.models import create_search_store_to_api
from pharia.models import update_search_store_to_api


@dataclass
class SemanticSearchStores:
    """Helper for creating search stores with semantic embedding."""

    client: "Client"

    async def create(
        self,
        name: str,
        embedding_model: str,
        representation: str,
        max_chunk_size_tokens: int = 512,
        chunk_overlap_tokens: int = 128,
        hybrid_index: str | None = None,
        metadata: dict[str, Any] | None = None,
        retention_policy: RetentionPolicy | None = None,
    ) -> SearchStore:
        """Create a search store with semantic embedding."""
        search_store_input: CreateSearchStoreInput = {
            "name": name,
            "embedding_strategy": {
                "type": "semantic",
                "config": {
                    "model": embedding_model,
                    "representation": representation,
                    **({} if hybrid_index is None else {"hybridIndex": hybrid_index}),
                },
            },
            "chunking_strategy": {
                "maxChunkSizeTokens": max_chunk_size_tokens,
                "chunkOverlapTokens": chunk_overlap_tokens,
            },
            **({} if metadata is None else {"metadata": metadata}),
            **({} if retention_policy is None else {"retention_policy": retention_policy}),
        }
        payload = create_search_store_to_api(search_store_input)
        return await self.client.request("POST", "/search_stores", json=payload)


@dataclass
class InstructSearchStores:
    """Helper for creating search stores with instruct embedding."""

    client: "Client"

    async def create(
        self,
        name: str,
        embedding_model: str,
        instruction_document: str,
        instruction_query: str,
        max_chunk_size_tokens: int = 512,
        chunk_overlap_tokens: int = 128,
        hybrid_index: str | None = None,
        metadata: dict[str, Any] | None = None,
        retention_policy: RetentionPolicy | None = None,
    ) -> SearchStore:
        """Create a search store with instruct embedding."""
        search_store_input: CreateSearchStoreInput = {
            "name": name,
            "embedding_strategy": {
                "type": "instruct",
                "config": {
                    "model": embedding_model,
                    "instruction": {"document": instruction_document, "query": instruction_query},
                    **({} if hybrid_index is None else {"hybridIndex": hybrid_index}),
                },
            },
            "chunking_strategy": {
                "maxChunkSizeTokens": max_chunk_size_tokens,
                "chunkOverlapTokens": chunk_overlap_tokens,
            },
            **({} if metadata is None else {"metadata": metadata}),
            **({} if retention_policy is None else {"retention_policy": retention_policy}),
        }
        payload = create_search_store_to_api(search_store_input)
        return await self.client.request("POST", "/search_stores", json=payload)


@dataclass
class SearchStores:
    """SearchStores resource for managing search stores."""

    client: "Client"

    @property
    def semantic(self) -> SemanticSearchStores:
        """Access semantic search store creation."""
        return SemanticSearchStores(self.client)

    @property
    def instruct(self) -> InstructSearchStores:
        """Access instruct search store creation."""
        return InstructSearchStores(self.client)

    async def list(self, page: int = 0, size: int = 100, name: str = "") -> SearchStoreListResponse:
        """
        List search stores with pagination.

        Args:
            page: Page number (default: 0)
            size: Page size (default: 100)
            name: Filter by name (optional)

        Returns:
            Paginated list of search stores
        """
        params = {"page": page, "size": size, **({} if not name else {"name": name})}
        return await self.client.request("GET", "/search_stores", params=params)

    async def get(self, search_store_id: str) -> SearchStore:
        """
        Get a search store by ID.

        Args:
            search_store_id: Search store ID

        Returns:
            Search store details
        """
        return await self.client.request("GET", f"/search_stores/{search_store_id}")

    async def update(
        self, search_store_id: str, **kwargs: Unpack[UpdateSearchStoreInput]
    ) -> SearchStore:
        """
        Update a search store.

        Args:
            search_store_id: Search store ID
            **kwargs: Update parameters (UpdateSearchStoreInput)

        Returns:
            Updated search store
        """
        payload = update_search_store_to_api(kwargs)
        return await self.client.request("PATCH", f"/search_stores/{search_store_id}", json=payload)

    async def delete(self, search_store_id: str) -> None:
        """
        Delete a search store.

        Args:
            search_store_id: Search store ID
        """
        await self.client.request("DELETE", f"/search_stores/{search_store_id}")
