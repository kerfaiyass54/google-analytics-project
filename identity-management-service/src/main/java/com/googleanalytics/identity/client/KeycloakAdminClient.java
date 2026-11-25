package com.googleanalytics.identity.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.googleanalytics.identity.config.KeycloakProperties;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.client.RestClient;

@Component
public class KeycloakAdminClient {
    private final RestClient client;
    private final KeycloakProperties properties;
    private final ObjectMapper mapper;
    private volatile String cachedToken;
    private volatile Instant tokenExpiresAt = Instant.EPOCH;

    public KeycloakAdminClient(RestClient keycloakRestClient, KeycloakProperties properties, ObjectMapper mapper) {
        this.client = keycloakRestClient;
        this.properties = properties;
        this.mapper = mapper;
    }

    public List<JsonNode> fetchAllUsers() {
        List<JsonNode> users = new ArrayList<>();
        int first = 0;
        int pageSize = 100;
        while (true) {
            JsonNode page = client.get()
                .uri(adminBase() + "/users?first=" + first + "&max=" + pageSize)
                .headers(headers -> headers.setBearerAuth(adminToken()))
                .retrieve().body(JsonNode.class);
            if (page == null || !page.isArray() || page.isEmpty()) break;
            page.forEach(users::add);
            if (page.size() < pageSize) break;
            first += pageSize;
        }
        return users;
    }

    public JsonNode fetchUserSessions(String userId) {
        return client.get().uri(adminBase() + "/users/{id}/sessions", userId)
            .headers(headers -> headers.setBearerAuth(adminToken()))
            .retrieve().body(JsonNode.class);
    }

    public JsonNode updateUser(String userId, Map<String, Object> profile) {
        client.put().uri(adminBase() + "/users/{id}", userId)
            .headers(headers -> headers.setBearerAuth(adminToken()))
            .contentType(MediaType.APPLICATION_JSON).body(profile).retrieve().toBodilessEntity();
        return client.get().uri(adminBase() + "/users/{id}", userId)
            .headers(headers -> headers.setBearerAuth(adminToken()))
            .retrieve().body(JsonNode.class);
    }

    public void sendPasswordResetEmail(String userId) {
        client.put().uri(uriBuilder -> uriBuilder
                .path(adminBase() + "/users/{id}/execute-actions-email")
                .queryParam("client_id", properties.frontendClientId())
                .queryParam("redirect_uri", properties.frontendRedirectUri())
                .build(userId))
            .headers(headers -> headers.setBearerAuth(adminToken()))
            .contentType(MediaType.APPLICATION_JSON)
            .body(List.of("UPDATE_PASSWORD"))
            .retrieve().toBodilessEntity();
    }

    private String adminToken() {
        if (cachedToken != null && Instant.now().isBefore(tokenExpiresAt.minusSeconds(30))) return cachedToken;
        if (properties.clientSecret() == null || properties.clientSecret().isBlank()) {
            throw new IllegalStateException("KEYCLOAK_ADMIN_CLIENT_SECRET must be configured.");
        }
        var form = new LinkedMultiValueMap<String, String>();
        form.add("grant_type", "client_credentials");
        form.add("client_id", properties.clientId());
        form.add("client_secret", properties.clientSecret());
        JsonNode token = client.post()
            .uri(properties.baseUrl() + "/realms/" + properties.realm() + "/protocol/openid-connect/token")
            .contentType(MediaType.APPLICATION_FORM_URLENCODED).body(form)
            .retrieve().body(JsonNode.class);
        if (token == null || !token.hasNonNull("access_token")) throw new IllegalStateException("Keycloak did not return an admin access token.");
        cachedToken = token.get("access_token").asText();
        tokenExpiresAt = Instant.now().plusSeconds(token.path("expires_in").asLong(60));
        return cachedToken;
    }

    private String adminBase() {
        return properties.baseUrl() + "/admin/realms/" + properties.realm();
    }
}
