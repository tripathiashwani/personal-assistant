"""
PDF text extraction using pypdf.

Note: this only handles text-based PDFs. Scanned/image-only PDFs will
extract empty or near-empty text — that's caught upstream in
ingestion_service, which marks the document as failed rather than
silently storing empty chunks. OCR support is a possible future addition
here, isolated to this one file.
"""
from pypdf import PdfReader


def extract_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()
