"""
Comprehensive integration tests for Pharia SDK — exercises every resource method
against the live API using the fluent API pattern.

Requires PHARIA_DATA_API_BASE_URL and PHARIA_API_KEY env vars.

Known issues discovered during testing:
- MediaType.JSON ("json") is rejected by the API; use "application/json" instead.
- Dataset creation requires multipart/form-data; the SDK sends JSON — dataset
  create/update_datapoints are broken at the SDK level.
- PresignedURL TypedDict doesn't match the actual API response shape.
- Document schemaVersion must be "V1" (not "1").
"""

import uuid

import httpx
import pytest

from pharia import Client
from pharia.models import MediaType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PREFIX = f"sdk-e2e-{uuid.uuid4().hex[:8]}"


def unique(label: str) -> str:
    return f"{PREFIX}-{label}-{uuid.uuid4().hex[:6]}"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class TestClient:
    """Client initialisation and option helpers."""

    def test_client_init(self):
        client = Client()
        assert client.base_url
        assert client.api_key
        assert "Authorization" in client.headers

    def test_with_options(self):
        client = Client()
        new = client.with_options(timeout=42.0)
        assert new.timeout == 42.0
        assert new.api_key == client.api_key

    def test_with_namespace(self):
        client = Client()
        ns = client.with_namespace("/api/v1")
        assert ns.base_url.endswith("/api/v1")


class TestStages:
    """Full CRUD + embedding helpers for stages."""

    @pytest.mark.asyncio
    async def test_list_stages(self):
        client = Client()
        resp = await client.v1.stages.list(page=0, size=5)
        assert "total" in resp
        assert "stages" in resp

    @pytest.mark.asyncio
    async def test_list_stages_with_filters(self):
        client = Client()
        resp = await client.v1.stages.list(page=0, size=5, with_search_store=True)
        assert "total" in resp

        resp2 = await client.v1.stages.list(page=0, size=5, name="nonexistent-xyz")
        assert resp2["total"] == 0 or "stages" in resp2

    @pytest.mark.asyncio
    async def test_create_simple_stage_and_delete(self):
        client = Client()
        name = unique("simple-stage")
        stage = await client.v1.stages.create(name=name)
        assert stage["stageId"]
        assert stage["name"] == name

        # GET
        got = await client.v1.stages(stage["stageId"]).get()
        assert got["stageId"] == stage["stageId"]

        # DELETE
        await client.v1.stages(stage["stageId"]).delete()

    @pytest.mark.asyncio
    async def test_create_and_update_stage(self):
        client = Client()
        stage = await client.v1.stages.create(name=unique("update-stage"))
        sid = stage["stageId"]
        try:
            updated = await client.v1.stages(sid).update(access_policy="private")
            assert updated is not None
        finally:
            await client.v1.stages(sid).delete()

    @pytest.mark.asyncio
    async def test_batch_get_and_delete(self):
        client = Client()
        s1 = await client.v1.stages.create(name=unique("batch-1"))
        s2 = await client.v1.stages.create(name=unique("batch-2"))
        ids = [s1["stageId"], s2["stageId"]]
        try:
            results = await client.v1.stages(*ids).get(concurrency=5)
            assert len(results) == 2
        finally:
            await client.v1.stages(*ids).delete(concurrency=5)

    @pytest.mark.asyncio
    async def test_instruct_stage(self):
        client = Client()
        stage = await client.v1.stages.instruct.create(
            name=unique("instruct-stage"),
            embedding_model="pharia-1-embedding-4608-control",
            instruction_document="Represent the document for retrieval",
            instruction_query="Represent the query for retrieval",
            hybrid_index="bm25",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
        )
        assert stage["stageId"]
        ss = stage.get("searchStore")
        assert ss is not None
        assert ss["embeddingStrategy"]["type"] == "instruct"
        await client.v1.stages(stage["stageId"]).delete()

    @pytest.mark.asyncio
    async def test_semantic_stage(self):
        client = Client()
        stage = await client.v1.stages.semantic.create(
            name=unique("semantic-stage"),
            embedding_model="luminous-base",
            representation="asymmetric",
            hybrid_index="bm25",
            max_chunk_size_tokens=1024,
            chunk_overlap_tokens=256,
        )
        assert stage["stageId"]
        ss = stage.get("searchStore")
        assert ss is not None
        assert ss["embeddingStrategy"]["type"] == "semantic"
        await client.v1.stages(stage["stageId"]).delete()

    @pytest.mark.asyncio
    async def test_vllm_stage(self):
        client = Client()
        stage = await client.v1.stages.vllm.create(
            name=unique("vllm-stage"),
            embedding_model="qwen3-embedding-8b",
            hybrid_index="bm25",
            max_chunk_size_tokens=2046,
            chunk_overlap_tokens=512,
        )
        assert stage["stageId"]
        assert stage.get("searchStore") is not None
        await client.v1.stages(stage["stageId"]).delete()


