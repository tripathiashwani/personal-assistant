import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(self, document_id: uuid.UUID, chunks: list[str]) -> list[DocumentChunk]:
        objects = [
            DocumentChunk(document_id=document_id, chunk_index=i, content=content)
            for i, content in enumerate(chunks)
        ]
        self.db.add_all(objects)
        await self.db.commit()
        return objects

    async def list_by_document(self, document_id: uuid.UUID) -> list[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def delete_by_document(self, document_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        await self.db.commit()
