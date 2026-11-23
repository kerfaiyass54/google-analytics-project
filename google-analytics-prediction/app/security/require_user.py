from fastapi import Depends

from app.security.current_claims import current_claims


def require_user(
    claims: dict = Depends(current_claims),
) -> dict:
    return claims
