from datetime import datetime
from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# Requests:


# Handles pagination (_start, _end) and sorting (_sort, _order) for Refine admin tables (max 150 items).
class AdminListQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True) #
    start: int = Field(default=0, ge=0, alias="_start")  # first row to return
    end: int = Field(default=25, ge=1, le=120, alias="_end")  # last row (max 200 per page)
    sort: str | None = Field(default=None, alias="_sort")  # column name to sort by
    order: Literal["ASC", "DESC"] = Field(default="ASC", alias="_order")


# Responses:

class AdminUserResponse(BaseModel):
    #Roles live in Zitadel so we are not use in here - response body
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    external_auth_id: str  # comes from the Zitadel sub
    email: str
    created_at: datetime
    last_login_at: datetime | None = None


#Who changed what and when:
class AdminAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    admin_user_id: UUID
    action: str
    target_type: str  # what was changed. ex: product
    target_id: str | None = None
    details: dict[str, Any] | None = None  # before and after values
    created_at: datetime