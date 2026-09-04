package com.googleanalytics.analyticsforgoogle.entities;

import com.googleanalytics.analyticsforgoogle.enums.AppType;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(
        name = "google_play_apps",
        indexes = {
                @Index(name = "idx_app_category", columnList = "category"),
                @Index(name = "idx_app_rating", columnList = "rating"),
                @Index(name = "idx_app_last_updated", columnList = "last_updated")
        }
)
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class GooglePlayApp {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "app", nullable = false, length = 255)
    private String app;

    @Column(name = "category", nullable = false, length = 100)
    private String category;

    @Column(name = "rating", nullable = false)
    private Double rating;

    @Column(name = "reviews", nullable = false)
    private Long reviews;

    @Column(name = "size_mb", nullable = false)
    private Double sizeMb;

    @Column(name = "installs", nullable = false, length = 50)
    private String installs;

    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false, length = 20)
    private AppType type;

    @Column(name = "price", nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "content_rating", nullable = false, length = 50)
    private String contentRating;

    @Column(name = "genres", nullable = false, length = 255)
    private String genres;

    @Column(name = "last_updated", nullable = false)
    private LocalDate lastUpdated;

    @Column(name = "current_version", nullable = false, length = 100)
    private String currentVersion;

    @Column(name = "android_version", nullable = false, length = 100)
    private String androidVersion;
}