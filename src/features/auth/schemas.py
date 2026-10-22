#No request class: Only the ZItadel token is input

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    roles: list[str]  #comes from token, not from our db
    last_login_at: datetime | None = None