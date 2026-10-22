from datetime import datetime
from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AdminListParams(BaseModel):
    start: int = Field(default=0, ge=0, alias="_start")
    end: int = Field(default=25, ge=1, le=200, alias="_end")
    sort: str | None = Field(default=None, alias="_sort")
    order: Literal["ASC", "DESC"] = Field(default="ASC", alias="_order")
    model_config = ConfigDict(populate_by_name=True)


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    external_auth_id: str
    email: str
    created_at: datetime
    last_login_at: datetime | None = None

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    admin_user_id: UUID
    action: str
    target_type: str
    target_id: str | None = None
    details: dict[str, Any] | None = None
    created_at: datetime