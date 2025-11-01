"""
Example: Using the Pharia SDK with proper type annotations.

This example demonstrates how to use the SDK with TypedDict models
for better IDE autocomplete and type checking.
"""

import asyncio

from helpers import ExamplePrinter

from pharia import Client
from pharia import CreateConnectorInput
from pharia import CreateRepositoryInput
from pharia import CreateStageInput
from pharia import DestinationConfig
from pharia import MediaType
from pharia import Modality
from pharia import RetentionPolicy
from pharia import SharepointSourceConfig
from pharia import Trigger


async def main():
    """Example showing how to use the SDK with type hints."""

    # Client reads credentials from environment variables:
    # - PHARIA_DATA_API_BASE_URL
    # - PHARIA_API_KEY
    client = Client()

    with ExamplePrinter("Type-Safe Usage Examples") as p:
        # Example 1: Create a stage with proper typing
        p.section(1, 5, "Creating a stage with type annotations")

        stage_input: CreateStageInput = {
            "name": "My Data Stage",
            "triggers": [
                {
                    "name": "my-trigger",
                    "transformationName": "text-extract",
                    "destinationType": "DataPlatform:Repository",
                    "repositoryId": "repo-123",
                }
            ],
            "retentionPolicy": {
                "retentionPeriod": 30  # days
            },
        }

        # stage = await client.v1.stages.create(**stage_input)
        p.info("Type-safe stage input prepared (not executed)")
        p.info(f"Name: {stage_input['name']}", indent=1)
        p.info(f"Triggers: {len(stage_input.get('triggers', []))}", indent=1)

        # Example 2: Create a repository with typing
        p.section(2, 5, "Creating a repository with type annotations")

        repo_input: CreateRepositoryInput = {
            "name": "My Repository",
            "media_type": MediaType.JSONLINES,
            "modality": Modality.TEXT,
            "mutable": True,
        }

        # repo = await client.v1.repositories.create(**repo_input)
        p.info("Type-safe repository input prepared (not executed)")
        p.info(f"Name: {repo_input['name']}", indent=1)
        p.info(f"Media Type: {repo_input['media_type'].value}", indent=1)
        p.info(f"Modality: {repo_input['modality'].value}", indent=1)

        # Example 3: Create a connector with SharePoint source
        p.section(3, 5, "Creating a connector with type annotations")

        sharepoint_source: SharepointSourceConfig = {
            "driveId": "drive-123",
            "folderId": "folder-456",
            "fileIds": ["file1", "file2"],
        }

        connector_input: CreateConnectorInput = {
            "connectionId": "conn-uuid-here",
            "name": "SharePoint Sync",
            "connector_mode": "SYNC",
            "stage_id": "stage-uuid-here",
            "source": {"type": "sharepoint", "configuration": sharepoint_source},
            "destination": {"type": "DataPlatform:SearchStore", "searchStore": "search-store-id"},
        }

        # connector = await client.v1.connectors.create(connector_data=connector_input)
        p.info("Type-safe connector input prepared (not executed)")
        p.info(f"Name: {connector_input['name']}", indent=1)
        p.info(f"Mode: {connector_input['connector_mode']}", indent=1)
        p.info(f"Source Type: {connector_input['source']['type']}", indent=1)

        # Example 4: List stages with type-safe access
        p.section(4, 5, "Listing stages with type hints")

        stages_response = await client.v1.stages.list(page=0, size=10)

        # Type hints help with autocomplete and type checking
        total_stages: int = stages_response["total"]
        stages = stages_response["stages"]

        p.success(f"Found {total_stages} total stages")

        for stage in stages[:3]:  # Show first 3
            p.info(f"Stage: {stage['name']}", indent=1)
            p.info(f"ID: {stage['stageId']}", indent=2)
            p.info(f"Created: {stage['createdAt']}", indent=2)
            p.info(f"Files: {stage['filesCount']}", indent=2)

            # Access triggers with type safety
            for trigger in stage.get("triggers", []):
                p.info(f"Trigger: {trigger['name']}", indent=2)

        # Example 5: List files with type-safe access
        p.section(5, 5, "Listing files in a stage")

        if stages:
            stage_id = stages[0]["stageId"]
            files_response = await client.v1.files.list(stage_id=stage_id, page=0, size=50)

            p.success(f"Found {files_response['total']} files")

            for file in files_response.get("files", [])[:3]:  # Show first 3
                p.info(f"File: {file.get('name', 'unnamed')}", indent=1)
                p.info(f"Size: {file['size']} bytes", indent=2)
                p.info(f"Type: {file['mediaType']}", indent=2)


if __name__ == "__main__":
    asyncio.run(main())
