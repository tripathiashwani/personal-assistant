import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.document import Document
from app.models.user import User
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.schemas.document import (
    DocumentChunkListResponse,
    DocumentListResponse,
    DocumentRead,
)
from app.services.document_service import DocumentService
from app.services.ingestion_service import process_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    document = await DocumentService(db).upload(current_user.id, file)
    # Ingestion (extract -> chunk -> store) runs after the response is
    # sent, so upload feels instant. The client polls GET /documents or
    # GET /documents/{id} to see status flip uploaded -> processing -> ready.
    background_tasks.add_task(process_document, document.id)
    return document


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    documents = await DocumentService(db).list_for_user(current_user.id)
    return DocumentListResponse(documents=documents)


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    return await DocumentService(db).get_owned(current_user.id, document_id)


@router.get("/{document_id}/chunks", response_model=DocumentChunkListResponse)
async def list_document_chunks(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentChunkListResponse:
    document = await DocumentService(db).get_owned(current_user.id, document_id)
    chunks = await DocumentChunkRepository(db).list_by_document(document_id)
    return DocumentChunkListResponse(
        document_id=document.id, status=document.status, chunks=chunks
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await DocumentService(db).delete(current_user.id, document_id)
