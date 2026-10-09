import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from albot.core.database import Base

class AdminAuditLog(Base):
    __tablename__ = "admin_audit_log"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    admin_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    target_type: Mapped[str] = mapped_column(String, nullable=False)
    target_id: Mapped[str | None] = mapped_column(String)
    details: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

