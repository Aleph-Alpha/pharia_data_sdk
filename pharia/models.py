"""
Type definitions for Pharia Data API SDK.

These types are derived from the Go DTOs in internal/application/dtos/
and match the actual API request/response structures.
"""

from enum import Enum
from typing import Any
from typing import Literal
from typing import NotRequired
from typing import TypedDict


# =============================================================================
# Enums
# =============================================================================


class MediaType(str, Enum):
    """Valid media types for repositories and files."""

    JSONLINES = "jsonlines"
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    AVRO = "avro"


class Modality(str, Enum):
    """Valid modalities for repositories."""

    TEXT = "text"
    IMAGE = "image"


# =============================================================================
# Pagination Responses
# =============================================================================


class PaginationBase(TypedDict):
    """Base pagination response structure."""

    page: int
    size: int
    total: int


# =============================================================================
# Stage Types
# =============================================================================


class Trigger(TypedDict):
    """Stage trigger configuration."""

    name: str
    transformationName: str
    destinationType: str  # DataStorageType: "DataPlatform:Repository" | "DataPlatform:Stage" | "DataPlatform:SearchStore"
    connectorType: NotRequired[
        str | None
    ]  # DataConnectorType: "DocumentIndex:Collection" | "DocumentIndex:SearchStore" | "DataPlatform:SearchStore"
    repositoryId: NotRequired[str | None]


class RetentionPolicy(TypedDict):
    """Stage retention policy."""

    retentionPeriod: int  # Period in days


class StageChunkingStrategy(TypedDict):
    """Chunking strategy for stage search store."""

    maxChunkSizeTokens: int
    chunkOverlapTokens: int


class StageEmbeddingStrategyInstruction(TypedDict):
    """Embedding strategy instruction."""

    document: str
    query: str


class StageEmbeddingStrategyInstructConfig(TypedDict):
    """Instruct embedding strategy configuration."""

    model: str
    instruction: StageEmbeddingStrategyInstruction
    hybridIndex: str


class StageEmbeddingStrategySemanticConfig(TypedDict):
    """Semantic embedding strategy configuration."""

    model: str
    hybridIndex: str
    representation: str  # "asymmetric" or "symmetric"


class StageEmbeddingStrategyVLLMConfig(TypedDict):
    """VLLM embedding strategy configuration."""

    model: str
    hybridIndex: str


class StageEmbeddingStrategy(TypedDict):
    """Embedding strategy (oneOf pattern) - uses 'config' field for actual configuration."""

    type: Literal["instruct", "semantic", "vllm"]
    config: (
        StageEmbeddingStrategyInstructConfig
        | StageEmbeddingStrategySemanticConfig
        | StageEmbeddingStrategyVLLMConfig
    )


class StageSearchStoreContext(TypedDict):
    """Stage search store configuration (for responses)."""

    id: str
    chunkingStrategy: NotRequired[StageChunkingStrategy | None]
    embeddingStrategy: NotRequired[StageEmbeddingStrategy | None]
    metadata: NotRequired[dict[str, Any] | None]


class CreateStageSearchStoreContext(TypedDict):
    """Stage search store configuration for creation (no id field)."""

    chunkingStrategy: StageChunkingStrategy
    embeddingStrategy: StageEmbeddingStrategy
    metadata: NotRequired[dict[str, Any] | None]


class CreateStageInput(TypedDict):
    """Input for creating a stage (uses snake_case)."""

    name: str
    triggers: NotRequired[list[Trigger]]
    retention_policy: NotRequired[RetentionPolicy]
    search_store: NotRequired[CreateStageSearchStoreContext]
    access_policy: NotRequired[str]


def create_stage_to_api(data: CreateStageInput) -> dict[str, Any]:
    """
    Convert CreateStageInput (snake_case) to API format (camelCase).

    Creates a new dictionary without mutating the input.
    """
    return {
        "name": data["name"],
        **({} if "triggers" not in data else {"triggers": data["triggers"]}),
        **(
            {}
            if "retention_policy" not in data
            else {"retentionPolicy": dict(data["retention_policy"])}
        ),
        **({} if "search_store" not in data else {"searchStore": dict(data["search_store"])}),
        **({} if "access_policy" not in data else {"accessPolicy": data["access_policy"]}),
    }


