from datetime import datetime
from typing import Annotated, Any, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from core.schemas import JsonDecimal
from features.agent.models import JobStatus
from features.chat.models import MessageRole, SessionStatus


class SessionCreateRequest(BaseModel):
    pass


class SessionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    status: SessionStatus | None = None  # ACTIVE <-> ARCHIVED


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    category_id: UUID | None = None
    title: str | None = None
    status: SessionStatus
    created_at: datetime
    updated_at: datetime


class SessionListResponse(BaseModel):
    items: list[SessionResponse]
    total: int


class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


class RecommendationCard(BaseModel):
    product_id: UUID
    rank: int
    score: JsonDecimal | None = None
    reason: str | None = None
    title: str
    price: JsonDecimal | None = None
    currency: str
    url: str
    image_url: str | None = None
    specs: dict[str, Any] | None = None


class RecommendationsContent(BaseModel):
    type: Literal["recommendations"] = "recommendations"
    job_id: UUID
    text: str | None = None  # short intro sentence from the assistant
    items: list[RecommendationCard]


MessageContent = Annotated[
    TextContent | RecommendationsContent, Field(discriminator="type")
]



class MessageCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    session_id: UUID
    role: MessageRole
    content: MessageContent
    sequence: int
    created_at: datetime


class MessageListResponse(BaseModel):
    items: list[MessageResponse]


class SendMessageResponse(BaseModel):
    message_id: UUID
    job_id: UUID
    session_id: UUID


class ProgressEventResponse(BaseModel):
    seq: int
    step: str | None = None
    replan_round: int
    message: str  # context_log.public_message
    created_at: datetime


class JobDoneEventResponse(BaseModel):
    job_id: UUID
    status: JobStatus  # completed | failed | cancelled
    message_id: UUID | None = None  # assistant message to fetch; None if the job failed