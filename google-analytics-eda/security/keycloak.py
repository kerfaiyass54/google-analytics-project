"""
Keycloak JWT security for FastAPI.

Responsibilities:
    - Read Bearer tokens from HTTP requests
    - Validate Keycloak JWT signatures
    - Validate issuer
    - Validate audience when configured
    - Validate token expiration
    - Extract authenticated user information

Keycloak:
    Keycloak 25+

Architecture:

    Angular
        |
        | Authorization: Bearer <access_token>
        v
    FastAPI
        |
        v
    KeycloakSecurity
        |
        +---- OIDC discovery
        |
        +---- JWKS public keys
        |
        v
    Authenticated user
"""

from __future__ import annotations

from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt import PyJWKClient
from pydantic import BaseModel

from config import get_keycloak_config


# ============================================================
# BEARER AUTHENTICATION
# ============================================================

bearer_scheme = HTTPBearer(
    auto_error=False
)


# ============================================================
# USER MODEL
# ============================================================

class KeycloakUser(BaseModel):
    """
    Authenticated Keycloak user.

    Only the information required by the application
    should be exposed to the business layer.
    """

    user_id: str

    email: str

    username: str | None = None

    preferred_username: str | None = None

    roles: list[str] = []


# ============================================================
# SECURITY SERVICE
# ============================================================

