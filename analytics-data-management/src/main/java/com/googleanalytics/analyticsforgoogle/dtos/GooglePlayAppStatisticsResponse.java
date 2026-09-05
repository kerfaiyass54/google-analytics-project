package com.googleanalytics.analyticsforgoogle.dtos;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public record GooglePlayAppStatisticsResponse(

        long totalApps,

        long freeApps,

        long paidApps,

        double averageRating,

        double minimumRating,

        double maximumRating,

        double averageReviews,

        long minimumReviews,

        long maximumReviews,

        double averageSizeMb,

        double minimumSizeMb,

        double maximumSizeMb,

        BigDecimal averagePrice,

        BigDecimal minimumPrice,

        BigDecimal maximumPrice,

        LocalDate oldestLastUpdated,

        LocalDate newestLastUpdated,

        List<CategoryStatistics> categories
) {

    public record CategoryStatistics(
            String category,
            long appCount,
            double averageRating,
            long totalReviews
    ) {
    }
}