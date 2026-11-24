import { Kafka } from 'kafkajs';
import { randomUUID } from 'node:crypto';
import { pool } from './db.js';

const topics = (process.env.KAFKA_NOTIFICATION_TOPICS || 'application-events,eda-events,evaluation-events,model-events')
  .split(',').map(value => value.trim()).filter(Boolean);
const kafka = new Kafka({
  clientId: 'analytics-notification-service',
  brokers: (process.env.KAFKA_BOOTSTRAP_SERVERS || 'localhost:9099').split(',')
});
const consumer = kafka.consumer({ groupId: process.env.KAFKA_NOTIFICATION_GROUP || 'analytics-notifications-v1' });

const definitions = {
  APP_CREATED: { role: 'ADMIN', title: 'New application added', message: e => `A new application "${e.entityName || e.payload?.app || 'application'}" was added.` },
  APP_UPDATED: { role: 'ADMIN', title: 'Application updated', message: e => `Application "${e.entityName || e.payload?.app || 'application'}" was updated.` },
  APP_DELETED: { role: 'USER', title: 'Application removed', message: e => `Application "${e.entityName || e.payload?.app || 'application'}" is no longer available.` },
  EDA_CREATED: { role: 'ADMIN', title: 'New EDA analysis completed', message: e => `A new EDA analysis was created (${e.entityId || 'new analysis'}).` },
  MODEL_PUBLISHED: { role: 'USER', title: 'New prediction model available', message: e => `A new ${e.payload?.task || 'prediction'} model is now available.` },
  MODEL_DELETED: { role: 'USER', title: 'Prediction model removed', message: e => `A prediction model (${e.entityId || 'model'}) was removed.` }
};

async function persist(event) {
  const type = String(event.eventType || event.type || '').toUpperCase();
  const definition = definitions[type];
  if (!definition) return;
  const eventId = String(event.eventId || event.id || randomUUID());
  const title = definition.title;
  const message = definition.message(event);
  await pool.query(
    `INSERT INTO notifications
      (id, event_id, recipient_role, event_type, title, message, entity_type, entity_id, payload, created_at)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9::jsonb,COALESCE($10::timestamptz,NOW()))
     ON CONFLICT (event_id, recipient_role) DO NOTHING`,
    [randomUUID(), eventId, definition.role, type, title, message,
      event.entityType || null, event.entityId || null, JSON.stringify(event.payload || {}),
      event.occurredAt || event.createdAt || null]
  );
}

export async function startConsumer() {
  while (true) {
    try { await consumer.connect(); break; }
    catch (error) {
      console.error('Kafka is not ready yet; retrying in 5 seconds.', error.message);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
  for (const topic of topics) await consumer.subscribe({ topic, fromBeginning: false });
  await consumer.run({
    eachMessage: async ({ message }) => {
      if (!message.value) return;
      const event = JSON.parse(message.value.toString());
      await persist(event);
    }
  });
  console.info('Notification consumer subscribed:', topics.join(', '));
}
