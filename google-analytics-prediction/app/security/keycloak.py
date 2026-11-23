from jwt import PyJWKClient
from app.config import get_settings

settings = get_settings()
issuer = settings.keycloak_issuer.rstrip("/")
jwks_url = settings.keycloak_jwks_url or f"{issuer}/protocol/openid-connect/certs"
jwks = PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=300)
