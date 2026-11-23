import os
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ISSUER=os.getenv("KEYCLOAK_ISSUER","http://localhost:8280/realms/google-analytics").rstrip("/")
CLIENT_ID=os.getenv("KEYCLOAK_CLIENT_ID","google-analytics-api")
ADMIN_ROLE=os.getenv("ADMIN_ROLE","ADMIN")
bearer=HTTPBearer(auto_error=False)
jwks=PyJWKClient(f"{ISSUER}/protocol/openid-connect/certs",cache_jwk_set=True)

def require_admin(credentials: HTTPAuthorizationCredentials|None=Depends(bearer)):
    if credentials is None:
        raise HTTPException(401,"Bearer token required.")
    try:
        key=jwks.get_signing_key_from_jwt(credentials.credentials)
        claims=jwt.decode(credentials.credentials,key.key,algorithms=["RS256"],issuer=ISSUER,
            options={"verify_signature":True,"verify_exp":True,"verify_iss":True,"verify_aud":False})
        realm=(claims.get("realm_access") or {}).get("roles",[])
        client_roles=((claims.get("resource_access") or {}).get(CLIENT_ID) or {}).get("roles",[])
        if ADMIN_ROLE not in set(realm)|set(client_roles):
            raise HTTPException(403,"Administrator role required.")
        return claims
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(401,"Invalid or expired access token.") from exc
