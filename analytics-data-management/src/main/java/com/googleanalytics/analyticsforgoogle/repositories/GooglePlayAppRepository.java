package com.googleanalytics.analyticsforgoogle.repositories;

import com.googleanalytics.analyticsforgoogle.entities.GooglePlayApp;
import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppStatisticsResponse.CategoryStatistics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public interface GooglePlayAppRepository
        extends JpaRepository<GooglePlayApp, Long> {

    boolean existsByAppIgnoreCase(String app);

    boolean existsByAppIgnoreCaseAndIdNot(
            String app,
            Long id
    );

    // =========================================================
    // GENERAL STATISTICS
    // =========================================================

    @Query("""
            SELECT AVG(a.rating)
            FROM GooglePlayApp a
            """)
    Double findAverageRating();

    @Query("""
            SELECT MIN(a.rating)
            FROM GooglePlayApp a
            """)
    Double findMinimumRating();

    @Query("""
            SELECT MAX(a.rating)
            FROM GooglePlayApp a
            """)
    Double findMaximumRating();

    // =========================================================
    // REVIEWS
    // =========================================================

    @Query("""
            SELECT AVG(a.reviews)
            FROM GooglePlayApp a
            """)
    Double findAverageReviews();

    @Query("""
            SELECT MIN(a.reviews)
            FROM GooglePlayApp a
            """)
    Long findMinimumReviews();

    @Query("""
            SELECT MAX(a.reviews)
            FROM GooglePlayApp a
            """)
    Long findMaximumReviews();

    // =========================================================
    // SIZE
    // =========================================================

    @Query("""
            SELECT AVG(a.sizeMb)
            FROM GooglePlayApp a
            """)
    Double findAverageSizeMb();

    @Query("""
            SELECT MIN(a.sizeMb)
            FROM GooglePlayApp a
            """)
    Double findMinimumSizeMb();

    @Query("""
            SELECT MAX(a.sizeMb)
            FROM GooglePlayApp a
            """)
    Double findMaximumSizeMb();

    // =========================================================
    // PRICE
    // =========================================================

    @Query("""
            SELECT AVG(a.price)
            FROM GooglePlayApp a
            """)
    BigDecimal findAveragePrice();

    @Query("""
            SELECT MIN(a.price)
            FROM GooglePlayApp a
            """)
    BigDecimal findMinimumPrice();

    @Query("""
            SELECT MAX(a.price)
            FROM GooglePlayApp a
            """)
    BigDecimal findMaximumPrice();

    // =========================================================
    // DATES
    // =========================================================

    @Query("""
            SELECT MIN(a.lastUpdated)
            FROM GooglePlayApp a
            """)
    LocalDate findOldestLastUpdated();

    @Query("""
            SELECT MAX(a.lastUpdated)
            FROM GooglePlayApp a
            """)
    LocalDate findNewestLastUpdated();

    // =========================================================
    // FREE / PAID
    // =========================================================

    @Query("""
            SELECT COUNT(a)
            FROM GooglePlayApp a
            WHERE a.type = com.googleanalytics.analyticsforgoogle.enums.AppType.FREE
            """)
    long countFreeApps();

    @Query("""
            SELECT COUNT(a)
            FROM GooglePlayApp a
            WHERE a.type = com.googleanalytics.analyticsforgoogle.enums.AppType.PAID
            """)
    long countPaidApps();

    // =========================================================
    // CATEGORY STATISTICS
    // =========================================================

    @Query("""
            SELECT new com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppStatisticsResponse$CategoryStatistics(
                a.category,
                COUNT(a),
                AVG(a.rating),
                SUM(a.reviews)
            )
            FROM GooglePlayApp a
            GROUP BY a.category
            ORDER BY COUNT(a) DESC
            """)
    List<CategoryStatistics> findCategoryStatistics();
}