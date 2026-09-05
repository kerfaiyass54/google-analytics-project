package com.googleanalytics.analyticsforgoogle.dtos;

import com.googleanalytics.analyticsforgoogle.enums.AppType;
import jakarta.validation.constraints.*;
import org.apache.logging.log4j.core.config.plugins.validation.constraints.NotBlank;

import java.math.BigDecimal;
import java.time.LocalDate;

public record GooglePlayAppRequest(

        @NotBlank(message = "App name is required")
        @Size(max = 255, message = "App name must not exceed 255 characters")
        String app,

        @NotBlank(message = "Category is required")
        @Size(max = 100, message = "Category must not exceed 100 characters")
        String category,

        @NotNull(message = "Rating is required")
        @DecimalMin(value = "0.0", message = "Rating must be at least 0")
        @DecimalMax(value = "5.0", message = "Rating must not exceed 5")
        Double rating,

        @NotNull(message = "Reviews is required")
        @PositiveOrZero(message = "Reviews cannot be negative")
        Long reviews,

        @NotNull(message = "Size is required")
        @PositiveOrZero(message = "Size cannot be negative")
        Double sizeMb,

        @NotBlank(message = "Installs is required")
        @Size(max = 50, message = "Installs must not exceed 50 characters")
        String installs,

        @NotNull(message = "Type is required")
        AppType type,

        @NotNull(message = "Price is required")
        @DecimalMin(value = "0.00", message = "Price cannot be negative")
        @Digits(
                integer = 8,
                fraction = 2,
                message = "Price must have at most 8 integer digits and 2 decimal digits"
        )
        BigDecimal price,

        @NotBlank(message = "Content rating is required")
        @Size(max = 50, message = "Content rating must not exceed 50 characters")
        String contentRating,

        @NotBlank(message = "Genres are required")
        @Size(max = 255, message = "Genres must not exceed 255 characters")
        String genres,

        @NotNull(message = "Last updated date is required")
        LocalDate lastUpdated,

        @NotBlank(message = "Current version is required")
        @Size(max = 100, message = "Current version must not exceed 100 characters")
        String currentVersion,

        @NotBlank(message = "Android version is required")
        @Size(max = 100, message = "Android version must not exceed 100 characters")
        String androidVersion
) {
}