package com.googleanalytics.identity.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "identity.keycloak")
public record KeycloakProperties(String baseUrl, String realm, String clientId, String clientSecret, long syncIntervalMs) {}
