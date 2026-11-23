from fastapi import Depends, HTTPException

from app.config import get_settings
from app.security.current_claims import current_claims


settings = get_settings()


def require_user(
    claims: dict = Depends(current_claims),
) -> dict:
    realm_access = claims.get("realm_access") or {}
    realm_roles = (
        realm_access.get("roles", [])
        if isinstance(realm_access, dict)
        else []
    )
    resource_access = claims.get("resource_access") or {}
    client_access = resource_access.get(settings.keycloak_client_id, {})
    client_roles = (
        client_access.get("roles", [])
        if isinstance(client_access, dict)
        else []
    )
    roles = set(realm_roles) | set(client_roles)

    # Prediction endpoints are reserved for USER accounts. An ADMIN account
    # must use model governance and evaluation screens, not prediction APIs.
    if settings.admin_role in roles or "USER" not in roles:
        raise HTTPException(
            status_code=403,
            detail="USER role required. Administrators cannot submit predictions.",
        )
    return claims
