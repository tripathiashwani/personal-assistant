"""
Dispatches to the correct loader based on a document's file_type.

This is the one place that knows "pdf -> pdf_loader, markdown ->
markdown_loader". Adding a new file type later (e.g. .docx, .txt) means
adding one loader module and one line here -- nothing else in the
ingestion pipeline needs to change.
"""
from app.models.document import DocumentType
from app.rag.loaders import markdown_loader, pdf_loader


def load_document_text(file_path: str, file_type: str) -> str:
    if file_type == DocumentType.PDF.value:
        return pdf_loader.extract_text(file_path)
    if file_type == DocumentType.MARKDOWN.value:
        return markdown_loader.extract_text(file_path)
    raise ValueError(f"No loader registered for file_type: {file_type}")