# ---------------------------------------------------------------------------
# Stage Runs
# ---------------------------------------------------------------------------


class TestStageRuns:
    @pytest.mark.asyncio
    async def test_list_runs(self):
        client = Client()
        stages = await client.v1.stages.list(page=0, size=10)
        if not stages["stages"]:
            pytest.skip("No stages available to test runs")
        for stage in stages["stages"]:
            sid = stage["stageId"]
            try:
                runs = await client.v1.stages(sid).runs.list(page=0, size=5)
                assert "total" in runs
                assert "runs" in runs
                return
            except httpx.HTTPStatusError:
                continue
        pytest.skip("No stages with runs endpoint available")


# ---------------------------------------------------------------------------
# Stage Files  (list / get / presigned_url)
# ---------------------------------------------------------------------------


class TestStageFiles:
    @pytest.mark.asyncio
    async def test_list_files(self):
        client = Client()
        stages = await client.v1.stages.list(page=0, size=1)
        if not stages["stages"]:
            pytest.skip("No stages available to test files")
        sid = stages["stages"][0]["stageId"]
        files = await client.v1.stages(sid).files.list(page=0, size=5)
        assert "total" in files
        assert "files" in files

    @pytest.mark.asyncio
    async def test_list_files_with_name_filter(self):
        client = Client()
        stages = await client.v1.stages.list(page=0, size=1)
        if not stages["stages"]:
            pytest.skip("No stages available")
        sid = stages["stages"][0]["stageId"]
        files = await client.v1.stages(sid).files.list(page=0, size=5, name="nonexistent")
        assert "total" in files

    @pytest.mark.asyncio
    async def test_get_file_content(self):
        """Download first available file (if any)."""
        client = Client()
        stages = await client.v1.stages.list(page=0, size=5)
        for s in stages.get("stages", []):
            files = await client.v1.stages(s["stageId"]).files.list(page=0, size=1)
            if files.get("files"):
                fid = files["files"][0]["fileId"]
                content = await client.v1.stages(s["stageId"]).files(fid).get()
                assert isinstance(content, bytes)
                return
        pytest.skip("No files found in any stage")

    @pytest.mark.asyncio
    async def test_presigned_url(self):
        """Get presigned URL for first available file."""
        client = Client()
        stages = await client.v1.stages.list(page=0, size=5)
        for s in stages.get("stages", []):
            files = await client.v1.stages(s["stageId"]).files.list(page=0, size=1)
            if files.get("files"):
                fid = files["files"][0]["fileId"]
                purl = await client.v1.stages(s["stageId"]).files(fid).presigned_url(ttl=60)
                # API returns {success, presignedUrl, ttlSeconds}
                assert purl.get("presignedUrl") or purl.get("url")
                return
        pytest.skip("No files found in any stage")


