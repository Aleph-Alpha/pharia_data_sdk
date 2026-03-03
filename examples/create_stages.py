"""
Example: Creating stages with different embedding configurations.

This example demonstrates how to create stages with:
1. No embedding (simple stage)
2. Instruct embedding (for instructable embeddings)
3. Semantic embedding (for semantic search)
4. VLLM embedding (for VLLM-based embeddings)

Note: This example will create and then delete stages for demonstration purposes.
"""

import asyncio
import uuid
from typing import Any

from examples.helpers import ExamplePrinter
from pharia import Client
from pharia import Stage


def _stage_details(stage: Stage, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build display details for a created stage."""
    details: dict[str, Any] = {"Stage ID": stage["stageId"], "Name": stage["name"]}
    if extra:
        details.update(extra)

    search_store = stage.get("searchStore")
    if search_store is None:
        return details

    details["Search Store ID"] = search_store["id"]

    embedding = search_store.get("embeddingStrategy")
    if embedding is None:
        return details

    details["Embedding Type"] = embedding.get("type")
    return details


async def main():
    """Demonstrate creating stages with different embedding types."""

    # Client reads credentials from environment variables:
    # - PHARIA_DATA_API_BASE_URL
    # - PHARIA_API_KEY
    client = Client()

    created_stage_ids: list[str] = []

    with ExamplePrinter("Creating Stages with Different Embeddings") as p:
        # Example 1: Create a simple stage WITHOUT embedding
        p.section(1, 4, "Creating a simple stage (no embedding)")
        try:
            stage = await client.v1.stages.create(name=f"Example - Simple Stage-{uuid.uuid4()}")
            p.success("SUCCESS!", _stage_details(stage, {"Files Count": stage["filesCount"]}))
            created_stage_ids.append(stage["stageId"])
        except Exception as e:
            p.error(f"FAILED: {e}")

        # Example 2: Create a stage with INSTRUCT embedding
        p.section(
            2,
            4,
            "Creating a stage with instruct embedding",
            "When you want to provide custom instructions for embeddings",
        )
        try:
            stage = await client.v1.stages.instruct.create(
                name=f"Example - Instruct Embedding-{uuid.uuid4()}",
                embedding_model="pharia-1-embedding-256-control",
                instruction_document="Represent this document for retrieval",
                instruction_query="Represent this query for retrieval",
                hybrid_index="bm25",
                max_chunk_size_tokens=512,
                chunk_overlap_tokens=128,
            )
            p.success(
                "SUCCESS!",
                _stage_details(stage, {"Chunk Size": "512 tokens", "Chunk Overlap": "128 tokens"}),
            )
            created_stage_ids.append(stage["stageId"])
        except Exception as e:
            p.error(f"FAILED: {e}")

        # Example 3: Create a stage with SEMANTIC embedding
        p.section(
            3,
            4,
            "Creating a stage with semantic embedding",
            "For semantic search with asymmetric/symmetric representations",
        )
        try:
            stage = await client.v1.stages.semantic.create(
                name=f"Example - Semantic Embedding-{uuid.uuid4()}",
                embedding_model="luminous-base",
                representation="asymmetric",
                hybrid_index="bm25",
                max_chunk_size_tokens=1024,
                chunk_overlap_tokens=256,
            )
            p.success(
                "SUCCESS!",
                _stage_details(
                    stage, {"Representation": "asymmetric", "Chunk Size": "1024 tokens"}
                ),
            )
            created_stage_ids.append(stage["stageId"])
        except Exception as e:
            p.error(f"FAILED: {e}")

        # Example 4: Create a stage with VLLM embedding
        p.section(
            4, 4, "Creating a stage with VLLM embedding", "For using VLLM-based embedding models"
        )
        try:
            stage = await client.v1.stages.vllm.create(
                name=f"Example - VLLM Embedding-{uuid.uuid4()}",
                embedding_model="qwen3-embedding-8b",
                hybrid_index="bm25",
                max_chunk_size_tokens=2046,
                chunk_overlap_tokens=512,
            )
            p.success("SUCCESS!", _stage_details(stage, {"Chunk Size": "2046 tokens"}))
            created_stage_ids.append(stage["stageId"])
        except Exception as e:
            p.error(f"FAILED: {e}")

        # Summary
        p.info(f"\nCreated {len(created_stage_ids)} stages total")

        if not created_stage_ids:
            return

        p.list_items(created_stage_ids, "Created Stage IDs")

        # Cleanup using fluent API
        p.info("\nCleaning up: Deleting example stages...")
        for stage_id in created_stage_ids:
            try:
                await client.v1.stages(stage_id).delete()
                p.success(f"Deleted stage: {stage_id}")
            except Exception as e:
                p.error(f"Failed to delete {stage_id}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