class UpdateStageInput(TypedDict):
    """Input for updating a stage (uses snake_case)."""

    triggers: NotRequired[list[Trigger]]
    access_policy: NotRequired[str]
    retention_policy: NotRequired[RetentionPolicy]


def update_stage_to_api(data: UpdateStageInput) -> dict[str, Any]:
    """
    Convert UpdateStageInput (snake_case) to API format (camelCase).

    Creates a new dictionary without mutating the input.
    """
    return {
        **({} if "triggers" not in data else {"triggers": data["triggers"]}),
        **({} if "access_policy" not in data else {"accessPolicy": data["access_policy"]}),
        **(
            {}
            if "retention_policy" not in data
            else {"retentionPolicy": dict(data["retention_policy"])}
        ),
    }


class Stage(TypedDict):
    """Stage response."""

    stageId: str
    name: str
    createdAt: str
    updatedAt: str
    triggers: list[Trigger]
    retentionPolicy: NotRequired[RetentionPolicy | None]
    searchStore: NotRequired[StageSearchStoreContext | None]
    accessPolicy: NotRequired[str | None]
    filesCount: int


class StageListResponse(PaginationBase):
    """Paginated stage list response."""

    stages: list[Stage]


# =============================================================================
# File Types
# =============================================================================


class ConnectorContext(TypedDict):
    """Connector context for file ingestion."""

    collection: NotRequired[str | None]
    namespace: NotRequired[str | None]
    searchStore: NotRequired[str | None]


class DestinationContext(TypedDict):
    """Destination context for file ingestion."""

    repositoryId: NotRequired[str | None]


class TransformationContext(TypedDict):
    """Transformation context."""

    parameters: dict[str, Any]


class IngestionContext(TypedDict):
    """File ingestion context."""

    triggerName: str
    connectorContext: NotRequired[ConnectorContext | None]
    destinationContext: DestinationContext
    transformationContext: NotRequired[TransformationContext]
    metadata: dict[str, Any]


class RunFileInfo(TypedDict):
    """Run information associated with a file."""

    runId: str
    transformationId: str


class File(TypedDict):
    """File response."""

    fileId: str
    name: NotRequired[str | None]
    stageId: str
    version: str
    mediaType: str
    createdAt: str  # ISO 8601
    updatedAt: str  # ISO 8601
    expireAt: NotRequired[str | None]  # ISO 8601
    size: int
    metadata: NotRequired[dict[str, Any]]
    run: NotRequired[RunFileInfo | None]


class FileListResponse(PaginationBase):
    """Paginated file list response."""

    files: list[File]


class PresignedURL(TypedDict):
    """Presigned URL response."""

    url: str
    expiresAt: str  # ISO 8601
    objectKey: str
    mediaType: str
    size: int


# =============================================================================
# Repository Types
# =============================================================================


class CreateRepositoryInput(TypedDict):
    """Input for creating a repository (uses snake_case)."""

    name: str
    media_type: MediaType
    modality: str  # "text" | "image" | etc
    schema: NotRequired[dict[str, Any] | None]
    mutable: NotRequired[bool]


def create_repository_to_api(data: CreateRepositoryInput) -> dict[str, Any]:
    """
    Convert CreateRepositoryInput (snake_case) to API format (camelCase).

    Creates a new dictionary without mutating the input.
    """
    return {
        "name": data["name"],
        "mediaType": data["media_type"],
        "modality": data["modality"],
        **(
            {}
            if "schema" not in data or data["schema"] is None
            else {"schema": dict(data["schema"])}
        ),
        **({} if "mutable" not in data else {"mutable": data["mutable"]}),
    }


class Repository(TypedDict):
    """Repository response."""

    repositoryId: str
    name: str
    mediaType: str
    modality: str
    createdAt: str
    updatedAt: str
    mutable: bool
    schema: NotRequired[dict[str, Any] | None]


