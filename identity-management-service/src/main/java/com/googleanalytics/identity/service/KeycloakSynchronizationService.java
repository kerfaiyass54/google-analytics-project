package com.googleanalytics.identity.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.googleanalytics.identity.client.KeycloakAdminClient;
import com.googleanalytics.identity.entity.IdentitySession;
import com.googleanalytics.identity.entity.IdentityUser;
import com.googleanalytics.identity.repository.IdentitySessionRepository;
import com.googleanalytics.identity.repository.IdentityUserRepository;
import java.time.Instant;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class KeycloakSynchronizationService {
    private final KeycloakAdminClient keycloak;
    private final IdentityUserRepository users;
    private final IdentitySessionRepository sessions;

    public KeycloakSynchronizationService(KeycloakAdminClient keycloak, IdentityUserRepository users, IdentitySessionRepository sessions) {
        this.keycloak = keycloak; this.users = users; this.sessions = sessions;
    }

    @Scheduled(fixedDelayString = "${identity.keycloak.sync-interval-ms:60000}", initialDelay = 15000)
    @Transactional
    public void synchronizeFromKeycloak() {
        Set<String> activeSessionIds = new HashSet<>();
        for (JsonNode source : keycloak.fetchAllUsers()) {
            String userId = text(source, "id");
            if (userId == null) continue;
            IdentityUser user = users.findById(userId).orElseGet(() -> new IdentityUser(userId));
            long createdMillis = source.path("createdTimestamp").asLong(0);
            user.synchronize(text(source, "username"), text(source, "email"), text(source, "firstName"),
                text(source, "lastName"), source.path("enabled").asBoolean(true),
                source.path("emailVerified").asBoolean(false), createdMillis > 0 ? Instant.ofEpochMilli(createdMillis) : null);
            users.save(user);

            JsonNode userSessions = keycloak.fetchUserSessions(userId);
            if (userSessions == null || !userSessions.isArray()) continue;
            for (JsonNode sourceSession : userSessions) {
                String sessionId = text(sourceSession, "id");
                if (sessionId == null) continue;
                activeSessionIds.add(sessionId);
                IdentitySession session = sessions.findById(sessionId).orElseGet(() -> new IdentitySession(sessionId));
                long started = sourceSession.path("start").asLong(0);
                long lastAccess = sourceSession.path("lastAccess").asLong(0);
                String clients = sourceSession.path("clients").isObject() ? sourceSession.path("clients").toString() : null;
                session.markActive(userId, text(sourceSession, "ipAddress"),
                    started > 0 ? sessionInstant(started) : Instant.now(),
                    lastAccess > 0 ? sessionInstant(lastAccess) : null, clients);
                sessions.save(session);
            }
        }

        Instant closedAt = Instant.now();
        for (IdentitySession session : sessions.findByStatus("ACTIVE")) {
            if (!activeSessionIds.contains(session.getId())) {
                session.markClosed(closedAt);
                sessions.save(session);
            }
        }
    }

    private Instant sessionInstant(long epoch) {
        return epoch < 10_000_000_000L ? Instant.ofEpochSecond(epoch) : Instant.ofEpochMilli(epoch);
    }

    private String text(JsonNode node, String field) {
        JsonNode value = node.get(field);
        return value == null || value.isNull() ? null : value.asText();
    }
}
