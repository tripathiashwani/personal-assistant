"""
Pure-Python cosine similarity -- the "vector store" for this MVP.

This is deliberately not a real vector database: chunk embeddings are
stored as a JSONB column and every query does a linear scan of the
requesting user's chunks in Python. That's fine at MVP scale (dozens to
low hundreds of documents per user). This is the one function to
replace with a real ANN index (e.g. pgvector's `<=>` operator) once
scale demands it -- retriever.py's calling code doesn't need to change,
just how it fetches candidates and how it scores them.
"""
import math


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vectors must be the same length to compare.")

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)
