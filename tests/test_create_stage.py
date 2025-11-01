"""
Comprehensive test for creating stages with different embedding types.
"""

import asyncio
import os
import uuid

import pytest

from pharia import Client


@pytest.mark.asyncio
async def test_create_stages():
    """Test creating stages with different embedding configurations."""
    client = Client()

    created_stage_ids = []

    # Test 1: Create stage with NO embedding (simple stage)
    stage = await client.stages.create(
        name=f"SDK Test - Simple Stage (No Embedding)-{uuid.uuid4()}"
    )
    assert stage["stageId"] is not None
    assert stage["name"].startswith("SDK Test - Simple Stage")
    created_stage_ids.append(stage["stageId"])

    # Test 2: Create stage with INSTRUCT embedding
    stage = await client.stages.instruct.create(
        name=f"SDK Test - Instruct Embedding Stage-{uuid.uuid4()}",
        embedding_model="pharia-1-embedding-256-control",
        instruction_document="Represent this document for retrieval",
        instruction_query="Represent this query for retrieval",
        hybrid_index="bm25",
        max_chunk_size_tokens=512,
        chunk_overlap_tokens=128,
    )
    assert stage["stageId"] is not None
    assert stage.get("searchStore") is not None
    assert stage["searchStore"].get("embeddingStrategy", {}).get("type") == "instruct"
    created_stage_ids.append(stage["stageId"])

    # Test 3: Create stage with SEMANTIC embedding
    stage = await client.stages.semantic.create(
        name=f"SDK Test - Semantic Embedding Stage-{uuid.uuid4()}",
        embedding_model="luminous-base",
        representation="asymmetric",
        hybrid_index="bm25",
        max_chunk_size_tokens=1024,
        chunk_overlap_tokens=256,
    )
    assert stage["stageId"] is not None
    assert stage.get("searchStore") is not None
    assert stage["searchStore"].get("embeddingStrategy", {}).get("type") == "semantic"
    created_stage_ids.append(stage["stageId"])

    # Test 4: Create stage with VLLM embedding
    stage = await client.stages.vllm.create(
        name=f"SDK Test - VLLM Embedding Stage-{uuid.uuid4()}",
        embedding_model="qwen3-embedding-8b",
        hybrid_index="bm25",
        max_chunk_size_tokens=2046,
        chunk_overlap_tokens=512,
    )
    assert stage["stageId"] is not None
    assert stage.get("searchStore") is not None
    created_stage_ids.append(stage["stageId"])

    # Cleanup: Delete created stages
    for stage_id in created_stage_ids:
        try:
            await client.stages.delete(stage_id)
        except Exception as e:
            print(f"Warning: Failed to delete test stage {stage_id}: {e}")
