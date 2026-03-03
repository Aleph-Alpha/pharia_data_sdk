from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import overload

from pharia.models import ContentDTO
from pharia.models import Document
from pharia.models import DocumentContentResponse
from pharia.models import DocumentListResponse
from pharia.models import DocumentWithContents
from pharia.resources.base import gather_with_limit


if TYPE_CHECKING:
    from pharia.client import Client


@dataclass
class DocumentResource:
    """Instance-level operations for a single document in a search store."""

    client: "Client"
    search_store_id: str
    document_name: str

    async def get(self) -> Document:
        """Retrieve this document's metadata."""
        return await self.client.request(
            "GET", f"/search_stores/{self.search_store_id}/documents/{self.document_name}"
        )

    async def get_content(self) -> DocumentContentResponse:
        """Retrieve this document's content."""
        return await self.client.request(
            "GET", f"/search_stores/{self.search_store_id}/documents/{self.document_name}/content"
        )

    async def create_or_update(
        self,
        schema_version: str,
        contents: list[ContentDTO],
        metadata: dict[str, Any] | None = None,
    ) -> DocumentWithContents:
        """Create or update this document."""
        payload: dict[str, Any] = {"schemaVersion": schema_version, "contents": contents}
        if metadata is not None:
            payload["metadata"] = metadata
        return await self.client.request(
            "PUT",
            f"/search_stores/{self.search_store_id}/documents/{self.document_name}",
            json=payload,
        )

    async def update_metadata(self, metadata: dict[str, Any]) -> Document:
        """Update this document's metadata."""
        return await self.client.request(
            "PATCH",
            f"/search_stores/{self.search_store_id}/documents/{self.document_name}/metadata",
            json=metadata,
        )

    async def delete(self) -> None:
        """Delete this document."""
        await self.client.request(
            "DELETE", f"/search_stores/{self.search_store_id}/documents/{self.document_name}"
        )


@dataclass
class BatchDocumentResource:
    """Batch operations for multiple documents in a search store."""

    client: "Client"
    search_store_id: str
    document_names: list[str]

    async def get(self, concurrency: int = 10) -> list[Document]:
        """Retrieve multiple documents concurrently."""
        coros = [
            self.client.request("GET", f"/search_stores/{self.search_store_id}/documents/{name}")
            for name in self.document_names
        ]
        return await gather_with_limit(coros, concurrency)

    async def delete(self, concurrency: int = 10) -> None:
        """Delete multiple documents concurrently."""
        coros = [
            self.client.request("DELETE", f"/search_stores/{self.search_store_id}/documents/{name}")
            for name in self.document_names
        ]
        await gather_with_limit(coros, concurrency)


@dataclass
class SearchStoreDocuments:
    """Collection-level operations for documents in a search store."""

    client: "Client"
    search_store_id: str

    @overload
    def __call__(self, name: str, /) -> DocumentResource: ...

    @overload
    def __call__(self, *names: str) -> BatchDocumentResource: ...

    def __call__(self, *names: str) -> DocumentResource | BatchDocumentResource:
        """Access a document or batch of documents by name(s)."""
        if len(names) == 1:
            return DocumentResource(
                client=self.client, search_store_id=self.search_store_id, document_name=names[0]
            )
        return BatchDocumentResource(
            client=self.client, search_store_id=self.search_store_id, document_names=list(names)
        )

    async def list(
        self, page: int = 0, size: int = 100, name: str = "", starts_with: str = ""
    ) -> DocumentListResponse:
        """List documents in this search store."""
        params = {
            "page": page,
            "size": size,
            **({} if not name else {"name": name}),
            **({} if not starts_with else {"startsWith": starts_with}),
        }
        return await self.client.request(
            "GET", f"/search_stores/{self.search_store_id}/documents", params=params
        )
