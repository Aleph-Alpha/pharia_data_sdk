from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Unpack
from typing import overload

from pharia.models import CreateSearchStoreInput
from pharia.models import EmbeddingStrategyVLLMConfig
from pharia.models import RetentionPolicy
from pharia.models import SearchResponse
from pharia.models import SearchStore
from pharia.models import SearchStoreListResponse
from pharia.models import UpdateSearchStoreInput
from pharia.models import create_search_store_to_api
from pharia.models import search_input_to_api
from pharia.models import update_search_store_to_api
from pharia.resources.base import gather_with_limit
from pharia.resources.documents import SearchStoreDocuments


if TYPE_CHECKING:
    from pharia.client import Client


@dataclass
class SearchStoreResource:
    """Instance-level operations for a single search store."""

    client: "Client"
    search_store_id: str

    @property
    def documents(self) -> SearchStoreDocuments:
        """Access documents in this search store."""
        return SearchStoreDocuments(client=self.client, search_store_id=self.search_store_id)

    async def get(self) -> SearchStore:
        """Retrieve this search store."""
        return await self.client.request("GET", f"/search_stores/{self.search_store_id}")

    async def update(self, **kwargs: Unpack[UpdateSearchStoreInput]) -> SearchStore:
        """Update this search store."""
        payload = update_search_store_to_api(kwargs)
        return await self.client.request(
            "PATCH", f"/search_stores/{self.search_store_id}", json=payload
        )

    async def delete(self) -> None:
        """Delete this search store."""
        await self.client.request("DELETE", f"/search_stores/{self.search_store_id}")

    async def search(
        self,
        query: str,
        limit: int = 10,
        search_type: str | None = None,
        min_score: float | None = None,
        filters: dict[str, Any] | None = None,
    ) -> SearchResponse:
        """Search this search store."""
        payload = search_input_to_api(
            {
                "query": query,
                "limit": limit,
                **({} if search_type is None else {"search_type": search_type}),
                **({} if min_score is None else {"min_score": min_score}),
                **({} if filters is None else {"filters": filters}),
            }
        )
        return await self.client.request(
            "POST", f"/search_stores/{self.search_store_id}/search", json=payload
        )


@dataclass
class BatchSearchStoreResource:
    """Batch operations for multiple search stores."""

    client: "Client"
    search_store_ids: list[str]

    async def get(self, concurrency: int = 10) -> list[SearchStore]:
        """Retrieve multiple search stores concurrently."""
        coros = [
            self.client.request("GET", f"/search_stores/{sid}") for sid in self.search_store_ids
        ]
        return await gather_with_limit(coros, concurrency)

    async def delete(self, concurrency: int = 10) -> None:
        """Delete multiple search stores concurrently."""
        coros = [
            self.client.request("DELETE", f"/search_stores/{sid}") for sid in self.search_store_ids
        ]
        await gather_with_limit(coros, concurrency)


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
class VLLMSearchStores:
    """Helper for creating search stores with VLLM embedding."""

    client: "Client"

    async def create(
        self,
        name: str,
        embedding_model: str,
        max_chunk_size_tokens: int = 512,
        chunk_overlap_tokens: int = 128,
        encoding_format: str | None = None,
        dimensions: int | None = None,
        instruction_document: str | None = None,
        instruction_query: str | None = None,
        hybrid_index: str | None = None,
        metadata: dict[str, Any] | None = None,
        retention_policy: RetentionPolicy | None = None,
    ) -> SearchStore:
        """Create a search store with VLLM embedding."""
        vllm_config: EmbeddingStrategyVLLMConfig = {
            "model": embedding_model,
            **({} if encoding_format is None else {"encodingFormat": encoding_format}),
            **({} if dimensions is None else {"dimensions": dimensions}),
            **(
                {}
                if instruction_document is None and instruction_query is None
                else {
                    "instruction": {
                        "document": instruction_document or "",
                        "query": instruction_query or "",
                    }
                }
            ),
            **({} if hybrid_index is None else {"hybridIndex": hybrid_index}),
        }

        search_store_input: CreateSearchStoreInput = {
            "name": name,
            "embedding_strategy": {"type": "vllm", "config": vllm_config},
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
    """Collection-level operations for /search_stores endpoints."""

    client: "Client"

    @property
    def semantic(self) -> SemanticSearchStores:
        """Access semantic search store creation."""
        return SemanticSearchStores(self.client)

    @property
    def instruct(self) -> InstructSearchStores:
        """Access instruct search store creation."""
        return InstructSearchStores(self.client)

    @property
    def vllm(self) -> VLLMSearchStores:
        """Access VLLM search store creation."""
        return VLLMSearchStores(self.client)

    @overload
    def __call__(self, id: str, /) -> SearchStoreResource: ...

    @overload
    def __call__(self, *ids: str) -> BatchSearchStoreResource: ...

    def __call__(self, *ids: str) -> SearchStoreResource | BatchSearchStoreResource:
        """Access a search store or batch of search stores by ID(s)."""
        if len(ids) == 1:
            return SearchStoreResource(client=self.client, search_store_id=ids[0])
        return BatchSearchStoreResource(client=self.client, search_store_ids=list(ids))

    async def list(self, page: int = 1, size: int = 100) -> SearchStoreListResponse:
        """List search stores with pagination. Page is 1-based."""
        if page < 1:
            raise ValueError(f"page must be >= 1, got {page}")
        params = {"page": page, "size": size}
        return await self.client.request("GET", "/search_stores", params=params)
