import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from albot.core.database import Base


class SearchQuery(Base):
    __tablename__ = "search_queries"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("search_jobs.id"))
    message_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chat_messages.id"))
    raw_query: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_filters: Mapped[dict | None] = mapped_column(JSONB)
    search_round: Mapped[int] = mapped_column(Integer, server_default=text("1"), nullable=False)
    status: Mapped[str] = mapped_column(String, server_default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CrawledPage(Base):
    __tablename__ = "crawled_pages"
    __table_args__ = (UniqueConstraint("job_id", "url"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("search_jobs.id"), nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    http_status: Mapped[int | None] = mapped_column(Integer)
    html: Mapped[str | None] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)