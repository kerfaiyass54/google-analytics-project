# Keycloak identity and session management

Spring Boot 3.5 / Java 21 service that mirrors Keycloak users and login sessions into PostgreSQL and routes profile changes back through the supported Keycloak APIs.

## Important database boundary

This service **does not read or write Keycloak's internal tables**. Those tables are Keycloak implementation details and direct writes can corrupt the realm. It creates its own `identity_users` and `identity_sessions` tables in the configured PostgreSQL database. Keycloak remains the identity source of truth; all changes are sent through Keycloak's supported APIs, then reflected in the mirror.

## Synchronization

- A scheduled reconciliation runs every 60 seconds (configurable).
- User attributes and enabled/email-verification state are mirrored from Keycloak.
- Active sessions are fetched per user and upserted with IP, start time, last access, and client metadata.
- A mirrored ACTIVE session missing from the next Keycloak session snapshot is changed to CLOSED with `closed_at`.
- Profile updates are sent to Keycloak first, then update the local mirror.
- Password changes use the authenticated user's Keycloak Account API and current-password verification. Passwords are never stored in this service database.

## Keycloak setup

Create a confidential client named `analytics-identity-admin` in the `google-analytics` realm and enable Service Accounts. Grant its service-account user the realm-management roles needed to list users and inspect user sessions (at minimum `view-users`; use `query-users` if required by the realm's fine-grained admin permissions). Store its secret in `KEYCLOAK_IDENTITY_CLIENT_SECRET`, never in source control.

For password changes, enable the account-management feature and make sure the authenticated frontend client has the required account-management permissions. Configure the frontend's realm/client audience so the JWT is accepted by this API.

## Run

From the repository root, with the existing `backend` Docker network and PostgreSQL/Keycloak services running:

```powershell
docker compose -f docker-compose.yml -f identity-management-service/compose.yml up -d --build identity-management-service
```

API base URL: `http://localhost:8040`.

## API

- `GET /api/profile` — current user's profile
- `PUT /api/profile` — update first name, last name, and email in Keycloak and the mirror
- `PUT /api/profile/password` — change password with current-password verification
- `GET /api/profile/sessions` — current user's active and closed sessions
- `GET /api/admin/users` — admin-only synchronized user list
- `GET /api/admin/sessions/summary` — admin-only session totals and seven-day trend
- `GET /api/health` — health check

All routes except health require a valid Keycloak bearer token. Admin routes require the `ADMIN` realm/client role.
