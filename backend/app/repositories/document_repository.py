import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: uuid.UUID,
        filename: str,
        file_type: str,
        file_path: str,
        status: str,
    ) -> Document:
        document = Document(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            status=status,
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete(self, document: Document) -> None:
        await self.db.delete(document)
        await self.db.commit()
