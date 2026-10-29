from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

# There is no request DTO here. The only input is the Zitadel token
# in the `Authorization: Bearer <JWT>` header.

#logged in user:
class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    roles: list[str]  #comes from token - not our db
    last_login_at: datetime | None = None