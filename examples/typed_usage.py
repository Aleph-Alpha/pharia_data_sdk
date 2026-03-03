"""
Example: Using the Pharia SDK with proper type annotations.

This example demonstrates how to use the SDK with TypedDict models
for better IDE autocomplete and type checking.
"""

import asyncio
import uuid

from examples.helpers import ExamplePrinter
from pharia import Client
from pharia import CreateConnectorInput
from pharia import CreateRepositoryInput
from pharia import CreateStageInput
from pharia import DestinationType
from pharia import MediaType
from pharia import Modality
from pharia import SharepointSourceConfig
from pharia import TransformationName
from pharia import TriggerInput


async def main():
    """Example showing how to use the SDK with type hints."""

    # Client reads credentials from environment variables:
    # - PHARIA_DATA_API_BASE_URL
    # - PHARIA_API_KEY
    client = Client()

    created_stage_id: str | None = None
    created_repo_id: str | None = None

    with ExamplePrinter("Type-Safe Usage Examples") as p:
        # Example 1: Create a stage with proper typing
        p.section(1, 5, "Creating a stage with type annotations")

        trigger: TriggerInput = {
            "name": "my-trigger",
            "transformation_name": TransformationName.DOCUMENT_TO_TEXT,
            "destination_type": DestinationType.DATA_PLATFORM_REPOSITORY,
            "repository_id": "repo-123",
        }
        stage_input: CreateStageInput = {
            "name": f"Example - Typed Stage-{uuid.uuid4()}",
            "triggers": [trigger],
            "retention_policy": {"retentionPeriod": 30},
        }

        stage = await client.v1.stages.create(**stage_input)
        created_stage_id = stage["stageId"]
        p.success(f"Created stage: {stage['name']}", {"ID": created_stage_id})

        # Example 2: Create a repository with typing
        p.section(2, 5, "Creating a repository with type annotations")

        repo_input: CreateRepositoryInput = {
            "name": f"Example - Typed Repo-{uuid.uuid4()}",
            "media_type": MediaType.JSONLINES,
            "modality": Modality.TEXT,
            "mutable": True,
        }

        repo = await client.v1.repositories.create(**repo_input)
        created_repo_id = repo["repositoryId"]
        p.success(f"Created repository: {repo['name']}", {"ID": created_repo_id})

        # Example 3: Create a connector with SharePoint source
        p.section(3, 5, "Creating a connector with type annotations")

        sharepoint_source: SharepointSourceConfig = {
            "driveId": "drive-123",
            "folderId": "folder-456",
            "fileIds": ["file1", "file2"],
        }

        connector_input: CreateConnectorInput = {
            "connection_id": "conn-uuid-here",
            "name": "SharePoint Sync",
            "connector_mode": "SYNC",
            "stage_id": created_stage_id,
            "source": {"type": "sharepoint", "configuration": sharepoint_source},
            "destination": {"type": "DataPlatform:SearchStore", "searchStore": "search-store-id"},
        }

        try:
            connector = await client.v1.connectors.create(**connector_input)
            p.success(f"Created connector: {connector['name']}", {"ID": connector["id"]})
        except Exception as e:
            p.error(f"FAILED (requires valid SharePoint connection): {e}")

        # Example 4: List stages with type-safe access
        p.section(4, 5, "Listing stages with type hints")

        stages_response = await client.v1.stages.list(page=0, size=10)

        total_stages: int = stages_response["total"]
        stages = stages_response["stages"]

        p.success(f"Found {total_stages} total stages")

        for stage in stages[:3]:  # Show first 3
            p.info(f"Stage: {stage['name']}", indent=1)
            p.info(f"ID: {stage['stageId']}", indent=2)
            p.info(f"Created: {stage['createdAt']}", indent=2)
            p.info(f"Files: {stage['filesCount']}", indent=2)

            for trigger in stage["triggers"]:
                p.info(f"Trigger: {trigger['name']}", indent=2)

        # Example 5: List files in a stage (fluent API)
        p.section(5, 5, "Listing files in a stage")

        if stages:
            stage_id = stages[0]["stageId"]
            files_response = await client.v1.stages(stage_id).files.list(page=0, size=50)

            p.success(f"Found {files_response['total']} files")

            for file in files_response.get("files", [])[:3]:  # Show first 3
                p.info(f"File: {file.get('name', 'unnamed')}", indent=1)
                p.info(f"Size: {file['size']} bytes", indent=2)
                p.info(f"Type: {file['mediaType']}", indent=2)

        # Cleanup
        p.info("\nCleaning up...")
        if created_stage_id:
            await client.v1.stages(created_stage_id).delete()
            p.success(f"Deleted stage: {created_stage_id}")
        if created_repo_id:
            await client.v1.repositories(created_repo_id).delete()
            p.success(f"Deleted repository: {created_repo_id}")


if __name__ == "__main__":
    asyncio.run(main())
