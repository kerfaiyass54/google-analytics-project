import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { initializeDatabase, pool } from './db.js';
import { authenticate } from './auth.js';
import { startConsumer } from './consumer.js';

const app = express();
app.use(cors({ origin: (process.env.CORS_ORIGINS || 'http://localhost:4200').split(','), credentials: true }));
app.use(express.json());

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
      `SELECT n.id, n.event_id, n.event_type, n.title, n.message, n.entity_type, n.entity_id,
              n.payload, n.created_at, r.read_at
       FROM notifications n
       LEFT JOIN notification_reads r ON r.notification_id = n.id AND r.user_id = $2
       WHERE n.recipient_role = $1 ${unreadOnly ? 'AND r.read_at IS NULL' : ''}
       ORDER BY n.created_at DESC LIMIT $3`, [req.identity.role, req.identity.userId, limit]);
    res.json(result.rows);
  } catch (error) { next(error); }
});
app.get('/api/notifications/unread-count', async (req, res, next) => {
  try {
    const result = await pool.query('SELECT COUNT(*)::int AS count FROM notifications n WHERE n.recipient_role=$1 AND NOT EXISTS (SELECT 1 FROM notification_reads r WHERE r.notification_id=n.id AND r.user_id=$2)', [req.identity.role, req.identity.userId]);
    res.json(result.rows[0]);
  } catch (error) { next(error); }
});
app.patch('/api/notifications/:id/read', async (req, res, next) => {
  try {
    const exists = await pool.query('SELECT id FROM notifications WHERE id=$1 AND recipient_role=$2', [req.params.id, req.identity.role]);
    if (!exists.rowCount) return res.status(404).json({ message: 'Notification not found.' });
    const result = await pool.query(
      `INSERT INTO notification_reads (notification_id, user_id) VALUES ($1,$2)
       ON CONFLICT (notification_id,user_id) DO UPDATE SET read_at=notification_reads.read_at
       RETURNING notification_id AS id, read_at`,
      [req.params.id, req.identity.userId]);
    res.json(result.rows[0]);
  } catch (error) { next(error); }
});
app.patch('/api/notifications/read-all', async (req, res, next) => {
  try {
    const result = await pool.query(
      `INSERT INTO notification_reads (notification_id,user_id)
       SELECT n.id,$2 FROM notifications n
       WHERE n.recipient_role=$1
         AND NOT EXISTS (SELECT 1 FROM notification_reads r WHERE r.notification_id=n.id AND r.user_id=$2)
       ON CONFLICT (notification_id,user_id) DO NOTHING`,
      [req.identity.role, req.identity.userId]);
    res.json({ updated: result.rowCount });
  } catch (error) { next(error); }
});
app.use((error, _req, res, _next) => {
  console.error(error);
  res.status(500).json({ message: 'Notification service request failed.' });
});

const port = Number(process.env.PORT || 8030);
await initializeDatabase();
app.listen(port, '0.0.0.0', () => console.info(`Notification service listening on ${port}`));
startConsumer().catch(error => console.error('Kafka consumer stopped:', error));

async function shutdown() {
  await pool.end();
  process.exit(0);
}
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
