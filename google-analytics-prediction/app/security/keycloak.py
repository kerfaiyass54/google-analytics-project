import jwt
from jwt import PyJWKClient

from app.config import get_settings


settings = get_settings()
issuer = settings.keycloak_issuer.rstrip("/")
jwks = PyJWKClient(
    f"{issuer}/protocol/openid-connect/certs",
    cache_jwk_set=True,
    lifespan=300,
)
