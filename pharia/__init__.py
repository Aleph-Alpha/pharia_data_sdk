"""
Pharia SDK - Modern Python SDK for the Pharia Data API

Configuration:
    Set environment variables before using the SDK:

    - PHARIA_DATA_API_BASE_URL: API base URL (required)
    - PHARIA_API_KEY: API authentication key (required)

Quick Start:
    >>> import asyncio
    >>> from pharia import Client
    >>>
    >>> async def main():
    ...     client = Client()  # Reads from environment variables
    ...     stages = await client.v1.stages.list()
    ...     print(f"Found {stages['total']} stages")
    >>>
    >>> asyncio.run(main())

For more examples, see the examples/ directory.
"""

from pharia.client import Client
from pharia.models import ChunkingStrategy
from pharia.models import Connector
from pharia.models import ConnectorFile
from pharia.models import ConnectorFilesListResponse
from pharia.models import ConnectorListResponse
from pharia.models import ConnectorType
from pharia.models import ContentDTO
from pharia.models import CreateConnectorInput
from pharia.models import CreateDatasetInput
from pharia.models import CreateDocumentInput
from pharia.models import CreateRepositoryInput
from pharia.models import CreateSearchStoreInput
from pharia.models import CreateStageInput
from pharia.models import CreateStageSearchStoreContext
from pharia.models import Cursor
from pharia.models import DataObjectDTO
from pharia.models import Dataset
from pharia.models import DatasetListResponse
from pharia.models import DataStorage
from pharia.models import DestinationConfig
from pharia.models import DestinationType
from pharia.models import Document
from pharia.models import DocumentContentResponse
from pharia.models import DocumentListResponse
from pharia.models import DocumentSection
from pharia.models import DocumentWithContents
from pharia.models import Download
from pharia.models import EmbeddingStrategy
from pharia.models import EmbeddingStrategyInstructConfig
from pharia.models import EmbeddingStrategySemanticConfig
from pharia.models import EmbeddingStrategyVLLMConfig
from pharia.models import File
from pharia.models import FileListResponse
from pharia.models import GoogleDriveSourceConfig
from pharia.models import IngestionContext
from pharia.models import MediaType
from pharia.models import Modality
from pharia.models import PaginationBase
from pharia.models import Parameter
from pharia.models import PresignedURL
from pharia.models import QueryEngineCloseSessionResult
from pharia.models import QueryEngineCommandResult
from pharia.models import QueryEngineDatabaseFile
from pharia.models import QueryEngineQueryResult
from pharia.models import QueryEngineSession
from pharia.models import Repository
from pharia.models import RepositoryListResponse
from pharia.models import RetentionPolicy
from pharia.models import Run
from pharia.models import RunListResponse
from pharia.models import SearchInput
from pharia.models import SearchResponse
from pharia.models import SearchResult
from pharia.models import SearchStore
from pharia.models import SearchStoreListResponse
from pharia.models import SharepointSourceConfig
from pharia.models import SourceConfig
from pharia.models import Stage
from pharia.models import StageChunkingStrategy
from pharia.models import StageEmbeddingStrategy
from pharia.models import StageListResponse
from pharia.models import StageSearchStoreContext
from pharia.models import Transformation
from pharia.models import TransformationContext
from pharia.models import TransformationName
from pharia.models import Trigger
from pharia.models import TriggerInput
from pharia.models import UpdateDatasetMetadataInput
from pharia.models import UpdateSearchStoreInput
from pharia.models import UpdateStageInput
from pharia.models import create_dataset_to_api
from pharia.models import create_repository_to_api
from pharia.models import create_search_store_to_api
from pharia.models import create_stage_to_api
from pharia.models import search_input_to_api
from pharia.models import update_dataset_metadata_to_api
from pharia.models import update_search_store_to_api
from pharia.models import update_stage_to_api


__all__ = [
    "ChunkingStrategy",
    # Client
    "Client",
    # Connector types
    "Connector",
    "ConnectorFile",
    "ConnectorFilesListResponse",
    "ConnectorListResponse",
    # Enums
    "ConnectorType",
    "ContentDTO",
    "CreateConnectorInput",
    "CreateDatasetInput",
    "CreateDocumentInput",
    "CreateRepositoryInput",
    "CreateSearchStoreInput",
    "CreateStageInput",
    "CreateStageSearchStoreContext",
    "Cursor",
    "DataObjectDTO",
    "DataStorage",
    # Dataset types
    "Dataset",
    "DatasetListResponse",
    "DestinationConfig",
    "DestinationType",
    # Document types
    "Document",
    "DocumentContentResponse",
    "DocumentListResponse",
    "DocumentSection",
    "DocumentWithContents",
    # Other types
    "Download",
    "EmbeddingStrategy",
    "EmbeddingStrategyInstructConfig",
    "EmbeddingStrategySemanticConfig",
    "EmbeddingStrategyVLLMConfig",
    # File types
    "File",
    "FileListResponse",
    "GoogleDriveSourceConfig",
    "IngestionContext",
    "MediaType",
    "Modality",
    "PaginationBase",
    "Parameter",
    "PresignedURL",
    "QueryEngineCloseSessionResult",
    "QueryEngineCommandResult",
    "QueryEngineDatabaseFile",
    "QueryEngineQueryResult",
    # Query Engine types
    "QueryEngineSession",
    # Repository types
    "Repository",
    "RepositoryListResponse",
    "RetentionPolicy",
    "Run",
    "RunListResponse",
    # Search types
    "SearchInput",
    "SearchResponse",
    "SearchResult",
    # Search Store types
    "SearchStore",
    "SearchStoreListResponse",
    "SharepointSourceConfig",
    "SourceConfig",
    # Stage types
    "Stage",
    "StageChunkingStrategy",
    "StageEmbeddingStrategy",
    "StageListResponse",
    "StageSearchStoreContext",
    # Transformation & Run types
    "Transformation",
    "TransformationContext",
    "TransformationName",
    "Trigger",
    "TriggerInput",
    "UpdateDatasetMetadataInput",
    "UpdateSearchStoreInput",
    "UpdateStageInput",
    "create_dataset_to_api",
    "create_repository_to_api",
    "create_search_store_to_api",
    "create_stage_to_api",
    "search_input_to_api",
    "update_dataset_metadata_to_api",
    "update_search_store_to_api",
    "update_stage_to_api",
]