class RepositoryListResponse(PaginationBase):
    """Paginated repository list response."""

    repositories: list[Repository]


# =============================================================================
# Dataset Types
# =============================================================================


class CreateDatasetInput(TypedDict):
    """Input for creating a dataset (uses snake_case)."""

    name: NotRequired[str | None]
    metadata: NotRequired[dict[str, Any] | None]
    labels: NotRequired[list[str]]
    total_datapoints: NotRequired[int]
    license: NotRequired[dict[str, Any] | None]


def create_dataset_to_api(data: CreateDatasetInput) -> dict[str, Any]:
    """
    Convert CreateDatasetInput (snake_case) to API format (camelCase).

    Creates a new dictionary without mutating the input.
    """
    return {
        **({} if "name" not in data else {"name": data["name"]}),
        **(
            {}
            if "metadata" not in data or data["metadata"] is None
            else {"metadata": dict(data["metadata"])}
        ),
        **({} if "labels" not in data else {"labels": list(data["labels"])}),
        **({} if "total_datapoints" not in data else {"totalDatapoints": data["total_datapoints"]}),
        **(
            {}
            if "license" not in data or data["license"] is None
            else {"license": dict(data["license"])}
        ),
    }


class UpdateDatasetMetadataInput(TypedDict):
    """Input for updating dataset metadata (uses snake_case)."""

    name: NotRequired[str | None]
    metadata: NotRequired[dict[str, Any] | None]
    labels: NotRequired[list[str]]
    total_datapoints: NotRequired[int]
    license: NotRequired[dict[str, Any] | None]


def update_dataset_metadata_to_api(data: UpdateDatasetMetadataInput) -> dict[str, Any]:
    """
    Convert UpdateDatasetMetadataInput (snake_case) to API format (camelCase).

    Creates a new dictionary without mutating the input.
    """
    return {
        **({} if "name" not in data else {"name": data["name"]}),
        **(
            {}
            if "metadata" not in data or data["metadata"] is None
            else {"metadata": dict(data["metadata"])}
        ),
        **({} if "labels" not in data else {"labels": list(data["labels"])}),
        **({} if "total_datapoints" not in data else {"totalDatapoints": data["total_datapoints"]}),
        **(
            {}
            if "license" not in data or data["license"] is None
            else {"license": dict(data["license"])}
        ),
    }


class Dataset(TypedDict):
    """Dataset response."""

    datasetId: str
    name: NotRequired[str | None]
    metadata: NotRequired[dict[str, Any] | None]
    labels: list[str]
    totalDatapoints: int
    version: str
    repositoryId: str
    createdAt: str
    updatedAt: str
    license: NotRequired[dict[str, Any] | None]
    projectId: NotRequired[str | None]


class DatasetListResponse(PaginationBase):
    """Paginated dataset list response."""

    datasets: list[Dataset]


# =============================================================================
# Connector Types
# =============================================================================


class SharepointSourceConfig(TypedDict):
    """SharePoint source configuration."""

    driveId: str
    folderId: str
    fileIds: list[str]


class GoogleDriveSourceConfig(TypedDict):
    """Google Drive source configuration."""

    driveId: str
    folderId: str
    fileIds: list[str]


class SourceConfig(TypedDict):
    """Generic source configuration."""

    type: str  # "sharepoint" | "google_drive"
    configuration: SharepointSourceConfig | GoogleDriveSourceConfig | dict[str, Any]


class DestinationConfig(TypedDict):
    """Connector destination configuration."""

    type: str
    collection: NotRequired[str | None]
    namespace: NotRequired[str | None]
    searchStore: NotRequired[str | None]


class CollectionDestinationConfiguration(TypedDict):
    """Collection destination details."""

    collection: str
    namespace: str
    searchStore: str


class DestinationOutput(TypedDict):
    """Connector destination output."""

    type: str
    configuration: CollectionDestinationConfiguration | dict[str, Any]


