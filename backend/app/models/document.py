import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"      # file saved, not yet processed
    PROCESSING = "processing"  # text extraction / chunking in progress (Step 5+)
    READY = "ready"            # chunks available, safe to use in chat (Step 5+)
    FAILED = "failed"          # extraction failed (Step 5+)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=DocumentStatus.UPLOADED.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
