# Verifies Zitadel-issued JWT tokens against its public keys and extracts the user id and roles.

import jwt
from jwt import PyJWKClient
from core.config import settings
from core.exceptions import UnauthorizedError

ROLES_CLAIM = "urn:zitadel:iam:org:project:roles"
_jwks=PyJWKClient(settings.ZITADEL_JWKS_URL, cache_keys=True)

def verify_token(token:str) ->dict:
    try:
        key=_jwks.get_signing_key_from_jwt(token).key
        return jwt.decode(token, key, algorithms=["RS256"], issuer=settings.ZITADEL_ISSUER, audience=settings.ZITADEL_PROJECT_ID)

    except jwt.PyJWTError as e:
        raise UnauthorizedError(f"Invalid token: {e}")


def roles_from(claims:dict)->set[str]:
    roles= set(claims.get(ROLES_CLAIM, {}).keys())
    return roles or {"user"} #yeni kayıt olan herkes user ile başlar, adminlik zitadel de elle girilir.

