"""
Markdown text extraction.

MVP approach: read the raw file as-is. Markdown syntax (#, *, -, etc.)
is left in place rather than stripped — it's cheap for the LLM to parse
and headers actually carry useful structural meaning for retrieval
(e.g. "# Advantages" tells the model something a stripped-down blob
wouldn't). If this turns out to hurt retrieval quality later, this is
the one file to swap for a proper markdown-to-text converter.
"""
from pathlib import Path


def extract_text(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore").strip()
