from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Unpack


if TYPE_CHECKING:
    from pharia.client import Client

from pharia.models import CreateStageInput
from pharia.models import CreateStageSearchStoreContext
from pharia.models import RetentionPolicy
from pharia.models import Stage
from pharia.models import StageChunkingStrategy
from pharia.models import StageEmbeddingStrategy
from pharia.models import StageEmbeddingStrategyInstructConfig
from pharia.models import StageEmbeddingStrategyInstruction
from pharia.models import StageEmbeddingStrategySemanticConfig
from pharia.models import StageEmbeddingStrategyVLLMConfig
from pharia.models import StageListResponse
from pharia.models import StageSearchStoreContext
from pharia.models import Trigger
from pharia.models import UpdateStageInput
from pharia.models import create_stage_to_api
from pharia.models import update_stage_to_api


@dataclass
class InstructStages:
    """
    Helper for creating stages with instruct embedding.
    """

    client: "Client"

    async def create(
        self,
        name: str,
        embedding_model: str,
        instruction_document: str,
        instruction_query: str,
        hybrid_index: str,
        max_chunk_size_tokens: int,
        chunk_overlap_tokens: int,
        triggers: list[Trigger] | None = None,
        retention_policy: RetentionPolicy | None = None,
        access_policy: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "Stage":
        """
        Create a stage with an instruct embedding strategy.

        Args:
            name: Stage name
            embedding_model: Embedding model name
            instruction_document: Document instruction for embedding
            instruction_query: Query instruction for embedding
            hybrid_index: Hybrid index type (e.g., "bm25")
            max_chunk_size_tokens: Maximum chunk size in tokens
            chunk_overlap_tokens: Chunk overlap in tokens
            triggers: Optional list of trigger configurations
            retention_policy: Optional retention policy
            access_policy: Optional access policy
            metadata: Optional metadata for search store

        Returns:
            Created Stage object

        Example:
            stage = await client.stages.instruct.create(
                name="My Instruct Stage",
                embedding_model="luminous-base",
                instruction_document="Represent the document for retrieval",
                instruction_query="Represent the query for retrieval",
                hybrid_index="bm25",
                max_chunk_size_tokens=512,
                chunk_overlap_tokens=128
            )
        """
        search_store: CreateStageSearchStoreContext = {
            "chunkingStrategy": {
                "maxChunkSizeTokens": max_chunk_size_tokens,
                "chunkOverlapTokens": chunk_overlap_tokens,
            },
            "embeddingStrategy": {
                "type": "instruct",
                "config": {
                    "model": embedding_model,
                    "instruction": {"document": instruction_document, "query": instruction_query},
                    "hybridIndex": hybrid_index,
                },
            },
            **({} if metadata is None else {"metadata": metadata}),
        }

        # When creating a stage with search store, we MUST include a SearchStore:CREATE trigger
        required_trigger: Trigger = {
            "name": "search-store-trigger",
            "transformationName": "DocumentToText",
            "destinationType": "DataPlatform:SearchStore",
            "connectorType": "DataPlatform:SearchStore:CREATE",
        }

        # Combine required trigger with any additional triggers
        all_triggers = [required_trigger]
        if triggers is not None:
            all_triggers.extend(triggers)

        stage_input: CreateStageInput = {
            "name": name,
            "search_store": search_store,
            "triggers": all_triggers,
            **({} if retention_policy is None else {"retention_policy": retention_policy}),
            **({} if access_policy is None else {"access_policy": access_policy}),
        }

        payload = create_stage_to_api(stage_input)
        return await self.client.request("POST", "/stages", json=payload)


@dataclass
class SemanticStages:
    """
    Helper for creating stages with semantic embedding.
    """

    client: "Client"

    async def create(
        self,
        name: str,
        embedding_model: str,
        representation: str,
        hybrid_index: str,
        max_chunk_size_tokens: int,
        chunk_overlap_tokens: int,
        triggers: list[Trigger] | None = None,
        retention_policy: RetentionPolicy | None = None,
        access_policy: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "Stage":
        """
        Create a stage with a semantic embedding strategy.

        Args:
            name: Stage name
            embedding_model: Embedding model name
            representation: Representation type ("asymmetric" or "symmetric")
            hybrid_index: Hybrid index type (e.g., "bm25")
            max_chunk_size_tokens: Maximum chunk size in tokens
            chunk_overlap_tokens: Chunk overlap in tokens
            triggers: Optional list of trigger configurations
            retention_policy: Optional retention policy
            access_policy: Optional access policy
            metadata: Optional metadata for search store

        Returns:
            Created Stage object

        Example:
            stage = await client.stages.semantic.create(
                name="My Semantic Stage",
                embedding_model="luminous-base",
                representation="asymmetric",
                hybrid_index="bm25",
                max_chunk_size_tokens=512,
                chunk_overlap_tokens=128
            )
        """
        search_store: CreateStageSearchStoreContext = {
            "chunkingStrategy": {
                "maxChunkSizeTokens": max_chunk_size_tokens,
                "chunkOverlapTokens": chunk_overlap_tokens,
            },
            "embeddingStrategy": {
                "type": "semantic",
                "config": {
                    "model": embedding_model,
                    "hybridIndex": hybrid_index,
                    "representation": representation,
                },
            },
            **({} if metadata is None else {"metadata": metadata}),
        }

        # When creating a stage with search store, we MUST include a SearchStore:CREATE trigger
        required_trigger: Trigger = {
            "name": "search-store-trigger",
            "transformationName": "DocumentToText",
            "destinationType": "DataPlatform:SearchStore",
            "connectorType": "DataPlatform:SearchStore:CREATE",
        }

        # Combine required trigger with any additional triggers
        all_triggers = [required_trigger]
        if triggers:
            all_triggers.extend(triggers)

        stage_input: CreateStageInput = {
            "name": name,
            "search_store": search_store,
            "triggers": all_triggers,
            **({} if retention_policy is None else {"retention_policy": retention_policy}),
            **({} if access_policy is None else {"access_policy": access_policy}),
        }

        payload = create_stage_to_api(stage_input)
        return await self.client.request("POST", "/stages", json=payload)


@dataclass
class VLLMStages:
    """
    Helper for creating stages with VLLM embedding.
    """

    client: "Client"

    async def create(
        self,
        name: str,
        embedding_model: str,
        hybrid_index: str,
        max_chunk_size_tokens: int,
        chunk_overlap_tokens: int,
        triggers: list[Trigger] | None = None,
        retention_policy: RetentionPolicy | None = None,
        access_policy: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "Stage":
        """
        Create a stage with a VLLM embedding strategy.

        Args:
            name: Stage name
            embedding_model: Embedding model name
            hybrid_index: Hybrid index type (e.g., "bm25")
            max_chunk_size_tokens: Maximum chunk size in tokens
            chunk_overlap_tokens: Chunk overlap in tokens
            triggers: Optional list of trigger configurations
            retention_policy: Optional retention policy
            access_policy: Optional access policy
            metadata: Optional metadata for search store

        Returns:
            Created Stage object

        Example:
            stage = await client.stages.vllm.create(
                name="My VLLM Stage",
                embedding_model="custom-vllm-model",
                hybrid_index="bm25",
                max_chunk_size_tokens=512,
                chunk_overlap_tokens=128
            )
        """
        search_store: CreateStageSearchStoreContext = {
            "chunkingStrategy": {
                "maxChunkSizeTokens": max_chunk_size_tokens,
                "chunkOverlapTokens": chunk_overlap_tokens,
            },
            "embeddingStrategy": {
                "type": "vllm",
                "config": {"model": embedding_model, "hybridIndex": hybrid_index},
            },
            **({} if metadata is None else {"metadata": metadata}),
        }

        # When creating a stage with search store, we MUST include a SearchStore:CREATE trigger
        required_trigger: Trigger = {
            "name": "search-store-trigger",
            "transformationName": "DocumentToText",
            "destinationType": "DataPlatform:SearchStore",
            "connectorType": "DataPlatform:SearchStore:CREATE",
        }

        # Combine required trigger with any additional triggers
        all_triggers = [required_trigger]
        if triggers is not None:
            all_triggers.extend(triggers)

        stage_input: CreateStageInput = {
            "name": name,
            "search_store": search_store,
            "triggers": all_triggers,
            **({} if retention_policy is None else {"retention_policy": retention_policy}),
            **({} if access_policy is None else {"access_policy": access_policy}),
        }

        payload = create_stage_to_api(stage_input)
        return await self.client.request("POST", "/stages", json=payload)


@dataclass
class Stages:
    """
    Operations for /stages endpoints.
    """

    client: "Client"

    @property
    def instruct(self) -> InstructStages:
        """Access instruct embedding stage creation."""
        return InstructStages(client=self.client)

    @property
    def semantic(self) -> SemanticStages:
        """Access semantic embedding stage creation."""
        return SemanticStages(client=self.client)

    @property
    def vllm(self) -> VLLMStages:
        """Access VLLM embedding stage creation."""
        return VLLMStages(client=self.client)

    async def list(
        self,
        page: int = 0,
        size: int = 100,
        name: str = "",
        access_policy: str = "",
        with_search_store: bool = False,
    ) -> "StageListResponse":
        """
        List stages with pagination and optional filters.

        Args:
            page: Page number (default: 0)
            size: Page size (default: 100)
            name: Filter by stage name
            access_policy: Filter by access policy
            with_search_store: Filter stages with/without search store

        Returns:
            StageListResponse with page, size, total, and stages list
        """
        params = {
            "page": page,
            "size": size,
            **({} if not name else {"name": name}),
            **({} if not access_policy else {"accessPolicy": access_policy}),
            **(
                {} if not with_search_store else {"withSearchStore": str(with_search_store).lower()}
            ),
        }

        return await self.client.request("GET", "/stages", params=params)

    async def create(self, **stage_data: Unpack["CreateStageInput"]) -> "Stage":
        """
        Create a new stage.

        Args:
            **stage_data: Stage configuration matching CreateStageInput (snake_case)
                - name (required): Stage name
                - triggers: List of trigger configurations
                - retention_policy: Retention policy configuration
                - search_store: Search store configuration
                - access_policy: Access policy

        Returns:
            Created Stage object

        Example:
            stage = await client.stages.create(
                name="My Stage",
                triggers=[{
                    "name": "my-trigger",
                    "transformationName": "text-extract",
                    "destinationType": "DataPlatform:Repository"
                }],
                retention_policy={"retentionPeriod": 30}
            )
        """
        # Convert snake_case to camelCase for API (without mutating input)
        payload = create_stage_to_api(stage_data)
        return await self.client.request("POST", "/stages", json=payload)

    async def get(self, stage_id: str) -> "Stage":
        """
        Retrieve a stage by ID.

        Args:
            stage_id: The stage ID

        Returns:
            Stage object
        """
        return await self.client.request("GET", f"/stages/{stage_id}")

    async def update(self, stage_id: str, **update_data: Unpack["UpdateStageInput"]) -> "Stage":
        """
        Update a stage's configuration.

        Args:
            stage_id: The stage ID
            **update_data: Fields to update matching UpdateStageInput (snake_case)
                - triggers: Updated trigger configurations
                - access_policy: Updated access policy
                - retention_policy: Updated retention policy

        Returns:
            Updated Stage object
        """
        # Convert snake_case to camelCase for API (without mutating input)
        payload = update_stage_to_api(update_data)
        return await self.client.request("PATCH", f"/stages/{stage_id}", json=payload)

    async def delete(self, stage_id: str) -> None:
        """
        Delete a stage by ID.

        Args:
            stage_id: The stage ID
        """
        await self.client.request("DELETE", f"/stages/{stage_id}")


@dataclass
class StageImports:
    """
    Import operations for a specific stage.

    Note: This is for legacy import operations. Consider using Connectors instead.
    """

    client: "Client"
    stage_id: str

    async def create(self, connection_id: str, provider: str, source: dict, **kwargs) -> dict:
        """
        Create a new import operation for this stage.

        Args:
            connection_id: Connection ID for authentication
            provider: Provider name (e.g., 'sharepoint')
            source: Source configuration
            **kwargs: Additional import configuration

        Returns:
            Import operation object
        """
        payload = {"connectionId": connection_id, "provider": provider, "source": source, **kwargs}

        return await self.client.request("POST", f"/stages/{self.stage_id}/imports", json=payload)

    async def get(self, import_id: str) -> dict:
        """
        Get an import operation by ID.

        Args:
            import_id: The import operation ID

        Returns:
            Import operation object
        """
        return await self.client.request("GET", f"/stages/{self.stage_id}/imports/{import_id}")
