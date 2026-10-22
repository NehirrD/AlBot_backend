from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class SearchQueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    session_id: UUID
    job_id: UUID | None = None
    message_id: UUID | None = None
    raw_query: str
    extracted_filters: dict[str, Any] | None = None
    search_round: int
    status: str  #pending -> done or failed
    created_at: datetime


class CrawledPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    job_id: UUID
    source: str
    url: str
    http_status: int | None = None
    fetched_at: datetime