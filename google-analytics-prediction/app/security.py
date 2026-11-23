from typing import Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from app.config import get_settings

bearer = HTTPBearer(auto_error=False)
settings = get_settings()
issuer = settings.keycloak_issuer.rstrip("/")
jwks = PyJWKClient(f"{issuer}/protocol/openid-connect/certs", cache_jwk_set=True, lifespan=300)

def current_claims(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer authentication is required.", headers={"WWW-Authenticate": "Bearer"})
    try:
        key = jwks.get_signing_key_from_jwt(credentials.credentials)
        options = {"verify_signature": True, "verify_exp": True, "verify_iss": True, "verify_aud": bool(settings.keycloak_audience)}
        return jwt.decode(credentials.credentials, key.key, algorithms=["RS256"], issuer=issuer,
                          audience=settings.keycloak_audience or None, options=options)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.", headers={"WWW-Authenticate": "Bearer"}) from exc

def require_admin(claims: dict = Depends(current_claims)) -> dict:
    realm_access = claims.get("realm_access") or {}
    roles = realm_access.get("roles", []) if isinstance(realm_access, dict) else []
    client_access = (claims.get("resource_access") or {}).get(settings.keycloak_client_id, {})
    client_roles = client_access.get("roles", []) if isinstance(client_access, dict) else []
    if settings.admin_role not in set(roles) | set(client_roles):
        raise HTTPException(status_code=403, detail="Administrator role required.")
    return claims

def require_user(claims: dict = Depends(current_claims)) -> dict:
    return claims
