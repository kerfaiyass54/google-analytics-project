from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.security.keycloak import issuer, jwks, settings


bearer = HTTPBearer(auto_error=False)


def current_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer
    ),
) -> dict[str, Any]:
    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        key = jwks.get_signing_key_from_jwt(
            credentials.credentials
        )
        options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_iss": True,
            "verify_aud": bool(settings.keycloak_audience),
        }
        return jwt.decode(
            credentials.credentials,
            key.key,
            algorithms=["RS256"],
            issuer=issuer,
            audience=settings.keycloak_audience or None,
            options=options,
        )
    except Exception as exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exception
