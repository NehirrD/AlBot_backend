#chat_sessions, chat_messages

import enum
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime,Enum, ForeignKey,Integer, String, Text,UniqueConstraint, func,text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from albot.core.database import Base

class MessageRole(str, enum.Enum):
    USER="user"
    ASSISTANT="assistant"
    SYSTEM="system"
    TOOL="tool"

class SessionStatus(str, enum.Enum):
    ACTIVE="active"
    INACTIVE="inactive"

class ChatSession(Base):
    __tablename__="chat_sessions"
    __table_args__ = (UniqueConstraint("user_id", "category_id"))
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True, server_default=text("gen_random_uuid()"))
    user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("users.id"),nullable=False)
    category_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("categories.id"),nullable=False)
    title:Mapped[str|None]=mapped_column(String)  #Oluşturulan yeni sohbet isimsiz kalabilir - kısa bir süre
    summary:Mapped[str|None]=mapped_column(Text)
    summary_up_to_sequence: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(
            SessionStatus,
            name="session_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        server_default="active",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

class ChatMessage(Base):
    __tablename__="chat_messages"
    __table_args__ = (UniqueConstraint("session_id", "sequence"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(
        Enum(
            MessageRole,
            name="message_role",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    # metadata SQLAlchemyde ayrılmış bir ad, o yüzden Pythonda meta diyoruz,
    # veritabanındaki sütun adı yine "metadata kalacak
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )