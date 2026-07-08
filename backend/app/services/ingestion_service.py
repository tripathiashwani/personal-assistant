"""
Document ingestion pipeline: extract text -> chunk -> store -> update status.

Written as a single plain async function (not a class, not tied to
FastAPI's BackgroundTasks) specifically so it can be handed to Celery
later with minimal change -- swap `background_tasks.add_task(process_document, ...)`
for `process_document_task.delay(...)` and this function's body barely
changes.

Uses its own DB session (AsyncSessionLocal) rather than a request-scoped
one via Depends(get_db) -- by the time a background task runs, the
original request (and its session) may already be closed.
"""
import logging
import uuid

from app.database.session import AsyncSessionLocal
from app.models.document import DocumentStatus
from app.rag.chunking import chunk_text
from app.rag.loaders import load_document_text
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


async def process_document(document_id: uuid.UUID) -> None:
    async with AsyncSessionLocal() as db:
        documents = DocumentRepository(db)
        chunks_repo = DocumentChunkRepository(db)

        document = await documents.get_by_id(document_id)
        if document is None:
            logger.warning("process_document: document %s no longer exists", document_id)
            return

        document.status = DocumentStatus.PROCESSING.value
        await db.commit()

        try:
            text = load_document_text(document.file_path, document.file_type)
            if not text.strip():
                raise ValueError(
                    "No extractable text found (file may be empty, corrupt, "
                    "or an image-only/scanned PDF)."
                )

            chunks = chunk_text(text)
            if not chunks:
                raise ValueError("Chunking produced no chunks from the extracted text.")

            # Idempotent: if this document is ever reprocessed, clear old
            # chunks first rather than appending duplicates.
            await chunks_repo.delete_by_document(document.id)
            await chunks_repo.create_many(document.id, chunks)

            document.status = DocumentStatus.READY.value
            await db.commit()
            logger.info(
                "process_document: document %s ready with %d chunks",
                document_id,
                len(chunks),
            )
        except Exception:
            logger.exception("process_document failed for document %s", document_id)
            document.status = DocumentStatus.FAILED.value
            await db.commit()
