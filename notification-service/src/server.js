import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { randomUUID } from 'node:crypto';
import { initializeDatabase, pool } from './db.js';
import { authenticate } from './auth.js';
import { startConsumer } from './consumer.js';

const app = express();
app.use(cors({ origin: (process.env.CORS_ORIGINS || 'http://localhost:4200').split(','), credentials: true }));
app.use(express.json());
const streams = new Map();

app.get('/health', async (_req, res) => {
  try { await pool.query('SELECT 1'); res.json({ status: 'UP', database: 'connected' }); }
  catch { res.status(503).json({ status: 'DOWN' }); }
});
app.use('/api/notifications', authenticate);

app.get('/api/notifications', async (req, res, next) => {
  try {
    const limit = Math.min(Math.max(Number(req.query.limit) || 20, 1), 100);
    const unreadOnly = req.query.unread === 'true';
    const result = await pool.query(
      `SELECT id, event_id, event_type, title, message, entity_type, entity_id, payload, created_at, read_at
       FROM notifications WHERE recipient_role = $1 ${unreadOnly ? 'AND read_at IS NULL' : ''}
       ORDER BY created_at DESC LIMIT $2`, [req.identity.role, limit]);
    res.json(result.rows);
  } catch (error) { next(error); }
});
app.get('/api/notifications/unread-count', async (req, res, next) => {
  try {
    const result = await pool.query('SELECT COUNT(*)::int AS count FROM notifications WHERE recipient_role=$1 AND read_at IS NULL', [req.identity.role]);
    res.json(result.rows[0]);
  } catch (error) { next(error); }
});
app.patch('/api/notifications/:id/read', async (req, res, next) => {
  try {
    const result = await pool.query(
      'UPDATE notifications SET read_at=NOW() WHERE id=$1 AND recipient_role=$2 RETURNING id, read_at',
      [req.params.id, req.identity.role]);
    if (!result.rowCount) return res.status(404).json({ message: 'Notification not found.' });
    res.json(result.rows[0]);
  } catch (error) { next(error); }
});
app.patch('/api/notifications/read-all', async (req, res, next) => {
  try {
    const result = await pool.query('UPDATE notifications SET read_at=NOW() WHERE recipient_role=$1 AND read_at IS NULL', [req.identity.role]);
    res.json({ updated: result.rowCount });
  } catch (error) { next(error); }
});
app.get('/api/notifications/stream', (req, res) => {
  // EventSource cannot attach Authorization headers; use the authenticated fetch-based polling fallback.
  res.status(501).json({ message: 'Use the authenticated notification polling endpoint.' });
});

app.use((error, _req, res, _next) => {
  console.error(error);
  res.status(500).json({ message: 'Notification service request failed.' });
});

const port = Number(process.env.PORT || 8030);
await initializeDatabase();
await startConsumer();
app.listen(port, '0.0.0.0', () => console.info(`Notification service listening on ${port}`));

async function shutdown() {
  for (const responseSet of streams.values()) for (const response of responseSet) response.end();
  await pool.end();
  process.exit(0);
}
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
