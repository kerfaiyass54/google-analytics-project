package com.googleanalytics.identity.dto;

import java.util.List;

public record SessionSummaryResponse(long active, long closed, List<DailySessionCount> daily) {
    public record DailySessionCount(String date, long active, long closed) {}
}
