# Notification Service

Node.js + KafkaJS + PostgreSQL service. It creates a separate PostgreSQL database named `notifications_db` automatically (using the configured PostgreSQL admin credentials), then creates the `notifications` table and indexes.

## Run

From the repository root:

```powershell
docker compose -f docker-compose.yml -f notification-service/compose.yml up -d --build notification-service
```

API: `http://localhost:8030`; health: `/health`.

## Authenticated API

All API routes except health require a Keycloak bearer token.

- `GET /api/notifications?limit=20`
- `GET /api/notifications?unread=true`
- `GET /api/notifications/unread-count`
- `PATCH /api/notifications/:id/read`
- `PATCH /api/notifications/read-all`

The service derives the recipient role from the verified Keycloak token. ADMIN notifications and USER notifications are separated by role. Duplicate Kafka deliveries are ignored by the unique `(event_id, recipient_role)` constraint.

## Kafka event contract

Publish JSON messages with `eventId`, `eventType`, `occurredAt`, `entityType`, `entityId`, `entityName`, and optional `payload`.

Supported types: `APP_CREATED`, `APP_UPDATED`, `APP_DELETED`, `EDA_CREATED`, `MODEL_PUBLISHED`, `MODEL_DELETED`.

Topics default to `application-events,eda-events,evaluation-events,model-events`. Events are role-targeted by the consumer mapping in `src/consumer.js`.

## Configuration

Set `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_ADMIN_DB`, `KAFKA_BOOTSTRAP_SERVERS`, `KEYCLOAK_ISSUER`, and `KEYCLOAK_JWKS_URL` in the compose environment.
