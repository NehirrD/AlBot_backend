from datetime import datetime
from typing import Annotated, Any, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from core.dtos import JsonDecimal
from features.agent.models import JobStatus
from features.chat.models import MessageRole, SessionStatus



# Chat sessions

#user starts a new chat - optional fields
class ChatSessionCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    category_slug: str | None = None

#user archieved the chat or rename it
class ChatSessionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    status: SessionStatus | None = None  # active | archived

#one chat in chat history list
class ChatSessionResponse(BaseModel):
    # from_attributes lets Pydantic read data directly from the ORM object
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    category_id: UUID | None = None
    title: str | None = None
    status: SessionStatus
    created_at: datetime
    updated_at: datetime

#chat history
class ChatSessionListResponse(BaseModel):
    items: list[ChatSessionResponse]
    total: int



# Message content
# A message can be plain text or a list of recommended products
# The type field tells the client which one it is


#Plain text message - from the user or the albot
class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


#One product card inside a recommendation message
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

#albot message that contains the 3-5 recommended products
class RecommendationsContent(BaseModel):
    type: Literal["recommendations"] = "recommendations"
    job_id: UUID
    text: str | None = None
    items: list[RecommendationCard]


# Pydantic uses type to choose the right class when reading the JSON
ChatMessageContent = Annotated[
    TextContent | RecommendationsContent, Field(discriminator="type")
]



# Chat messages

#user sends a message
class ChatMessageCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)

#answer to a message
class ChatMessageCreateResponse(BaseModel):
    message_id: UUID
    job_id: UUID
    session_id: UUID

# one message in chat
class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    session_id: UUID
    role: MessageRole
    content: ChatMessageContent
    sequence: int
    created_at: datetime

#all messages in chat in order
class ChatMessageListResponse(BaseModel):
    items: list[ChatMessageResponse]



# Live events - pushed to the client over SSE, not a normal response

#A short status update while the job runs
class ProgressEvent(BaseModel):
    seq: int
    step: str | None = None
    replan_round: int
    message: str
    created_at: datetime

#last event of a job
class JobDoneEvent(BaseModel):
    job_id: UUID
    status: JobStatus
    message_id: UUID | None = None