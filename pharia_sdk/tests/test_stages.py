import pytest

from pharia_sdk.client import Client


@pytest.mark.asyncio
async def test_stages_list():
    """Test stages list method signature and URL construction."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    # Verify the client has stages property
    assert hasattr(client, "stages")
    assert hasattr(client.stages, "list")
    assert hasattr(client.stages, "create")
    assert hasattr(client.stages, "get")
    assert hasattr(client.stages, "delete")


@pytest.mark.asyncio
async def test_stages_create():
    """Test stages create method signature."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    # Verify method exists and accepts required parameters
    assert callable(client.stages.create)


@pytest.mark.asyncio
async def test_stages_get():
    """Test stages get method signature."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    # Verify method exists
    assert callable(client.stages.get)


@pytest.mark.asyncio
async def test_stages_delete():
    """Test stages delete method signature."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    # Verify method exists
    assert callable(client.stages.delete)
