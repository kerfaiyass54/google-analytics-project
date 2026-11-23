import pg from 'pg';
const { Pool, Client } = pg;

const database = process.env.NOTIFICATIONS_DB || 'notifications_db';
const admin = new Client({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: Number(process.env.POSTGRES_PORT || 5540),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD || 'postgres',
  database: process.env.POSTGRES_ADMIN_DB || 'postgres'
});

await admin.connect();
const exists = await admin.query('SELECT 1 FROM pg_database WHERE datname = $1', [database]);
if (!exists.rowCount) await admin.query('CREATE DATABASE "' + database.replace(/"/g, '""') + '"');
await admin.end();

export const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: Number(process.env.POSTGRES_PORT || 5540),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD || 'postgres',
  database,
  max: 10
});

export async function initializeDatabase() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS notifications (
      id UUID PRIMARY KEY,
      event_id VARCHAR(160) NOT NULL,
      recipient_role VARCHAR(32) NOT NULL,
      event_type VARCHAR(64) NOT NULL,
      title VARCHAR(200) NOT NULL,
      message TEXT NOT NULL,
      entity_type VARCHAR(64),
      entity_id VARCHAR(160),
      payload JSONB NOT NULL DEFAULT '{}'::jsonb,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      read_at TIMESTAMPTZ,
      CONSTRAINT uq_notifications_event_role UNIQUE (event_id, recipient_role)
    );
    CREATE INDEX IF NOT EXISTS idx_notifications_role_created
      ON notifications (recipient_role, created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_notifications_unread
      ON notifications (recipient_role, created_at DESC) WHERE read_at IS NULL;
  `);
}