class CreateConnectorInput(TypedDict):
    """Input for creating a connector (uses snake_case)."""

    connection_id: str  # UUID string
    name: str
    connector_mode: str  # "SYNC" | "ASYNC"
    stage_id: str
    source: SourceConfig
    destination: NotRequired[DestinationConfig]
    transformation_context: NotRequired[TransformationContext]


def create_connector_to_api(data: CreateConnectorInput) -> dict[str, Any]:
    """
    Convert CreateConnectorInput (snake_case) to API format (camelCase).

    Creates a new dictionary without mutating the input.
    """
    return {
        "connectionId": data["connection_id"],
        "name": data["name"],
        "connector_mode": data["connector_mode"],
        "stage_id": data["stage_id"],
        "source": dict(data["source"]),
        **({} if "destination" not in data else {"destination": dict(data["destination"])}),
        **(
            {}
            if "transformation_context" not in data
            else {"transformationContext": dict(data["transformation_context"])}
        ),
    }


class Connector(TypedDict):
    """Connector response."""

    id: str
    connectionId: str
    name: str
    provider: str  # "sharepoint" | "google_drive"
    connector_mode: str  # "SYNC" | "ASYNC"
    stage_id: str
    source: dict[str, Any]  # Type depends on provider
    destination: DestinationOutput
    transformationContext: NotRequired[TransformationContext]
    createdAt: str  # ISO 8601
    status: str  # "CREATED" | "RUNNING" | "COMPLETED" | "FAILED"


class ConnectorListResponse(PaginationBase):
    """Paginated connector list response."""

    connectors: list[Connector]


class ConnectorFile(TypedDict):
    """Connector file information."""

    connectorId: str
    fileId: NotRequired[str | None]
    stageId: str
    mediaType: str
    name: str
    size: int
    createdAt: str  # ISO 8601
    updatedAt: str  # ISO 8601
    expiredAt: str  # ISO 8601
    status: str
    error: NotRequired[str | None]


class ConnectorFilesListResponse(PaginationBase):
    """Paginated connector files list response."""

    files: list[ConnectorFile]


# =============================================================================
# Transformation & Run Types
# =============================================================================


class Parameter(TypedDict):
    """Transformation parameter definition."""

    name: str
    type: str
    required: bool
    description: NotRequired[str]


class Transformation(TypedDict):
    """Transformation response."""

    transformationId: str
    name: str
    inputType: str  # DataObjectType
    supportedDestinations: list[str]  # List of DataStorageType
    outputSchema: NotRequired[dict[str, Any] | None]
    supportedInputMediaTypes: list[str]
    parameters: list[Parameter]


class DataObjectDTO(TypedDict):
    """Data object in run context."""

    type: str
    id: NotRequired[str]
    locations: NotRequired[list[str]]


class DataStorage(TypedDict):
    """Data storage destination."""

    type: str
    id: NotRequired[str]


class DataConnector(TypedDict):
    """Data connector information."""

    type: str  # DataConnectorType
    collection: NotRequired[str | None]
    namespace: NotRequired[str | None]
    searchStore: NotRequired[str | None]


class DataContent(TypedDict):
    """Data content with modality."""

    modality: str
    locations: list[str]


class ErrorObject(TypedDict):
    """Error object in run."""

    message: str
    code: NotRequired[str]
    details: NotRequired[dict[str, Any]]


class ChunkingConfig(TypedDict):
    """Chunking configuration."""

    maxChunkSizeTokens: int
    chunkOverlapTokens: int


class EmbeddingConfig(TypedDict):
    """Embedding configuration."""

    type: str
    model: NotRequired[str]
    hybridIndex: NotRequired[str]


