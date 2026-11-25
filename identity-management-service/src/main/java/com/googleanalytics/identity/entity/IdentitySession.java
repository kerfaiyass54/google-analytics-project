package com.googleanalytics.identity.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "identity_sessions", indexes = {
    @Index(name = "idx_identity_sessions_user", columnList = "user_id"),
    @Index(name = "idx_identity_sessions_status", columnList = "status"),
    @Index(name = "idx_identity_sessions_started", columnList = "started_at")
})
public class IdentitySession {
    @Id @Column(length = 80) private String id;
    @Column(name = "user_id", nullable = false, length = 64) private String userId;
    @Column(name = "ip_address", length = 64) private String ipAddress;
    @Column(name = "started_at") private Instant startedAt;
    @Column(name = "last_access_at") private Instant lastAccessAt;
    @Column(name = "closed_at") private Instant closedAt;
    @Column(length = 16, nullable = false) private String status;
    @Column(length = 500) private String clients;

    protected IdentitySession() {}
    public IdentitySession(String id) { this.id = id; }
    public void markActive(String userId, String ipAddress, Instant startedAt, Instant lastAccessAt, String clients) {
        this.userId = userId; this.ipAddress = ipAddress; this.startedAt = startedAt;
        this.lastAccessAt = lastAccessAt; this.clients = clients; this.status = "ACTIVE"; this.closedAt = null;
    }
    public void markClosed(Instant at) { this.status = "CLOSED"; this.closedAt = at; }
    public String getId() { return id; }
    public String getUserId() { return userId; }
    public String getIpAddress() { return ipAddress; }
    public Instant getStartedAt() { return startedAt; }
    public Instant getLastAccessAt() { return lastAccessAt; }
    public Instant getClosedAt() { return closedAt; }
    public String getStatus() { return status; }
    public String getClients() { return clients; }
}
