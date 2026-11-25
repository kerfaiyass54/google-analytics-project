package com.googleanalytics.identity.dto;

import java.time.Instant;

public record SessionResponse(String id, String ipAddress, Instant startedAt, Instant lastAccessAt,
                              Instant closedAt, String status, String clients) {}