class KeycloakSecurity:
    """
    Validates and extracts information from Keycloak JWTs.

    The class uses Keycloak's JWKS endpoint to obtain
    the public keys required to verify token signatures.
    """

    def __init__(self) -> None:

        config = get_keycloak_config()

        self.issuer = (
            config.issuer.rstrip("/")
        )

        self.client_id = (
            config.client_id
        )

        self.audience = (
            config.audience
        )

        # ----------------------------------------------------
        # Keycloak OIDC JWKS endpoint
        # ----------------------------------------------------

        self.jwks_url = (
            f"{self.issuer}"
            "/protocol/openid-connect/certs"
        )

        self.jwks_client = PyJWKClient(
            self.jwks_url,
            cache_jwk_set=True,
            lifespan=300,
            max_cached_keys=16,
        )

    # ========================================================
    # VALIDATE TOKEN
    # ========================================================

    def validate_token(
        self,
        token: str,
    ) -> dict[str, Any]:
        """
        Validate a Keycloak access token.

        Validation includes:

            - Signature
            - Issuer
            - Expiration
            - Audience when configured

        Returns:
            Decoded JWT claims.

        Raises:
            HTTPException:
                401 when the token is invalid.
        """

        if not token:

            raise self._unauthorized(
                "Missing access token."
            )

        try:

            # ------------------------------------------------
            # Get signing key from Keycloak JWKS
            # ------------------------------------------------

            signing_key = (
                self.jwks_client.get_signing_key_from_jwt(
                    token
                )
            )

            # ------------------------------------------------
            # JWT validation options
            # ------------------------------------------------

            decode_options = {
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
            }

            # ------------------------------------------------
            # Audience validation
            #
            # Keycloak access tokens do not necessarily have
            # your client ID as `aud` unless the appropriate
            # audience mapper is configured.
            # ------------------------------------------------

            if self.audience:

                decode_options[
                    "verify_aud"
                ] = True

            else:

                decode_options[
                    "verify_aud"
                ] = False

            # ------------------------------------------------
            # Decode and validate
            # ------------------------------------------------

            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=[
                    "RS256"
                ],
                issuer=self.issuer,
                audience=(
                    self.audience
                    if self.audience
                    else None
                ),
                options=decode_options,
            )

            return claims

        except jwt.ExpiredSignatureError as exception:

            raise self._unauthorized(
                "Access token has expired."
            ) from exception

        except jwt.InvalidIssuerError as exception:

            raise self._unauthorized(
                "Invalid token issuer."
            ) from exception

        except jwt.InvalidAudienceError as exception:

            raise self._unauthorized(
                "Invalid token audience."
            ) from exception

        except jwt.InvalidSignatureError as exception:

            raise self._unauthorized(
                "Invalid token signature."
            ) from exception

        except jwt.PyJWTError as exception:

            raise self._unauthorized(
                "Invalid access token."
            ) from exception

        except Exception as exception:

            raise self._unauthorized(
                "Unable to validate access token."
            ) from exception

    # ========================================================
    # EXTRACT USER
    # ========================================================

    def get_user(
        self,
        token: str,
    ) -> KeycloakUser:
        """
        Validate a JWT and convert its claims into
        an application-level KeycloakUser.
        """

        claims = (
            self.validate_token(
                token
            )
        )

        # ----------------------------------------------------
        # Required user ID
        # ----------------------------------------------------

        user_id = claims.get(
            "sub"
        )

        if not user_id:

            raise self._unauthorized(
                "Token does not contain a subject."
            )

        # ----------------------------------------------------
        # Email
        # ----------------------------------------------------

        email = claims.get(
            "email"
        )

        if not email:

            raise self._unauthorized(
                "Token does not contain an email."
            )

        # ----------------------------------------------------
        # Username
        # ----------------------------------------------------

        username = claims.get(
            "username"
        )

        preferred_username = claims.get(
            "preferred_username"
        )

        # ----------------------------------------------------
        # Roles
        # ----------------------------------------------------

        roles = self._extract_roles(
            claims
        )

        return KeycloakUser(
            user_id=str(
                user_id
            ),
            email=str(
                email
            ),
            username=(
                str(username)
                if username is not None
                else None
            ),
            preferred_username=(
                str(preferred_username)
                if preferred_username is not None
                else None
            ),
            roles=roles,
        )

    # ========================================================
    # EXTRACT ROLES
    # ========================================================

    @staticmethod
    def _extract_roles(
        claims: dict[str, Any],
    ) -> list[str]:
        """
        Extract Keycloak realm and client roles.

        Keycloak commonly stores:

            realm roles:
                realm_access.roles

            client roles:
                resource_access.<client>.roles
        """

        roles: set[str] = set()

        # ----------------------------------------------------
        # Realm roles
        # ----------------------------------------------------

        realm_access = claims.get(
            "realm_access",
            {},
        )

        if isinstance(
            realm_access,
            dict,
        ):

            realm_roles = realm_access.get(
                "roles",
                [],
            )

            if isinstance(
                realm_roles,
                list,
            ):

                roles.update(
                    str(role)
                    for role in realm_roles
                )

        # ----------------------------------------------------
        # Client roles
        # ----------------------------------------------------

        resource_access = claims.get(
            "resource_access",
            {},
        )

        if isinstance(
            resource_access,
            dict,
        ):

            for client_data in (
                resource_access.values()
            ):

                if not isinstance(
                    client_data,
                    dict,
                ):

                    continue

                client_roles = client_data.get(
                    "roles",
                    [],
                )

                if isinstance(
                    client_roles,
                    list,
                ):

                    roles.update(
                        str(role)
                        for role in client_roles
                    )

        return sorted(
            roles
        )

    # ========================================================
    # UNAUTHORIZED
    # ========================================================

    @staticmethod
    def _unauthorized(
        message: str,
    ) -> HTTPException:
        """
        Build a standard HTTP 401 response.

        WWW-Authenticate is important for Bearer
        authentication according to HTTP authentication
        conventions.
        """

        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


# ============================================================
# SINGLETON
# ============================================================

keycloak_security = (
    KeycloakSecurity()
)


# ============================================================
# FASTAPI DEPENDENCY
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> KeycloakUser:
    """
    FastAPI dependency that authenticates the current user.

    Usage:

        @router.get(...)
        def endpoint(
            user: KeycloakUser = Depends(
                get_current_user
            )
        ):
            ...

    The endpoint receives a fully validated KeycloakUser.
    """

    if credentials is None:

        raise keycloak_security._unauthorized(
            "Authentication is required."
        )

    if credentials.scheme.lower() != "bearer":

        raise keycloak_security._unauthorized(
            "Bearer authentication is required."
        )

    return keycloak_security.get_user(
        credentials.credentials
    )


# ============================================================
# EMAIL DEPENDENCY
# ============================================================

def get_current_user_email(
    user: KeycloakUser = Depends(
        get_current_user
    ),
) -> str:
    """
    FastAPI dependency returning only the authenticated
    user's email.

    This is useful for services that only need the email.

    Example:

        current_user_email: str = Depends(
            get_current_user_email
        )
    """

    return user.email