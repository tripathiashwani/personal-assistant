import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    file_type: str
    status: str
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentRead]


class DocumentChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chunk_index: int
    content: str


class DocumentChunkListResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    chunks: list[DocumentChunkRead]
