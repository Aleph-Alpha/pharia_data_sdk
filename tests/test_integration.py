"""
Integration tests for Pharia SDK - testing against live API.
"""

import asyncio
import os

import pytest

from pharia_sdk import Client


@pytest.mark.asyncio
async def test_all_get_endpoints():
    """Test all GET endpoints against the staging API."""

    # Get credentials from environment variables
    api_key = os.getenv("PHARIA_API_KEY")
    base_url = os.getenv(
        "PHARIA_BASE_URL", "https://pharia-data-api.stage.product.pharia.com/api/v1"
    )

    if not api_key:
        pytest.skip("PHARIA_API_KEY environment variable not set")

    client = Client(base_url=base_url, api_key=api_key)

    # Test 1: List Stages
    stages = await client.stages.list(page=0, size=10)
    assert "total" in stages
    assert "stages" in stages

    # Test 2: List Repositories
    repos = await client.repositories.list(page=0, size=10)
    assert "total" in repos
    assert "repositories" in repos

    # Test 3: List Connectors
    connectors = await client.connectors.list(page=0, size=10)
    assert "total" in connectors
    assert "connectors" in connectors

    # Test 4: Get a specific stage (if any exist)
    if stages.get("stages") and len(stages["stages"]) > 0:
        stage_id = stages["stages"][0]["stageId"]
        stage = await client.stages.get(stage_id)
        assert stage is not None
        assert "stageId" in stage

    # Test 5: List files in a stage (if any exist)
    if stages.get("stages") and len(stages["stages"]) > 0:
        stage_id = stages["stages"][0]["stageId"]
        files = await client.files.list(stage_id, page=0, size=10)
        assert "total" in files


if __name__ == "__main__":
    asyncio.run(test_all_get_endpoints())
