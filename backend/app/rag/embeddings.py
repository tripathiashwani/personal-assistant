"""
Wraps Gemini's embeddings API.

Called from two places: ingestion_service (embed each chunk after
extraction) and retriever (embed the user's query at search time). Both
call through this module -- `from app.rag import embeddings` then
`embeddings.get_embedding(...)` -- rather than importing the function
directly, so tests can patch `app.rag.embeddings.get_embeddings_batch`
and have every caller pick up the patched version.

A future provider swap (different embedding API, or a local model)
only touches this one file -- callers just want "text in, vector out".
"""
import asyncio
from google import genai

from app.core.config import settings

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 1536


class EmbeddingError(Exception):
    pass


def _get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise EmbeddingError(
            "GEMINI_API_KEY is not configured. Set it in your .env file to enable embeddings."
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Embeds multiple texts concurrently. Order is preserved."""
    if not texts:
        return []

    client = _get_client()
    try:
        tasks = [
            client.aio.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
                config={"output_dimensionality": EMBEDDING_DIMENSIONS}
            )
            for text in texts
        ]
        responses = await asyncio.gather(*tasks)
        return [res.embeddings[0].values for res in responses]
    except Exception as e:
        raise EmbeddingError(f"Gemini embedding API call failed: {e}") from e


async def get_embedding(text: str) -> list[float]:
    """Embeds a single piece of text (e.g. a user's chat query)."""
    return (await get_embeddings_batch([text]))[0]

