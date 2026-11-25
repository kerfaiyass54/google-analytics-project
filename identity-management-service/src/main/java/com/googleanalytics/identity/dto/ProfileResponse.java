package com.googleanalytics.identity.dto;

import java.time.Instant;

public record ProfileResponse(String id, String username, String email, String firstName, String lastName,
                              boolean enabled, boolean emailVerified, Instant createdAt) {}
