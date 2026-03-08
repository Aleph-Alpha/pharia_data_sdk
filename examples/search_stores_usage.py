"""
Search Stores usage examples for the Pharia SDK.

This example demonstrates search store operations using the v1 API:
- Creating search stores with semantic embedding
- Creating search stores with instruct embedding
- Listing search stores
- Getting a specific search store
- Updating search store metadata
- Searching with the Filter DSL
- Deleting a search store
"""

import asyncio
import uuid

from examples.helpers import ExamplePrinter
from pharia import And
from pharia import Client
from pharia import Filter
from pharia import ModalityCondition


async def main():
    """Search Stores SDK usage examples."""

    # Client reads credentials from environment variables:
    # - PHARIA_DATA_API_BASE_URL
    # - PHARIA_API_KEY
    client = Client()

    with ExamplePrinter("Search Stores Examples (V1 API)") as p:
        # Example 1: Create a search store with semantic embedding
        p.section(1, 6, "Creating a search store with semantic embedding")
        unique_name_semantic = f"test-semantic-store-{uuid.uuid4().hex[:8]}"

        semantic_store = await client.v1.search_stores.semantic.create(
            name=unique_name_semantic,
            embedding_model="luminous-base",
            representation="asymmetric",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
            metadata={"purpose": "testing", "type": "semantic"},
        )
        p.success(
            f"Created semantic search store: {semantic_store['id']}",
            {"ID": semantic_store["id"], "Type": semantic_store["embeddingStrategy"]["type"]},
        )
        semantic_store_id = semantic_store["id"]

        # Example 2: Create a search store with instruct embedding
        p.section(2, 6, "Creating a search store with instruct embedding")
        unique_name_instruct = f"test-instruct-store-{uuid.uuid4().hex[:8]}"

        instruct_store = await client.v1.search_stores.instruct.create(
            name=unique_name_instruct,
            embedding_model="pharia-1-embedding-256-control",
            instruction_document="Represent this document for retrieval",
            instruction_query="Represent this query for retrieval",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
            metadata={"purpose": "testing", "type": "instruct"},
        )
        p.success(
            f"Created instruct search store: {instruct_store['id']}",
            {"ID": instruct_store["id"], "Type": instruct_store["embeddingStrategy"]["type"]},
        )
        instruct_store_id = instruct_store["id"]

        # Example 3: List all search stores
        p.section(3, 6, "Listing search stores")
        search_stores_response = await client.v1.search_stores.list(page=1, size=10)
        p.success(f"Found {search_stores_response['total']} total search stores")

        if search_stores_response.get("results"):
            for ss in search_stores_response["results"][:3]:  # Show first 3
                p.info(f"ID: {ss['id']}", indent=1)
                p.info(f"Chunks: {ss['chunkingStrategy']['maxChunkSizeTokens']} tokens", indent=2)

        # Example 4: Get a specific search store (fluent API)
        p.section(4, 6, "Getting a specific search store")
        retrieved_store = await client.v1.search_stores(semantic_store_id).get()
        p.success(
            f"Retrieved search store: {retrieved_store['id']}",
            {
                "ID": retrieved_store["id"],
                "Chunking": f"{retrieved_store['chunkingStrategy']['maxChunkSizeTokens']} tokens",
                "Embedding": retrieved_store["embeddingStrategy"]["type"],
            },
        )

        # Example 5: Update search store metadata (fluent API)
        p.section(5, 6, "Updating search store metadata")
        updated_store = await client.v1.search_stores(semantic_store_id).update(
            metadata={"purpose": "testing", "environment": "dev", "updated": "true"}
        )
        p.success(
            "Updated search store metadata",
            {"Metadata keys": list(updated_store.get("metadata", {}).keys())},
        )

        # Example 6: Search with Filter DSL
        p.section(6, 7, "Searching with Filter DSL")

        # Add a document so there's something to search
        doc_name = f"test-doc-{uuid.uuid4().hex[:8]}"
        await (
            client.v1.search_stores(semantic_store_id)
            .documents(doc_name)
            .create_or_update(
                schema_version="V1",
                contents=[{"modality": "text", "text": "Machine learning is a subset of AI."}],
                metadata={"category": "science"},
            )
        )
        p.info(f"Created document: {doc_name}", indent=1)

        # Search using the Filter DSL
        search_result = await client.v1.search_stores(semantic_store_id).search(
            query="artificial intelligence",
            max_results=5,
            filters=[And(Filter("category") == "science", ModalityCondition.text())],
        )
        p.success(
            f"Search returned {len(search_result)} results",
            {"Query": "artificial intelligence", "Filter": 'category == "science"'},
        )

        # Clean up document
        await client.v1.search_stores(semantic_store_id).documents(doc_name).delete()

        # Example 7: Delete the search stores (fluent API)
        p.section(7, 7, "Deleting search stores")
        await client.v1.search_stores(semantic_store_id).delete()
        p.success(f"Deleted semantic search store: {semantic_store_id}")

        await client.v1.search_stores(instruct_store_id).delete()
        p.success(f"Deleted instruct search store: {instruct_store_id}")


if __name__ == "__main__":
    asyncio.run(main())
