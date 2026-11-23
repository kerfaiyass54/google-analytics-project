import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import Settings

settings = Settings()
bearer = HTTPBearer(auto_error=False)
jwks = PyJWKClient(settings.jwks_url, cache_jwk_set=True)


def require_admin(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token required.")
    try:
        key = jwks.get_signing_key_from_jwt(credentials.credentials)
        claims = jwt.decode(
            credentials.credentials,
            key.key,
            algorithms=["RS256"],
            issuer=settings.keycloak_issuer,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": False,
            },
        )
        realm_roles = set((claims.get("realm_access") or {}).get("roles", []))
        client_roles = set(
            ((claims.get("resource_access") or {}).get(settings.keycloak_client_id) or {}).get("roles", [])
        )
        if settings.admin_role not in realm_roles | client_roles:
            raise HTTPException(status_code=403, detail="Administrator role required.")
        return claims
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.") from exc
