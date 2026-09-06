from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import DocumentStatus

if TYPE_CHECKING:
    from app.models.project import Project


class ProjectDocument(Base):
    __tablename__ = "project_documents"
    __table_args__ = (
        CheckConstraint("page_count IS NULL OR page_count > 0", name="page_count_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    document_type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(300))
    source_url: Mapped[str] = mapped_column(Text)
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    published_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus,
            name="document_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=DocumentStatus.PENDING,
        server_default=DocumentStatus.PENDING.value,
        index=True,
    )
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[Project] = relationship(back_populates="documents")
    chunks: Mapped[list[DocumentChunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunks_document_index"),
        CheckConstraint("chunk_index >= 0", name="chunk_index_non_negative"),
        CheckConstraint("page_start IS NULL OR page_start > 0", name="page_start_positive"),
        CheckConstraint("page_end IS NULL OR page_end > 0", name="page_end_positive"),
        CheckConstraint(
            "page_end IS NULL OR page_start IS NULL OR page_end >= page_start",
            name="page_order",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("project_documents.id", ondelete="CASCADE"), index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(1536))
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, server_default="{}"
    )

    document: Mapped[ProjectDocument] = relationship(back_populates="chunks")
