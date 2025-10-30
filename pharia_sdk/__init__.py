"""
Pharia SDK - Modern Python SDK for the Pharia Data API

Configuration:
    Set environment variables before using the SDK:

    - PHARIA_DATA_API_BASE_URL: API base URL (required)
    - PHARIA_API_KEY: API authentication key (required)

Quick Start:
    >>> import asyncio
    >>> from pharia_sdk import Client
    >>>
    >>> async def main():
    ...     client = Client()  # Reads from environment variables
    ...     stages = await client.stages.list()
    ...     print(f"Found {stages['total']} stages")
    >>>
    >>> asyncio.run(main())

For more examples, see the examples/ directory.
"""

from pharia_sdk.client import Client
from pharia_sdk.models import ChunkingStrategy
from pharia_sdk.models import Connector  # Connector types
from pharia_sdk.models import ConnectorFile
from pharia_sdk.models import ConnectorFilesListResponse
from pharia_sdk.models import ConnectorListResponse
from pharia_sdk.models import ContentDTO
from pharia_sdk.models import CreateConnectorInput
from pharia_sdk.models import CreateDatasetInput
from pharia_sdk.models import CreateDocumentInput
from pharia_sdk.models import CreateRepositoryInput
from pharia_sdk.models import CreateSearchStoreInput
from pharia_sdk.models import CreateStageInput
from pharia_sdk.models import CreateStageSearchStoreContext
from pharia_sdk.models import DataObjectDTO
from pharia_sdk.models import Dataset  # Dataset types
from pharia_sdk.models import DatasetListResponse
from pharia_sdk.models import DataStorage
from pharia_sdk.models import DestinationConfig
from pharia_sdk.models import Document  # Document types
from pharia_sdk.models import DocumentWithContents
from pharia_sdk.models import Download  # Other types
from pharia_sdk.models import EmbeddingStrategy
from pharia_sdk.models import EmbeddingStrategyInstructConfig
from pharia_sdk.models import EmbeddingStrategySemanticConfig
from pharia_sdk.models import File  # File types
from pharia_sdk.models import FileListResponse
from pharia_sdk.models import GoogleDriveSourceConfig
from pharia_sdk.models import IngestionContext
from pharia_sdk.models import PaginationBase
from pharia_sdk.models import Parameter
from pharia_sdk.models import PresignedURL
from pharia_sdk.models import QueryEngineCloseSessionResult
from pharia_sdk.models import QueryEngineCommandResult
from pharia_sdk.models import QueryEngineDatabaseFile
from pharia_sdk.models import QueryEngineQueryResult
from pharia_sdk.models import QueryEngineSession  # Query Engine types
from pharia_sdk.models import Repository  # Repository types
from pharia_sdk.models import RepositoryListResponse
from pharia_sdk.models import RetentionPolicy
from pharia_sdk.models import Run
from pharia_sdk.models import RunListResponse
from pharia_sdk.models import SearchStore  # Search Store types
from pharia_sdk.models import SearchStoreListResponse
from pharia_sdk.models import SharepointSourceConfig
from pharia_sdk.models import SourceConfig

# Export commonly used types for type hints
from pharia_sdk.models import Stage  # Stage types
from pharia_sdk.models import StageChunkingStrategy
from pharia_sdk.models import StageEmbeddingStrategy
from pharia_sdk.models import StageListResponse
from pharia_sdk.models import StageSearchStoreContext
from pharia_sdk.models import Transformation  # Transformation & Run types
from pharia_sdk.models import TransformationContext
from pharia_sdk.models import Trigger
from pharia_sdk.models import UpdateDatasetMetadataInput
from pharia_sdk.models import UpdateSearchStoreInput
from pharia_sdk.models import UpdateStageInput
from pharia_sdk.models import create_dataset_to_api
from pharia_sdk.models import create_repository_to_api
from pharia_sdk.models import create_stage_to_api
from pharia_sdk.models import update_dataset_metadata_to_api
from pharia_sdk.models import update_stage_to_api


__all__ = [
    "ChunkingStrategy",
    # Client
    "Client",
    # Connector types
    "Connector",
    "ConnectorFile",
    "ConnectorFilesListResponse",
    "ConnectorListResponse",
    "ContentDTO",
    "CreateConnectorInput",
    "CreateDatasetInput",
    "CreateDocumentInput",
    "CreateRepositoryInput",
    "CreateSearchStoreInput",
    "CreateStageInput",
    "CreateStageSearchStoreContext",
    "DataObjectDTO",
    "DataStorage",
    # Dataset types
    "Dataset",
    "DatasetListResponse",
    "DestinationConfig",
    # Document types
    "Document",
    "DocumentWithContents",
    # Other types
    "Download",
    "EmbeddingStrategy",
    "EmbeddingStrategyInstructConfig",
    "EmbeddingStrategySemanticConfig",
    # File types
    "File",
    "FileListResponse",
    "GoogleDriveSourceConfig",
    "IngestionContext",
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
    "Trigger",
    "UpdateDatasetMetadataInput",
    "UpdateSearchStoreInput",
    "UpdateStageInput",
]
