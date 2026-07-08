"""
Splits extracted text into overlapping chunks for retrieval.

Deliberately word-based rather than using a real tokenizer (e.g.
tiktoken): tiktoken downloads its encoding file from the network on
first use, which is an unnecessary hidden dependency for something as
basic as chunking, and would break in offline/restricted environments.
Word count is a fine proxy for chunk size at this stage — if precise
token budgeting against a specific embedding model's limits becomes
necessary later, this is the one function to swap.
"""

DEFAULT_CHUNK_SIZE_WORDS = 300
DEFAULT_OVERLAP_WORDS = 50


def chunk_text(
    text: str,
    chunk_size_words: int = DEFAULT_CHUNK_SIZE_WORDS,
    overlap_words: int = DEFAULT_OVERLAP_WORDS,
) -> list[str]:
    if chunk_size_words <= overlap_words:
        raise ValueError("chunk_size_words must be greater than overlap_words")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = chunk_size_words - overlap_words
    start = 0

    while start < len(words):
        end = min(start + chunk_size_words, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
        start += step

    return chunks
