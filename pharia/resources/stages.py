from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Unpack
from typing import overload

from pharia.models import ConnectorType
from pharia.models import CreateStageInput
from pharia.models import CreateStageSearchStoreContext
from pharia.models import DestinationType
from pharia.models import RetentionPolicy
from pharia.models import RunListResponse
from pharia.models import Stage
from pharia.models import StageListResponse
from pharia.models import TransformationName
from pharia.models import TriggerInput
from pharia.models import UpdateStageInput
from pharia.models import create_stage_to_api
from pharia.models import update_stage_to_api
from pharia.resources.base import gather_with_limit
from pharia.resources.files import BatchStageFiles
from pharia.resources.files import StageFiles


if TYPE_CHECKING:
    from pharia.client import Client


@dataclass
class StageRuns:
    """Operations for /stages/{stageId}/runs endpoints."""

    client: "Client"
    stage_id: str

    async def list(self, page: int = 0, size: int = 100, status: str = "") -> RunListResponse:
        """List runs for a stage."""
        params = {"page": page, "size": size, **({} if not status else {"status": status})}
        return await self.client.request("GET", f"/stages/{self.stage_id}/runs", params=params)


@dataclass
class BatchStageRuns:
    """Batch list operations for runs across multiple stages."""

    client: "Client"
    stage_ids: list[str]

    async def list(
        self, page: int = 0, size: int = 100, status: str = "", concurrency: int = 10
    ) -> list[RunListResponse]:
        """List runs in multiple stages concurrently."""
        coros = [
            StageRuns(client=self.client, stage_id=sid).list(page=page, size=size, status=status)
            for sid in self.stage_ids
        ]
        return await gather_with_limit(coros, concurrency)


@dataclass
class StageResource:
    """Instance-level operations for a single stage."""

    client: "Client"
    stage_id: str

    @property
    def files(self) -> StageFiles:
        """Access files in this stage."""
        return StageFiles(client=self.client, stage_id=self.stage_id)

    @property
    def runs(self) -> StageRuns:
        """Access runs for this stage."""
        return StageRuns(client=self.client, stage_id=self.stage_id)

    async def get(self) -> Stage:
        """Retrieve this stage."""
        return await self.client.request("GET", f"/stages/{self.stage_id}")

    async def update(self, **update_data: Unpack[UpdateStageInput]) -> Stage:
        """Update this stage."""
        payload = update_stage_to_api(update_data)
        return await self.client.request("PATCH", f"/stages/{self.stage_id}", json=payload)

    async def delete(self) -> None:
        """Delete this stage."""
        await self.client.request("DELETE", f"/stages/{self.stage_id}")


@dataclass
class BatchStageResource:
    """Batch operations for multiple stages."""

    client: "Client"
    stage_ids: list[str]

    @property
    def files(self) -> BatchStageFiles:
        """Access files across multiple stages."""
        return BatchStageFiles(client=self.client, stage_ids=self.stage_ids)

    @property
    def runs(self) -> BatchStageRuns:
        """Access runs across multiple stages."""
        return BatchStageRuns(client=self.client, stage_ids=self.stage_ids)

    async def get(self, concurrency: int = 10) -> list[Stage]:
        """Retrieve multiple stages concurrently."""
        coros = [self.client.request("GET", f"/stages/{sid}") for sid in self.stage_ids]
        return await gather_with_limit(coros, concurrency)

    async def delete(self, concurrency: int = 10) -> None:
        """Delete multiple stages concurrently."""
        coros = [self.client.request("DELETE", f"/stages/{sid}") for sid in self.stage_ids]
        await gather_with_limit(coros, concurrency)


