package com.googleanalytics.analyticsforgoogle.services;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class NotificationEventPublisher {

    private final KafkaTemplate<Object, Object> kafkaTemplate;

    public void publishAfterCommit(String eventType, Long appId, String appName) {
        Runnable publish = () -> {
            Map<String, Object> event = Map.of(
                    "eventId", UUID.randomUUID().toString(),
                    "eventType", eventType,
                    "occurredAt", Instant.now().toString(),
                    "entityType", "APPLICATION",
                    "entityId", String.valueOf(appId),
                    "entityName", appName == null ? "application" : appName,
                    "payload", Map.of("appId", appId, "app", appName == null ? "application" : appName)
            );
            kafkaTemplate.send("application-events", String.valueOf(appId), event)
                    .whenComplete((result, error) -> {
                        if (error != null) log.error("Failed to publish {} notification event for app {}", eventType, appId, error);
                    });
        };

        if (TransactionSynchronizationManager.isSynchronizationActive()) {
            TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
                @Override
                public void afterCommit() { publish.run(); }
            });
        } else {
            publish.run();
        }
    }
}