class Run(TypedDict):
    """Run response."""

    runId: str
    input: DataObjectDTO
    destination: DataStorage
    parameters: dict[str, Any]
    metadata: dict[str, Any]
    fileMetadata: NotRequired[dict[str, Any]]
    destinationMapping: dict[str, str]
    connectorMapping: dict[str, str]
    connector: NotRequired[DataConnector | None]
    output: NotRequired[DataObjectDTO | None]
    content: list[DataContent]
    document: NotRequired[DataObjectDTO | None]
    status: str  # RunStatus: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED"
    errors: list[str]
    errorsObject: list[ErrorObject]
    inputMediaType: NotRequired[str | None]
    inputFileName: NotRequired[str | None]
    inputFilePaths: list[str]
    inputFileSize: NotRequired[int | None]
    transformationId: str
    transformationName: str
    createdAt: str
    updatedAt: str
    carrier: dict[str, str]
    projectId: NotRequired[str | None]
    expireAt: NotRequired[str | None]  # ISO 8601
    batchId: NotRequired[str | None]
    isBatch: bool
    chunkingConfig: NotRequired[ChunkingConfig | None]
    embeddingConfig: NotRequired[EmbeddingConfig | None]


class RunListResponse(PaginationBase):
    """Paginated run list response."""

    runs: list[Run]


# =============================================================================
# Document Types
# =============================================================================


class ContentDTO(TypedDict):
    """Document content modality."""

    modality: str
    text: NotRequired[str | None]
    bytes: NotRequired[str | None]


class CreateDocumentInput(TypedDict):
    """Input for creating a document (uses snake_case)."""

    name: str
    search_store_id: str  # UUID string
    project_id: NotRequired[str]  # UUID string
    schema_version: str
    contents: list[ContentDTO]
    metadata: NotRequired[dict[str, Any]]


def create_document_to_api(data: CreateDocumentInput) -> dict[str, Any]:
    """
    Convert CreateDocumentInput (snake_case) to API format (camelCase).

    Creates a new dictionary without mutating the input.
    """
    return {
        "name": data["name"],
        "searchStoreId": data["search_store_id"],
        "schemaVersion": data["schema_version"],
        "contents": list(data["contents"]),
        **({} if "project_id" not in data else {"projectId": data["project_id"]}),
        **({} if "metadata" not in data else {"metadata": dict(data["metadata"])}),
    }


class Document(TypedDict):
    """Document response."""

    name: str
    createdAt: str  # ISO 8601
    version: int
    metadata: NotRequired[dict[str, Any]]


class DocumentWithContents(TypedDict):
    """Document with full contents."""

    name: str
    createdAt: str  # ISO 8601
    version: int
    metadata: NotRequired[dict[str, Any]]
    contents: list[ContentDTO]


# =============================================================================
# Download Types
# =============================================================================


class Download(TypedDict):
    """Download response."""

    downloadId: str
    expireAt: str  # ISO 8601
    totalDatapoints: int
    mediaType: str
    datasetId: str
    url: str
    fileId: str
    createdAt: str
    updatedAt: str
    datasetVersion: str


# =============================================================================
# Search Store Types
# =============================================================================


class ChunkingStrategy(TypedDict):
    """Chunking strategy configuration."""

    maxChunkSizeTokens: int
    chunkOverlapTokens: int


class EmbeddingStrategyInstructConfig(TypedDict):
    """Instruct embedding strategy configuration."""

    model: str
    instruction: StageEmbeddingStrategyInstruction
    hybridIndex: NotRequired[str | None]  # "bm25" or None


class EmbeddingStrategySemanticConfig(TypedDict):
    """Semantic embedding strategy configuration."""

    model: str
    representation: str  # "asymmetric" or "symmetric"
    hybridIndex: NotRequired[str | None]  # "bm25" or None


class EmbeddingStrategy(TypedDict):
    """Embedding strategy (oneOf pattern)."""

    type: Literal["instruct", "semantic"]
    instruct: NotRequired[EmbeddingStrategyInstructConfig]
    semantic: NotRequired[EmbeddingStrategySemanticConfig]