@dataclass
class InstructStages:
    """Helper for creating stages with instruct embedding."""

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
        triggers: list[TriggerInput] | None = None,
        retention_policy: RetentionPolicy | None = None,
        access_policy: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Stage:
        """Create a stage with an instruct embedding strategy."""
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

        required_trigger: TriggerInput = {
            "name": "search-store-trigger",
            "transformation_name": TransformationName.DOCUMENT_TO_TEXT,
            "destination_type": DestinationType.DATA_PLATFORM_SEARCH_STORE,
            "connector_type": ConnectorType.DATA_PLATFORM_SEARCH_STORE_CREATE,
        }

        stage_input: CreateStageInput = {
            "name": name,
            "search_store": search_store,
            "triggers": [required_trigger, *(triggers or [])],
            **({} if retention_policy is None else {"retention_policy": retention_policy}),
            **({} if access_policy is None else {"access_policy": access_policy}),
        }

        payload = create_stage_to_api(stage_input)
        return await self.client.request("POST", "/stages", json=payload)


@dataclass
class SemanticStages:
    """Helper for creating stages with semantic embedding."""

    client: "Client"

    async def create(
        self,
        name: str,
        embedding_model: str,
        representation: str,
        hybrid_index: str,
        max_chunk_size_tokens: int,
        chunk_overlap_tokens: int,
        triggers: list[TriggerInput] | None = None,
        retention_policy: RetentionPolicy | None = None,
        access_policy: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Stage:
        """Create a stage with a semantic embedding strategy."""
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

        required_trigger: TriggerInput = {
            "name": "search-store-trigger",
            "transformation_name": TransformationName.DOCUMENT_TO_TEXT,
            "destination_type": DestinationType.DATA_PLATFORM_SEARCH_STORE,
            "connector_type": ConnectorType.DATA_PLATFORM_SEARCH_STORE_CREATE,
        }

        stage_input: CreateStageInput = {
            "name": name,
            "search_store": search_store,
            "triggers": [required_trigger, *(triggers or [])],
            **({} if retention_policy is None else {"retention_policy": retention_policy}),
            **({} if access_policy is None else {"access_policy": access_policy}),
        }

        payload = create_stage_to_api(stage_input)
        return await self.client.request("POST", "/stages", json=payload)


@dataclass
class VLLMStages:
    """Helper for creating stages with VLLM embedding."""

    client: "Client"

    async def create(
        self,
        name: str,
        embedding_model: str,
        hybrid_index: str,
        max_chunk_size_tokens: int,
        chunk_overlap_tokens: int,
        triggers: list[TriggerInput] | None = None,
        retention_policy: RetentionPolicy | None = None,
        access_policy: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Stage:
        """Create a stage with a VLLM embedding strategy."""
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

        required_trigger: TriggerInput = {
            "name": "search-store-trigger",
            "transformation_name": TransformationName.DOCUMENT_TO_TEXT,
            "destination_type": DestinationType.DATA_PLATFORM_SEARCH_STORE,
            "connector_type": ConnectorType.DATA_PLATFORM_SEARCH_STORE_CREATE,
        }

        stage_input: CreateStageInput = {
            "name": name,
            "search_store": search_store,
            "triggers": [required_trigger, *(triggers or [])],
            **({} if retention_policy is None else {"retention_policy": retention_policy}),
            **({} if access_policy is None else {"access_policy": access_policy}),
        }

        payload = create_stage_to_api(stage_input)
        return await self.client.request("POST", "/stages", json=payload)


@dataclass
class Stages:
    """Collection-level operations for /stages endpoints."""

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

    @overload
    def __call__(self, id: str, /) -> StageResource: ...

    @overload
    def __call__(self, *ids: str) -> BatchStageResource: ...

    def __call__(self, *ids: str) -> StageResource | BatchStageResource:
        """Access a stage or batch of stages by ID(s)."""
        if len(ids) == 1:
            return StageResource(client=self.client, stage_id=ids[0])
        return BatchStageResource(client=self.client, stage_ids=list(ids))

    async def list(
        self,
        page: int = 0,
        size: int = 100,
        name: str = "",
        access_policy: str = "",
        with_search_store: bool = False,
    ) -> StageListResponse:
        """List stages with pagination and optional filters."""
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

    async def create(self, **stage_data: Unpack[CreateStageInput]) -> Stage:
        """Create a new stage."""
        payload = create_stage_to_api(stage_data)
        return await self.client.request("POST", "/stages", json=payload)
