from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import overload

from pharia.models import File
from pharia.models import FileListResponse
from pharia.models import PresignedURL
from pharia.resources.base import gather_with_limit


if TYPE_CHECKING:
    from pharia.client import Client


@dataclass
class StageFileResource:
    """Instance-level operations for a single file in a stage."""

    client: "Client"
    stage_id: str
    file_id: str

    async def get(self) -> bytes:
        """Download/stream this file."""
        return await self.client.request_raw("GET", f"/stages/{self.stage_id}/files/{self.file_id}")

    async def update(self, file_data: dict) -> File:
        """Update this file."""
        return await self.client.request(
            "PUT", f"/stages/{self.stage_id}/files/{self.file_id}", json=file_data
        )

    async def delete(self) -> None:
        """Delete this file."""
        await self.client.request("DELETE", f"/stages/{self.stage_id}/files/{self.file_id}")

    async def presigned_url(self, ttl: int = 3600) -> PresignedURL:
        """Get a presigned URL for this file."""
        params = {"ttl": ttl}
        return await self.client.request(
            "GET", f"/stages/{self.stage_id}/files/{self.file_id}/presigned-url", params=params
        )


@dataclass
class BatchStageFileResource:
    """Batch operations for multiple files in a stage."""

    client: "Client"
    stage_id: str
    file_ids: list[str]

    async def get(self, concurrency: int = 10) -> list[bytes]:
        """Download multiple files concurrently."""
        coros = [
            self.client.request_raw("GET", f"/stages/{self.stage_id}/files/{fid}")
            for fid in self.file_ids
        ]
        return await gather_with_limit(coros, concurrency)

    async def delete(self, concurrency: int = 10) -> None:
        """Delete multiple files concurrently."""
        coros = [
            self.client.request("DELETE", f"/stages/{self.stage_id}/files/{fid}")
            for fid in self.file_ids
        ]
        await gather_with_limit(coros, concurrency)


@dataclass
class StageFiles:
    """Collection-level operations for files in a stage."""

    client: "Client"
    stage_id: str

    @overload
    def __call__(self, id: str, /) -> StageFileResource: ...

    @overload
    def __call__(self, *ids: str) -> BatchStageFileResource: ...

    def __call__(self, *ids: str) -> StageFileResource | BatchStageFileResource:
        """Access a file or batch of files by ID(s)."""
        if len(ids) == 1:
            return StageFileResource(client=self.client, stage_id=self.stage_id, file_id=ids[0])
        return BatchStageFileResource(
            client=self.client, stage_id=self.stage_id, file_ids=list(ids)
        )

    async def list(
        self,
        page: int = 0,
        size: int = 100,
        name: str = "",
        created_after: str = "",
        created_before: str = "",
    ) -> FileListResponse:
        """List files in this stage."""
        params = {
            "page": page,
            "size": size,
            **({} if not name else {"name": name}),
            **({} if not created_after else {"createdAfter": created_after}),
            **({} if not created_before else {"createdBefore": created_before}),
        }
        return await self.client.request("GET", f"/stages/{self.stage_id}/files", params=params)

    async def create(self, file_data: dict) -> File:
        """Upload a file to this stage."""
        return await self.client.request("POST", f"/stages/{self.stage_id}/files", json=file_data)


@dataclass
class BatchStageFiles:
    """Batch list operations for files across multiple stages."""

    client: "Client"
    stage_ids: list[str]

    async def list(
        self,
        page: int = 0,
        size: int = 100,
        name: str = "",
        created_after: str = "",
        created_before: str = "",
        concurrency: int = 10,
    ) -> list[FileListResponse]:
        """List files in multiple stages concurrently."""
        coros = [
            StageFiles(client=self.client, stage_id=sid).list(
                page=page,
                size=size,
                name=name,
                created_after=created_after,
                created_before=created_before,
            )
            for sid in self.stage_ids
        ]
        return await gather_with_limit(coros, concurrency)
