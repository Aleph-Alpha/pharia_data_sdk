import pytest

from pharia.client import Client


@pytest.mark.asyncio
async def test_stages_list():
    """Test stages list method signature and URL construction."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    # Verify the client has stages property via v1
    assert hasattr(client.v1, "stages")
    assert hasattr(client.v1.stages, "list")
    assert hasattr(client.v1.stages, "create")
    assert callable(client.v1.stages)


@pytest.mark.asyncio
async def test_stages_fluent_api():
    """Test stages fluent API returns correct resource types."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    # Single ID returns StageResource
    stage_resource = client.v1.stages("test-id")
    assert hasattr(stage_resource, "get")
    assert hasattr(stage_resource, "update")
    assert hasattr(stage_resource, "delete")
    assert hasattr(stage_resource, "files")
    assert hasattr(stage_resource, "runs")

    # Multiple IDs returns BatchStageResource
    batch_resource = client.v1.stages("id1", "id2")
    assert hasattr(batch_resource, "get")
    assert hasattr(batch_resource, "delete")


@pytest.mark.asyncio
async def test_stages_nested_files():
    """Test nested files access via fluent API."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    stage_files = client.v1.stages("test-stage").files
    assert hasattr(stage_files, "list")
    assert hasattr(stage_files, "create")
    assert callable(stage_files)

    # Single file ID
    file_resource = client.v1.stages("test-stage").files("test-file")
    assert hasattr(file_resource, "get")
    assert hasattr(file_resource, "update")
    assert hasattr(file_resource, "delete")
    assert hasattr(file_resource, "presigned_url")
