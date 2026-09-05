package com.googleanalytics.analyticsforgoogle.services;

import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppStatisticsResponse;
import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppStatisticsResponse.CategoryStatistics;
import com.googleanalytics.analyticsforgoogle.repositories.GooglePlayAppRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class GooglePlayAppStatisticsService {

    private final GooglePlayAppRepository repository;

    public GooglePlayAppStatisticsResponse getStatistics() {

        long totalApps = repository.count();

        long freeApps =
                repository.countFreeApps();

        long paidApps =
                repository.countPaidApps();

        Double averageRating =
                repository.findAverageRating();

        Double minimumRating =
                repository.findMinimumRating();

        Double maximumRating =
                repository.findMaximumRating();

        Double averageReviews =
                repository.findAverageReviews();

        Long minimumReviews =
                repository.findMinimumReviews();

        Long maximumReviews =
                repository.findMaximumReviews();

        Double averageSizeMb =
                repository.findAverageSizeMb();

        Double minimumSizeMb =
                repository.findMinimumSizeMb();

        Double maximumSizeMb =
                repository.findMaximumSizeMb();

        BigDecimal averagePrice =
                repository.findAveragePrice();

        BigDecimal minimumPrice =
                repository.findMinimumPrice();

        BigDecimal maximumPrice =
                repository.findMaximumPrice();

        LocalDate oldestLastUpdated =
                repository.findOldestLastUpdated();

        LocalDate newestLastUpdated =
                repository.findNewestLastUpdated();

        List<CategoryStatistics> categories =
                repository.findCategoryStatistics();

        return new GooglePlayAppStatisticsResponse(
                totalApps,
                freeApps,
                paidApps,
                defaultDouble(averageRating),
                defaultDouble(minimumRating),
                defaultDouble(maximumRating),
                defaultDouble(averageReviews),
                defaultLong(minimumReviews),
                defaultLong(maximumReviews),
                defaultDouble(averageSizeMb),
                defaultDouble(minimumSizeMb),
                defaultDouble(maximumSizeMb),
                defaultBigDecimal(averagePrice),
                defaultBigDecimal(minimumPrice),
                defaultBigDecimal(maximumPrice),
                oldestLastUpdated,
                newestLastUpdated,
                categories
        );
    }

    private double defaultDouble(Double value) {
        return value != null ? value : 0.0;
    }

    private long defaultLong(Long value) {
        return value != null ? value : 0L;
    }

    private BigDecimal defaultBigDecimal(BigDecimal value) {
        return value != null
                ? value
                : BigDecimal.ZERO;
    }
}