class CreateSearchStoreInput(TypedDict):
    """Input for creating a search store (uses snake_case)."""

    name: NotRequired[str | None]
    embedding_strategy: EmbeddingStrategy
    chunking_strategy: ChunkingStrategy
    metadata: NotRequired[dict[str, Any]]
    metadata_schema: NotRequired[
        dict[str, str]
    ]  # key -> type ("string" | "integer" | "float" | "boolean" | "date_time")
    retention_policy: NotRequired[RetentionPolicy]


def create_search_store_to_api(data: CreateSearchStoreInput) -> dict[str, Any]:
    """
    Convert CreateSearchStoreInput (snake_case) to API format (camelCase).

    Creates a new dictionary without mutating the input.
    """
    return {
        "embeddingStrategy": dict(data["embedding_strategy"]),
        "chunkingStrategy": dict(data["chunking_strategy"]),
        **({} if "name" not in data else {"name": data["name"]}),
        **({} if "metadata" not in data else {"metadata": dict(data["metadata"])}),
        **(
            {}
            if "metadata_schema" not in data
            else {"metadataSchema": dict(data["metadata_schema"])}
        ),
        **(
            {}
            if "retention_policy" not in data
            else {"retentionPolicy": dict(data["retention_policy"])}
        ),
    }


class UpdateSearchStoreInput(TypedDict):
    """Input for updating a search store (uses snake_case)."""

    name: NotRequired[str]
    metadata: NotRequired[dict[str, Any]]
    access_policy: NotRequired[str]


def update_search_store_to_api(data: UpdateSearchStoreInput) -> dict[str, Any]:
    """
    Convert UpdateSearchStoreInput (snake_case) to API format (camelCase).

    Creates a new dictionary without mutating the input.
    """
    return {
        **({} if "name" not in data else {"name": data["name"]}),
        **({} if "metadata" not in data else {"metadata": dict(data["metadata"])}),
        **({} if "access_policy" not in data else {"accessPolicy": data["access_policy"]}),
    }


class SearchStore(TypedDict):
    """Search store response."""

    id: str
    name: NotRequired[str | None]
    createdAt: str  # ISO 8601
    chunkingStrategy: ChunkingStrategy
    embeddingStrategy: EmbeddingStrategy
    metadata: dict[str, Any]
    metadataSchema: dict[str, str]
    retentionPolicy: NotRequired[RetentionPolicy | None]


class SearchStoreListResponse(PaginationBase):
    """Paginated search store list response."""

    searchStores: list[SearchStore]


# =============================================================================
# Query Engine Types
# =============================================================================


class QueryEngineSession(TypedDict):
    """Query engine session."""

    session_id: str


class QueryEngineDatabaseFile(TypedDict):
    """Query engine database file."""

    table_name: str
    file_extension: str
    file_path: str


class QueryEngineCommandResult(TypedDict):
    """Query engine command result."""

    success: bool
    error_message: NotRequired[str | None]


class QueryEngineQueryResult(TypedDict):
    """Query engine query result."""

    success: bool
    error_message: NotRequired[str | None]
    result_files: list[str]


class QueryEngineCloseSessionResult(TypedDict):
    """Query engine close session result."""

    success: bool
    total_rows_written: NotRequired[int | None]


# =============================================================================
# Session/Mutation Types
# =============================================================================


class MutationStatus(TypedDict):
    """Mutation status response."""

    mutationId: str
    status: str


class BatchInsertOperation(TypedDict):
    """Batch insert operation."""

    datapoints: list[dict[str, Any]]


class DeleteOperation(TypedDict):
    """Delete operation."""

    filters: dict[str, Any]


class BatchDeleteOperation(TypedDict):
    """Batch delete operation."""

    deleteOperations: list[DeleteOperation]


class UpdateOperation(TypedDict):
    """Update operation."""

    filters: dict[str, Any]
    values: dict[str, Any]


class BatchUpdateOperation(TypedDict):
    """Batch update operation."""

    updateOperations: list[UpdateOperation]


class Mutation(TypedDict):
    """Mutation request."""

    batchInsert: NotRequired[BatchInsertOperation]
    batchDelete: NotRequired[BatchDeleteOperation]
    batchUpdate: NotRequired[BatchUpdateOperation]