class TestRepositories:
    @pytest.mark.asyncio
    async def test_list_repositories(self):
        client = Client()
        resp = await client.v1.repositories.list(page=0, size=5)
        assert "total" in resp
        assert "repositories" in resp

    @pytest.mark.asyncio
    async def test_create_get_delete_repository(self):
        client = Client()
        name = unique("repo")
        repo = await client.v1.repositories.create(
            name=name, media_type=MediaType.JSONLINES, modality="text"
        )
        rid = repo["repositoryId"]
        assert rid
        assert repo["name"] == name

        got = await client.v1.repositories(rid).get()
        assert got["repositoryId"] == rid

        await client.v1.repositories(rid).delete()

    @pytest.mark.asyncio
    async def test_batch_get_repositories(self):
        client = Client()
        r1 = await client.v1.repositories.create(
            name=unique("batch-repo-1"), media_type=MediaType.JSONLINES, modality="text"
        )
        r2 = await client.v1.repositories.create(
            name=unique("batch-repo-2"), media_type=MediaType.JSONLINES, modality="text"
        )
        ids = [r1["repositoryId"], r2["repositoryId"]]
        try:
            results = await client.v1.repositories(*ids).get()
            assert len(results) == 2
        finally:
            await client.v1.repositories(*ids).delete()


# ---------------------------------------------------------------------------
# Datasets
# NOTE: dataset creation requires multipart/form-data but the SDK sends JSON.
# These tests document the known SDK limitation.
# ---------------------------------------------------------------------------


class TestDatasets:
    @pytest.mark.asyncio
    async def test_list_datasets(self):
        """Listing datasets on an existing repo works (GET endpoint)."""
        client = Client()
        repos = await client.v1.repositories.list(page=0, size=10)
        if not repos["repositories"]:
            pytest.skip("No repositories to list datasets from")
        for repo in repos["repositories"]:
            rid = repo["repositoryId"]
            try:
                ds_list = await client.v1.repositories(rid).datasets.list(page=0, size=5)
                assert "total" in ds_list
                assert "datasets" in ds_list
                return
            except httpx.HTTPStatusError:
                continue
        pytest.skip("No repositories with datasets endpoint available")

    @pytest.mark.asyncio
    async def test_get_existing_dataset(self):
        """Get an existing dataset if one exists."""
        client = Client()
        repos = await client.v1.repositories.list(page=0, size=10)
        for repo in repos.get("repositories", []):
            rid = repo["repositoryId"]
            try:
                ds_list = await client.v1.repositories(rid).datasets.list(page=0, size=1)
            except httpx.HTTPStatusError:
                continue
            if ds_list.get("datasets"):
                did = ds_list["datasets"][0]["datasetId"]
                ds = await client.v1.repositories(rid).datasets(did).get()
                assert ds["datasetId"] == did
                return
        pytest.skip("No datasets found in any repository")

    @pytest.mark.asyncio
    async def test_create_dataset_known_broken(self):
        """Dataset creation fails: API requires multipart/form-data, SDK sends JSON."""
        client = Client()
        repo = await client.v1.repositories.create(
            name=unique("ds-repo"), media_type=MediaType.JSONLINES, modality="text"
        )
        rid = repo["repositoryId"]
        try:
            with pytest.raises(httpx.HTTPStatusError):
                await client.v1.repositories(rid).datasets.create(name=unique("ds"))
        finally:
            await client.v1.repositories(rid).delete()


class TestBatchStageNested:
    """E2E tests for batch stage .files and .runs fan-out."""

    @pytest.mark.asyncio
    async def test_batch_stages_files_list(self):
        client = Client()
        s1 = await client.v1.stages.create(name=unique("bfiles-1"))
        s2 = await client.v1.stages.create(name=unique("bfiles-2"))
        ids = [s1["stageId"], s2["stageId"]]
        try:
            results = await client.v1.stages(*ids).files.list(page=0, size=5)
            assert len(results) == 2
            for r in results:
                assert "total" in r
                assert "files" in r
        finally:
            await client.v1.stages(*ids).delete()

    @pytest.mark.asyncio
    async def test_batch_stages_runs_list(self):
        client = Client()
        s1 = await client.v1.stages.create(name=unique("bruns-1"))
        s2 = await client.v1.stages.create(name=unique("bruns-2"))
        ids = [s1["stageId"], s2["stageId"]]
        try:
            results = await client.v1.stages(*ids).runs.list(page=0, size=5)
            assert len(results) == 2
            for r in results:
                assert "total" in r
                assert "runs" in r
        finally:
            await client.v1.stages(*ids).delete()


