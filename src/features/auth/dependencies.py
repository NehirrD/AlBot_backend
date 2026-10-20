# Provides the get_current_user and require_role FastAPI dependencies used to protect endpoints.
# role enum

from dataclasses import dataclass
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from core.config import settings
from core.exceptions import ForbiddenError
from .zitadel import roles_from, verify_token

oauth2_scheme=OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.ZITADEL_ISSUER}/oauth/v2/authorize",
    tokenUrl=f"{settings.ZITADEL_ISSUER}/oauth/v2/token")

@dataclass
class CurrentUser:
    sub:str
    email:str | None
    roles:set[str]


async def get_current_user(token: str=Depends(oauth2_scheme)) -> CurrentUser:
    claims = verify_token(token)
    return CurrentUser(
        sub=claims["sub"],
        email=claims.get("email"),
        roles=roles_from(claims)
    )


def require_role(role:str):
    async def checker(user: CurrentUser=Depends(get_current_user)) -> CurrentUser:
        if role not in user.roles and "admin" not in user.roles:
            raise ForbiddenError("İşlem için yetkiniz yok")
        return user
    return checker
