# Defines framework-independent error classes such as NotFoundError and ForbiddenError that the HTTP layer maps to status codes.

class UnauthorizedError(Exception):
    """Token missing or invalid -> 401"""

class ForbiddenError(Exception):
    """Token is valid, but the role is insufficient -> 403"""