package com.googleanalytics.identity.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.googleanalytics.identity.client.KeycloakAdminClient;
import com.googleanalytics.identity.dto.ProfileResponse;
import com.googleanalytics.identity.dto.ProfileUpdateRequest;
import com.googleanalytics.identity.entity.IdentityUser;
import com.googleanalytics.identity.repository.IdentityUserRepository;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProfileService {
    private final KeycloakAdminClient keycloak;
    private final IdentityUserRepository users;

    public ProfileService(KeycloakAdminClient keycloak, IdentityUserRepository users) {
        this.keycloak = keycloak; this.users = users;
    }

    public ProfileResponse getProfile(String userId) {
        IdentityUser user = users.findById(userId).orElseThrow(() -> new IllegalStateException("Profile is being synchronized. Please retry shortly."));
        return toResponse(user);
    }

    @Transactional
    public ProfileResponse updateProfile(String userId, ProfileUpdateRequest request) {
        IdentityUser user = users.findById(userId).orElseGet(() -> new IdentityUser(userId));
        boolean emailChanged = !java.util.Objects.equals(user.getEmail() == null ? null : user.getEmail().toLowerCase(java.util.Locale.ROOT), request.email().trim().toLowerCase(java.util.Locale.ROOT));
        JsonNode updated = keycloak.updateUser(userId, Map.of(
            "firstName", request.firstName().trim(),
            "lastName", request.lastName().trim(),
            "email", request.email().trim(),
            "emailVerified", emailChanged ? false : user.isEmailVerified()
        ));
        if (emailChanged) keycloak.sendVerificationEmail(userId);
        user.synchronize(updated.path("username").asText(user.getUsername()),
            updated.path("email").asText(request.email()), updated.path("firstName").asText(request.firstName()),
            updated.path("lastName").asText(request.lastName()), updated.path("enabled").asBoolean(true),
            updated.path("emailVerified").asBoolean(false),
            updated.hasNonNull("createdTimestamp") ? java.time.Instant.ofEpochMilli(updated.path("createdTimestamp").asLong()) : null);
        users.save(user);
        return toResponse(user);
    }

    public void requestPasswordReset(String userId) {
        keycloak.sendPasswordResetEmail(userId);
    }

    private ProfileResponse toResponse(IdentityUser user) {
        return new ProfileResponse(user.getId(), user.getUsername(), user.getEmail(), user.getFirstName(),
            user.getLastName(), user.isEnabled(), user.isEmailVerified(), user.getCreatedAt());
    }
}