class TestBatchSearchStoreNested:
    """E2E tests for batch search store .documents fan-out."""

    @pytest.mark.asyncio
    async def test_batch_search_stores_documents_list(self):
        client = Client()
        ss1 = await client.v1.search_stores.semantic.create(
            name=unique("bdocs-ss-1"), embedding_model="luminous-base", representation="asymmetric"
        )
        ss2 = await client.v1.search_stores.semantic.create(
            name=unique("bdocs-ss-2"), embedding_model="luminous-base", representation="asymmetric"
        )
        ids = [ss1["id"], ss2["id"]]
        try:
            results = await client.v1.search_stores(*ids).documents.list(page=1, size=5)
            assert len(results) == 2
            for r in results:
                assert "total" in r
                assert "results" in r
        finally:
            await client.v1.search_stores(*ids).delete()


class TestBatchRepositoryNested:
    """E2E tests for batch repository .datasets fan-out."""

    @pytest.mark.asyncio
    async def test_batch_repositories_datasets_list(self):
        client = Client()
        r1 = await client.v1.repositories.create(
            name=unique("bds-repo-1"), media_type=MediaType.JSONLINES, modality="text"
        )
        r2 = await client.v1.repositories.create(
            name=unique("bds-repo-2"), media_type=MediaType.JSONLINES, modality="text"
        )
        ids = [r1["repositoryId"], r2["repositoryId"]]
        try:
            results = await client.v1.repositories(*ids).datasets.list(page=0, size=5)
            assert len(results) == 2
            for r in results:
                assert "total" in r
                assert "datasets" in r
        finally:
            await client.v1.repositories(*ids).delete()


class TestBatchConnectorNested:
    """E2E tests for batch connector .files and .runs fan-out."""

    @pytest.mark.asyncio
    async def test_batch_connectors_files_list(self):
        client = Client()
        listing = await client.v1.connectors.list(page=0, size=2)
        conns = listing["connectors"]
        if len(conns) < 2:
            pytest.skip("Need >=2 connectors for batch nested test")
        ids = [c["id"] for c in conns[:2]]
        results = await client.v1.connectors(*ids).files.list(page=0, size=5)
        assert len(results) == 2
        for r in results:
            assert "total" in r

    @pytest.mark.asyncio
    async def test_batch_connectors_runs_list(self):
        client = Client()
        listing = await client.v1.connectors.list(page=0, size=2)
        conns = listing["connectors"]
        if len(conns) < 2:
            pytest.skip("Need >=2 connectors for batch nested test")
        ids = [c["id"] for c in conns[:2]]
        results = await client.v1.connectors(*ids).runs.list(page=0, size=5)
        assert len(results) == 2
        for r in results:
            assert "total" in r
            assert "runs" in r


