import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(
        self,
        document_id: uuid.UUID,
        chunks: list[str],
        embeddings: list[list[float]] | None = None,
    ) -> list[DocumentChunk]:
        """
        `embeddings`, if provided, must be the same length as `chunks` and
        in the same order -- embeddings[i] belongs to chunks[i]. Passed as
        None during Step 5-only testing; Step 6's ingestion pipeline always
        provides it now.
        """
        objects = [
            DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                content=content,
                embedding=embeddings[i] if embeddings is not None else None,
            )
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

    async def list_embedded_chunks_for_user(self, user_id: uuid.UUID) -> list[DocumentChunk]:
        """
        Candidates for retrieval: only chunks whose parent document is
        fully `ready` (extraction succeeded) AND that have an embedding
        stored, scoped to one user. This is the query retriever.py builds
        its similarity search on top of.
        """
        result = await self.db.execute(
            select(DocumentChunk)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(
                Document.user_id == user_id,
                Document.status == DocumentStatus.READY.value,
                DocumentChunk.embedding.is_not(None),
            )
        )
        return list(result.scalars().all())

    async def delete_by_document(self, document_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        await self.db.commit()
