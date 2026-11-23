from fastapi import Depends, HTTPException

from app.config import get_settings
from app.security.current_claims import current_claims


settings = get_settings()


def require_admin(
    claims: dict = Depends(current_claims),
) -> dict:
    realm_access = claims.get("realm_access") or {}
    roles = (
        realm_access.get("roles", [])
        if isinstance(realm_access, dict)
        else []
    )
    client_access = (
        claims.get("resource_access") or {}
    ).get(settings.keycloak_client_id, {})
    client_roles = (
        client_access.get("roles", [])
        if isinstance(client_access, dict)
        else []
    )
    if settings.admin_role not in set(roles) | set(client_roles):
        raise HTTPException(
            status_code=403,
            detail="Administrator role required.",
        )
    return claims
