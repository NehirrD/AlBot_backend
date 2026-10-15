# Creates the FastAPI app, registers the feature routers and exception handlers, and serves as the application entry point.
from fastapi import FastAPI
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from core.config import settings
from core.exceptions import ForbiddenError, UnauthorizedError
from features.auth.dependencies import CurrentUser, get_current_user, require_role


app=FastAPI(
    swagger_ui_init_oauth={
        "clientId": settings.ZITADEL_CLIENT_ID,
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes":(
            "openid profile email"
            f"urn:zitadel:iam:org:project:id:{settings.ZITADEL_PROJECT_ID}:aud"
            "urn:zitadel:iam:org:projects:roles"
            )
    }
)


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


# Test amacıyla geçici endpointler:
@app.get("/me")
async def me(user: CurrentUser = Depends(get_current_user)):
    return {"sub": user.sub, "email": user.email, "roles": sorted(user.roles)}


@app.get("/admin-only")
async def admin_only(user: CurrentUser = Depends(require_role("admin"))):
    return {"message": "Merhaba admin"}

