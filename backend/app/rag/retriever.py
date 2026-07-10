"""
Given a natural-language query, returns the most relevant chunks
belonging to a specific user.

This is the seam future work plugs into: Step 8's LangGraph agent will
call get_relevant_chunks() to build context for the LLM. When we swap
to pgvector later, only the "fetch candidates + score" internals change
-- the contract (query in, ranked ScoredChunk list out) stays the same.
"""
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag import embeddings
from app.rag.vector_store import cosine_similarity
from app.repositories.document_chunk_repository import DocumentChunkRepository

DEFAULT_TOP_K = 5


@dataclass
class ScoredChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    content: str
    score: float


async def get_relevant_chunks(
    db: AsyncSession,
    user_id: uuid.UUID,
    query: str,
    top_k: int = DEFAULT_TOP_K,
) -> list[ScoredChunk]:
    candidates = await DocumentChunkRepository(db).list_embedded_chunks_for_user(user_id)
    if not candidates:
        return []

    query_embedding = await embeddings.get_embedding(query)

    scored = [
        ScoredChunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            score=cosine_similarity(query_embedding, chunk.embedding),
        )
        for chunk in candidates
    ]
    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:top_k]
