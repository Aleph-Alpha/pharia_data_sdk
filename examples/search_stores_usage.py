"""
Search Stores usage examples for the Pharia SDK.

This example demonstrates search store operations using the beta API:
- Creating search stores with semantic embedding
- Creating search stores with instruct embedding
- Listing search stores
- Getting a specific search store
- Updating search store metadata
- Deleting a search store
"""

import asyncio
import uuid

from helpers import ExamplePrinter

from pharia import Client


async def main():
    """Search Stores SDK usage examples."""

    # Client reads credentials from environment variables:
    # - PHARIA_DATA_API_BASE_URL
    # - PHARIA_API_KEY
    client = Client()

    with ExamplePrinter("Search Stores Examples (Beta API)") as p:
        # Example 1: Create a search store with semantic embedding
        p.section(1, 6, "Creating a search store with semantic embedding")
        unique_name_semantic = f"test-semantic-store-{uuid.uuid4().hex[:8]}"

        semantic_store = await client.beta.search_stores.semantic.create(
            name=unique_name_semantic,
            embedding_model="luminous-base",
            representation="asymmetric",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
            metadata={"purpose": "testing", "type": "semantic"},
        )
        p.success(
            f"Created semantic search store: {semantic_store['name']}",
            {
                "ID": semantic_store["id"],
                "Model": semantic_store["embeddingStrategy"]["config"]["model"],
                "Type": semantic_store["embeddingStrategy"]["type"],
            },
        )
        semantic_store_id = semantic_store["id"]

        # Example 2: Create a search store with instruct embedding
        p.section(2, 6, "Creating a search store with instruct embedding")
        unique_name_instruct = f"test-instruct-store-{uuid.uuid4().hex[:8]}"

        instruct_store = await client.beta.search_stores.instruct.create(
            name=unique_name_instruct,
            embedding_model="pharia-1-embedding-256-control",
            instruction_document="Represent this document for retrieval",
            instruction_query="Represent this query for retrieval",
            max_chunk_size_tokens=512,
            chunk_overlap_tokens=128,
            metadata={"purpose": "testing", "type": "instruct"},
        )
        p.success(
            f"Created instruct search store: {instruct_store['name']}",
            {
                "ID": instruct_store["id"],
                "Model": instruct_store["embeddingStrategy"]["config"]["model"],
                "Type": instruct_store["embeddingStrategy"]["type"],
                "Instruction": instruct_store["embeddingStrategy"]["config"]["instruction"][
                    "document"
                ][:50]
                + "...",
            },
        )
        instruct_store_id = instruct_store["id"]

        # Example 3: List all search stores
        p.section(3, 6, "Listing search stores")
        search_stores_response = await client.beta.search_stores.list(page=0, size=10)
        p.success(f"Found {search_stores_response['total']} total search stores")

        if search_stores_response.get("searchStores"):
            for ss in search_stores_response["searchStores"][:3]:  # Show first 3
                p.info(f"{ss.get('name', 'unnamed')} (ID: {ss['id']})", indent=1)
                p.info(f"Chunks: {ss['chunkingStrategy']['maxChunkSizeTokens']} tokens", indent=2)

        # Example 4: Get a specific search store
        p.section(4, 6, "Getting a specific search store")
        retrieved_store = await client.beta.search_stores.get(semantic_store_id)
        p.success(
            f"Retrieved search store: {retrieved_store.get('name', 'unnamed')}",
            {
                "ID": retrieved_store["id"],
                "Chunking": f"{retrieved_store['chunkingStrategy']['maxChunkSizeTokens']} tokens",
                "Embedding": retrieved_store["embeddingStrategy"]["type"],
            },
        )

        # Example 5: Update search store metadata
        p.section(5, 6, "Updating search store metadata")
        updated_store = await client.beta.search_stores.update(
            semantic_store_id,
            metadata={"purpose": "testing", "environment": "dev", "updated": "true"},
        )
        p.success(
            "Updated search store metadata",
            {"Metadata keys": list(updated_store.get("metadata", {}).keys())},
        )

        # Example 6: Delete the search stores
        p.section(6, 6, "Deleting search stores")
        await client.beta.search_stores.delete(semantic_store_id)
        p.success(f"Deleted semantic search store: {semantic_store_id}")

        await client.beta.search_stores.delete(instruct_store_id)
        p.success(f"Deleted instruct search store: {instruct_store_id}")

        # Verify deletion
        remaining_semantic = await client.beta.search_stores.list(name=unique_name_semantic)
        remaining_instruct = await client.beta.search_stores.list(name=unique_name_instruct)
        p.info(
            f"Verified deletion - found {remaining_semantic['total']} semantic and {remaining_instruct['total']} instruct stores",
            indent=1,
        )


if __name__ == "__main__":
    asyncio.run(main())
