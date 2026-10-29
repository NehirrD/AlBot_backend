from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from core.dtos import JsonDecimal
from features.agent.models import JobStatus
from features.catalog.dtos import ProductResponse

# Responses (users):

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    session_id: UUID
    status: JobStatus
    current_step: str  # plan | collect | validate | research | rank | done | failed
    replan_count: int
    started_at: datetime
    finished_at: datetime | None = None

#recommended product with its rank and the reasen why it was chosen
class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rank: int
    score: JsonDecimal | None = None
    reason: str | None = None  # why this one- text written by the LLM
    product: ProductResponse


#Finished job response with 3 - 5 product list
class JobResultResponse(JobResponse):
    recommendations: list[RecommendationResponse] = []



# Responses (admin only):

#job view w cost and errors
class AdminJobResponse(JobResponse):
    trigger_message_id: UUID | None = None
    tool_call_count: int
    cost_usd: JsonDecimal
    last_error: str | None = None
    updated_at: datetime

#Trace of one agent step
#Helps admins to see why it recommened this product
class AdminAgentStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    step_number: int
    step: str
    input_context: dict[str, Any] | None = None  #what the LLM was shown
    output: dict[str, Any] | None = None  #what the LLM answered
    model: str | None = None  #cheap or strong model
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: int | None = None
    error: str | None = None
    created_at: datetime



# Internal models (not sent over HTTP)
# TODO: these will be replaced by `JobContext` when we write the orchestrator

#Filters that PLAN extracts from the user's request - max price or minimum RAM
class SearchFilters(BaseModel):
    keywords: list[str] = []
    min_price: JsonDecimal | None = None
    max_price: JsonDecimal | None = None
    currency: str = "TRY"
    requirements: dict[str, Any] = Field(default_factory=dict)


#small checkpoints for context log
class JobSnapshot(BaseModel):
    filters: SearchFilters | None = None
    crawled_page_ids: list[UUID] = []
    candidate_product_ids: list[UUID] = []
    rejected_count: int = 0