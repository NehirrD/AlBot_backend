from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from core.schemas import JsonDecimal
from features.agent.models import JobStatus
from features.catalog.schemas import ProductResponse

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    session_id: UUID
    status: JobStatus
    current_step: str
    replan_count: int
    started_at: datetime
    finished_at: datetime | None = None


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rank: int
    score: JsonDecimal | None = None
    reason: str | None = None
    product: ProductResponse


class JobResultResponse(JobResponse):
    recommendations: list[RecommendationResponse] = []


class AdminJobResponse(JobResponse):
    trigger_message_id: UUID | None = None
    tool_call_count: int
    cost_usd: JsonDecimal
    last_error: str | None = None
    updated_at: datetime

#For admin: why did it recommend this?
class AgentStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    step_number: int
    step: str
    input_context: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    model: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: int | None = None
    error: str | None = None
    created_at: datetime


class SearchFilters(BaseModel):
    keywords: list[str] = []
    min_price: JsonDecimal | None = None
    max_price: JsonDecimal | None = None
    currency: str = "TRY"
    requirements: dict[str, Any] = Field(default_factory=dict)


class JobSnapshot(BaseModel):
    filters: SearchFilters | None = None
    crawled_page_ids: list[UUID] = []
    candidate_product_ids: list[UUID] = []
    rejected_count: int = 0