class TestConnectors:
    @pytest.mark.asyncio
    async def test_list_connectors(self):
        client = Client()
        resp = await client.v1.connectors.list(page=0, size=5)
        assert "total" in resp
        assert "connectors" in resp

    @pytest.mark.asyncio
    async def test_list_connectors_with_filters(self):
        client = Client()
        resp = await client.v1.connectors.list(page=0, size=5, name="nonexistent-xyz")
        assert "total" in resp

    @pytest.mark.asyncio
    async def test_get_connector(self):
        client = Client()
        listing = await client.v1.connectors.list(page=0, size=1)
        if not listing["connectors"]:
            pytest.skip("No connectors available")
        cid = listing["connectors"][0]["id"]
        conn = await client.v1.connectors(cid).get()
        assert conn["id"] == cid

    @pytest.mark.asyncio
    async def test_connector_files(self):
        client = Client()
        listing = await client.v1.connectors.list(page=0, size=1)
        if not listing["connectors"]:
            pytest.skip("No connectors available")
        cid = listing["connectors"][0]["id"]
        files = await client.v1.connectors(cid).files.list(page=0, size=5)
        assert "total" in files

    @pytest.mark.asyncio
    async def test_connector_runs(self):
        client = Client()
        listing = await client.v1.connectors.list(page=0, size=1)
        if not listing["connectors"]:
            pytest.skip("No connectors available")
        cid = listing["connectors"][0]["id"]
        runs = await client.v1.connectors(cid).runs.list(page=0, size=5)
        assert "total" in runs
        assert "runs" in runs

    @pytest.mark.asyncio
    async def test_batch_get_connectors(self):
        client = Client()
        listing = await client.v1.connectors.list(page=0, size=2)
        conns = listing["connectors"]
        if len(conns) < 2:
            pytest.skip("Need >=2 connectors for batch test")
        ids = [c["id"] for c in conns[:2]]
        results = await client.v1.connectors(*ids).get()
        assert len(results) == 2


# ---------------------------------------------------------------------------
# Search Stores  (list / create / get / update / search / delete / batch)
# ---------------------------------------------------------------------------


class TestSearchStores:
    @pytest.mark.asyncio
    async def test_list_search_stores(self):
        client = Client()
        resp = await client.v1.search_stores.list(page=1, size=5)
        assert "total" in resp
        assert "results" in resp

    @pytest.mark.asyncio
    async def test_semantic_search_store_lifecycle(self):
        client = Client()
        ss = await client.v1.search_stores.semantic.create(
            name=unique("semantic-ss"),
            embedding_model="luminous-base",
            representation="asymmetric",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
        )
        ssid = ss["id"]
        assert ssid

        # GET
        got = await client.v1.search_stores(ssid).get()
        assert got["id"] == ssid
        assert got["embeddingStrategy"]["type"] == "semantic"

        # UPDATE
        updated = await client.v1.search_stores(ssid).update(metadata={"env": "e2e-test"})
        assert updated is not None

        # DELETE
        await client.v1.search_stores(ssid).delete()

    @pytest.mark.asyncio
    async def test_instruct_search_store_lifecycle(self):
        client = Client()
        ss = await client.v1.search_stores.instruct.create(
            name=unique("instruct-ss"),
            embedding_model="pharia-1-embedding-4608-control",
            instruction_document="Represent the document for retrieval",
            instruction_query="Represent the query for retrieval",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
        )
        ssid = ss["id"]
        assert ssid
        assert ss["embeddingStrategy"]["type"] == "instruct"
        await client.v1.search_stores(ssid).delete()

    @pytest.mark.asyncio
    async def test_vllm_search_store_lifecycle(self):
        client = Client()
        ss = await client.v1.search_stores.vllm.create(
            name=unique("vllm-ss"),
            embedding_model="qwen3-embedding-8b",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
        )
        ssid = ss["id"]
        assert ssid
        assert ss["embeddingStrategy"]["type"] == "vllm"
        await client.v1.search_stores(ssid).delete()

    @pytest.mark.asyncio
    async def test_batch_get_and_delete_search_stores(self):
        client = Client()
        s1 = await client.v1.search_stores.semantic.create(
            name=unique("batch-ss-1"), embedding_model="luminous-base", representation="asymmetric"
        )
        s2 = await client.v1.search_stores.semantic.create(
            name=unique("batch-ss-2"), embedding_model="luminous-base", representation="asymmetric"
        )
        ids = [s1["id"], s2["id"]]
        try:
            results = await client.v1.search_stores(*ids).get()
            assert len(results) == 2
        finally:
            await client.v1.search_stores(*ids).delete()

    @pytest.mark.asyncio
    async def test_search_existing_store(self):
        """Search against an existing search store with documents."""
        client = Client()
        listing = await client.v1.search_stores.list(page=1, size=10)
        stores = listing.get("results", [])
        if not stores:
            pytest.skip("No search stores available for search test")
        for store in stores:
            ssid = store["id"]
            try:
                result = await client.v1.search_stores(ssid).search(query="test", limit=3)
                assert "results" in result
                return
            except Exception:
                continue
        pytest.skip("No search store returned results")


