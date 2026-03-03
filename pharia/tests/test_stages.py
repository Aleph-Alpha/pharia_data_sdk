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


@pytest.mark.asyncio
async def test_batch_stages_has_files_and_runs():
    """Test batch stages expose .files and .runs with .list() methods."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    batch = client.v1.stages("id1", "id2")
    assert hasattr(batch, "files")
    assert hasattr(batch, "runs")

    batch_files = batch.files
    assert hasattr(batch_files, "list")
    assert batch_files.stage_ids == ["id1", "id2"]

    batch_runs = batch.runs
    assert hasattr(batch_runs, "list")
    assert batch_runs.stage_ids == ["id1", "id2"]


@pytest.mark.asyncio
async def test_batch_search_stores_has_documents():
    """Test batch search stores expose .documents with .list() method."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    batch = client.v1.search_stores("ss1", "ss2")
    assert hasattr(batch, "documents")

    batch_docs = batch.documents
    assert hasattr(batch_docs, "list")
    assert batch_docs.search_store_ids == ["ss1", "ss2"]


@pytest.mark.asyncio
async def test_batch_repositories_has_datasets():
    """Test batch repositories expose .datasets with .list() method."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    batch = client.v1.repositories("r1", "r2")
    assert hasattr(batch, "datasets")

    batch_datasets = batch.datasets
    assert hasattr(batch_datasets, "list")
    assert batch_datasets.repository_ids == ["r1", "r2"]


@pytest.mark.asyncio
async def test_batch_connectors_has_files_and_runs():
    """Test batch connectors expose .files and .runs with .list() methods."""
    client = Client(base_url="https://api.example.com", api_key="test-key")

    batch = client.v1.connectors("c1", "c2")
    assert hasattr(batch, "files")
    assert hasattr(batch, "runs")

    batch_files = batch.files
    assert hasattr(batch_files, "list")
    assert batch_files.connector_ids == ["c1", "c2"]

    batch_runs = batch.runs
    assert hasattr(batch_runs, "list")
    assert batch_runs.connector_ids == ["c1", "c2"]
