import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationAppError
from app.models.document import Document, DocumentStatus
from app.repositories.document_repository import DocumentRepository
from app.utils.file_utils import (
    MAX_FILE_SIZE_BYTES,
    build_storage_path,
    delete_file,
    extension_to_document_type,
    is_allowed_extension,
    save_file_bytes,
)


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.documents = DocumentRepository(db)

    async def upload(self, user_id: uuid.UUID, file: UploadFile) -> Document:
        if not file.filename:
            raise ValidationAppError("No filename provided.")

        if not is_allowed_extension(file.filename):
            raise ValidationAppError("Only .pdf and .md/.markdown files are supported.")

        content = await file.read()
        if len(content) == 0:
            raise ValidationAppError("Uploaded file is empty.")
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise ValidationAppError(
                f"File exceeds the {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB size limit."
            )

        document_id = uuid.uuid4()
        storage_path = build_storage_path(user_id, document_id, file.filename)
        save_file_bytes(storage_path, content)

        document = Document(
            id=document_id,
            user_id=user_id,
            filename=file.filename,
            file_type=extension_to_document_type(file.filename),
            file_path=str(storage_path),
            status=DocumentStatus.UPLOADED.value,
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def list_for_user(self, user_id: uuid.UUID) -> list[Document]:
        return await self.documents.list_by_user(user_id)

    async def get_owned(self, user_id: uuid.UUID, document_id: uuid.UUID) -> Document:
        """
        Fetches a document and verifies it belongs to the requesting user.
        Returns 404 (not 403) when it belongs to someone else — this avoids
        leaking whether a given document id exists at all to non-owners.
        """
        document = await self.documents.get_by_id(document_id)
        if document is None:
            raise NotFoundError("Document not found.")
        if document.user_id != user_id:
            raise NotFoundError("Document not found.")
        return document

    async def delete(self, user_id: uuid.UUID, document_id: uuid.UUID) -> None:
        document = await self.get_owned(user_id, document_id)
        delete_file(document.file_path)
        await self.documents.delete(document)