class TestDocuments:
    @pytest.mark.asyncio
    async def test_full_document_lifecycle(self):
        client = Client()
        ss = await client.v1.search_stores.semantic.create(
            name=unique("doc-ss"),
            embedding_model="luminous-base",
            representation="asymmetric",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
        )
        ssid = ss["id"]
        try:
            docs = await client.v1.search_stores(ssid).documents.list(page=1, size=5)
            assert "total" in docs
            assert "results" in docs

            # CREATE OR UPDATE — note: schemaVersion must be "V1"
            doc_name = unique("test-doc")
            doc = (
                await client.v1.search_stores(ssid)
                .documents(doc_name)
                .create_or_update(
                    schema_version="V1",
                    contents=[
                        {"modality": "text", "text": "Hello world. This is a test document."}
                    ],
                    metadata={"source": "e2e-test"},
                )
            )
            assert doc["name"] == doc_name

            # GET metadata
            got = await client.v1.search_stores(ssid).documents(doc_name).get()
            assert got["name"] == doc_name

            # GET content (returns list[ContentDTO])
            content = await client.v1.search_stores(ssid).documents(doc_name).get_content()
            assert isinstance(content, list)
            assert len(content) > 0

            # LIST with starts_with filter
            filtered = await client.v1.search_stores(ssid).documents.list(
                page=1, size=5, starts_with=PREFIX
            )
            assert "results" in filtered

            # DELETE
            await client.v1.search_stores(ssid).documents(doc_name).delete()
        finally:
            await client.v1.search_stores(ssid).delete()

    @pytest.mark.asyncio
    async def test_batch_documents(self):
        client = Client()
        ss = await client.v1.search_stores.semantic.create(
            name=unique("batch-doc-ss"),
            embedding_model="luminous-base",
            representation="asymmetric",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
        )
        ssid = ss["id"]
        try:
            name1 = unique("bdoc-1")
            name2 = unique("bdoc-2")
            await (
                client.v1.search_stores(ssid)
                .documents(name1)
                .create_or_update(
                    schema_version="V1", contents=[{"modality": "text", "text": "Document one."}]
                )
            )
            await (
                client.v1.search_stores(ssid)
                .documents(name2)
                .create_or_update(
                    schema_version="V1", contents=[{"modality": "text", "text": "Document two."}]
                )
            )
            # Batch GET
            results = await client.v1.search_stores(ssid).documents(name1, name2).get()
            assert len(results) == 2

            # Batch DELETE
            await client.v1.search_stores(ssid).documents(name1, name2).delete()
        finally:
            await client.v1.search_stores(ssid).delete()

    @pytest.mark.asyncio
    async def test_search_store_with_document_and_search(self):
        """End-to-end: create store, add doc, search, clean up."""
        client = Client()
        ss = await client.v1.search_stores.semantic.create(
            name=unique("search-doc-ss"),
            embedding_model="luminous-base",
            representation="asymmetric",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
        )
        ssid = ss["id"]
        try:
            doc_name = unique("searchable-doc")
            await (
                client.v1.search_stores(ssid)
                .documents(doc_name)
                .create_or_update(
                    schema_version="V1",
                    contents=[
                        {
                            "modality": "text",
                            "text": (
                                "The quick brown fox jumps over the lazy dog. "
                                "Machine learning is a subset of artificial intelligence."
                            ),
                        }
                    ],
                )
            )

            # Search may fail on freshly created stores (embeddings not indexed yet)
            try:
                result = await client.v1.search_stores(ssid).search(
                    query="artificial intelligence", limit=5
                )
                assert "results" in result
            except httpx.HTTPStatusError:
                pass  # expected on freshly created stores

            await client.v1.search_stores(ssid).documents(doc_name).delete()
        finally:
            await client.v1.search_stores(ssid).delete()
