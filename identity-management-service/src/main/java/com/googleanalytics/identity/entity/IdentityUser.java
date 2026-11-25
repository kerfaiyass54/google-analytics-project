package com.googleanalytics.identity.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "identity_users", indexes = @Index(name = "idx_identity_users_username", columnList = "username", unique = true))
public class IdentityUser {
    @Id @Column(length = 64) private String id;
    @Column(nullable = false, length = 120) private String username;
    @Column(length = 180) private String email;
    @Column(name = "first_name", length = 100) private String firstName;
    @Column(name = "last_name", length = 100) private String lastName;
    @Column(nullable = false) private boolean enabled;
    @Column(name = "email_verified", nullable = false) private boolean emailVerified;
    @Column(name = "created_at") private Instant createdAt;
    @Column(name = "last_synced_at", nullable = false) private Instant lastSyncedAt;

    protected IdentityUser() {}
    public IdentityUser(String id) { this.id = id; }
    public void synchronize(String username, String email, String firstName, String lastName, boolean enabled, boolean emailVerified, Instant createdAt) {
        this.username = username; this.email = email; this.firstName = firstName; this.lastName = lastName;
        this.enabled = enabled; this.emailVerified = emailVerified; this.createdAt = createdAt; this.lastSyncedAt = Instant.now();
    }
    public String getId() { return id; }
    public String getUsername() { return username; }
    public String getEmail() { return email; }
    public String getFirstName() { return firstName; }
    public String getLastName() { return lastName; }
    public boolean isEnabled() { return enabled; }
    public boolean isEmailVerified() { return emailVerified; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getLastSyncedAt() { return lastSyncedAt; }
}
