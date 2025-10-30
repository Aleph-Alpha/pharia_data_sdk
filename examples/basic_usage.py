"""
Basic usage examples for the Pharia SDK.

This example demonstrates the most common operations:
- Creating a client
- Listing stages, repositories, and connectors
- Getting specific resources
- Listing files in a stage
"""

import asyncio

from helpers import ExamplePrinter

from pharia_sdk import Client


async def main():
    """Basic SDK usage examples."""

    # Client reads credentials from environment variables:
    # - PHARIA_DATA_API_BASE_URL
    # - PHARIA_API_KEY
    client = Client()

    with ExamplePrinter("Basic Usage Examples") as p:
        # Example 1: List all stages
        p.section(1, 5, "Listing stages")
        stages_response = await client.stages.list(page=0, size=10)
        p.success(f"Found {stages_response['total']} total stages")

        if stages_response.get("stages"):
            for stage in stages_response["stages"][:3]:  # Show first 3
                p.info(f"{stage['name']} (ID: {stage['stageId']})", indent=1)
                p.info(f"Files: {stage['filesCount']}", indent=2)

        # Example 2: List repositories
        p.section(2, 5, "Listing repositories")
        repos_response = await client.repositories.list(page=0, size=10)
        p.success(f"Found {repos_response['total']} total repositories")

        if repos_response.get("repositories"):
            for repo in repos_response["repositories"][:3]:  # Show first 3
                p.info(f"{repo['name']} (ID: {repo['repositoryId']})", indent=1)
                p.info(f"Modality: {repo.get('modality', 'N/A')}", indent=2)

        # Example 3: List connectors
        p.section(3, 5, "Listing connectors")
        connectors_response = await client.connectors.list(page=0, size=10)
        p.success(f"Found {connectors_response['total']} total connectors")

        if connectors_response.get("connectors"):
            for connector in connectors_response["connectors"][:3]:  # Show first 3
                p.info(f"{connector['name']} (ID: {connector['connectorId']})", indent=1)
                p.info(f"Mode: {connector.get('connectorMode', 'N/A')}", indent=2)

        # Example 4: Get a specific stage
        p.section(4, 5, "Getting a specific stage")
        if stages_response.get("stages") and len(stages_response["stages"]) > 0:
            stage_id = stages_response["stages"][0]["stageId"]
            stage = await client.stages.get(stage_id)
            p.success(
                f"Retrieved stage: {stage['name']}",
                {
                    "ID": stage["stageId"],
                    "Created": stage["createdAt"],
                    "Files": stage["filesCount"],
                },
            )
        else:
            p.warning("No stages found to demonstrate get operation")

        # Example 5: List files in a stage
        p.section(5, 5, "Listing files in a stage")
        if stages_response.get("stages") and len(stages_response["stages"]) > 0:
            stage_id = stages_response["stages"][0]["stageId"]
            files_response = await client.files.list(stage_id, page=0, size=10)
            p.success(f"Found {files_response['total']} files in stage")

            if files_response.get("files"):
                for file in files_response["files"][:3]:  # Show first 3
                    p.info(f"{file.get('name', 'unnamed')}", indent=1)
                    p.info(f"Size: {file['size']} bytes, Type: {file['mediaType']}", indent=2)
        else:
            p.warning("No stages found to demonstrate file listing")


if __name__ == "__main__":
    asyncio.run(main())
