package com.googleanalytics.analyticsforgoogle.services;


import com.googleanalytics.analyticsforgoogle.entities.GooglePlayApp;
import com.googleanalytics.analyticsforgoogle.enums.AppType;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Locale;

@Service
public class GooglePlayAppCleaner {

    private static final DateTimeFormatter DATE_FORMATTER =
            DateTimeFormatter.ofPattern("MMMM d, yyyy", Locale.ENGLISH);

    public GooglePlayApp clean(
            String app,
            String category,
            String rating,
            String reviews,
            String size,
            String installs,
            String type,
            String price,
            String contentRating,
            String genres,
            String lastUpdated,
            String currentVersion,
            String androidVersion
    ) {

        /*
         * Missing values:
         * Reject the entire row.
         */
        if (isBlank(app)
                || isBlank(category)
                || isBlank(rating)
                || isBlank(reviews)
                || isBlank(size)
                || isBlank(installs)
                || isBlank(type)
                || isBlank(price)
                || isBlank(contentRating)
                || isBlank(genres)
                || isBlank(lastUpdated)
                || isBlank(currentVersion)
                || isBlank(androidVersion)) {

            return null;
        }

        try {

            Double cleanedRating = parseRating(rating);

            Long cleanedReviews = parseReviews(reviews);

            Double cleanedSize = parseSize(size);

            AppType cleanedType = parseType(type);

            BigDecimal cleanedPrice = parsePrice(price);

            LocalDate cleanedDate = parseDate(lastUpdated);

            /*
             * Any invalid value causes the complete row
             * to be rejected.
             */
            if (cleanedRating == null
                    || cleanedReviews == null
                    || cleanedSize == null
                    || cleanedType == null
                    || cleanedPrice == null
                    || cleanedDate == null) {

                return null;
            }

            return GooglePlayApp.builder()
                    .app(app.trim())
                    .category(category.trim())
                    .rating(cleanedRating)
                    .reviews(cleanedReviews)
                    .sizeMb(cleanedSize)
                    .installs(installs.trim())
                    .type(cleanedType)
                    .price(cleanedPrice)
                    .contentRating(contentRating.trim())
                    .genres(genres.trim())
                    .lastUpdated(cleanedDate)
                    .currentVersion(currentVersion.trim())
                    .androidVersion(androidVersion.trim())
                    .build();

        } catch (RuntimeException exception) {

            /*
             * Malformed/inconsistent row.
             * Do not insert it.
             */
            return null;
        }
    }

    private Double parseRating(String value) {

        double rating = Double.parseDouble(value.trim());

        /*
         * Google Play ratings must logically be between 0 and 5.
         */
        if (rating < 0 || rating > 5) {
            return null;
        }

        return rating;
    }

    private Long parseReviews(String value) {

        return Long.parseLong(value.trim());
    }

    private Double parseSize(String value) {

        String normalized = value
                .trim()
                .toUpperCase(Locale.ENGLISH);

        /*
         * "Varies with device" cannot be converted to Double.
         * Therefore the row is rejected.
         */
        if (normalized.equals("VARIES WITH DEVICE")) {
            return null;
        }

        if (normalized.endsWith("M")) {

            String numericPart =
                    normalized.substring(0, normalized.length() - 1);

            return Double.parseDouble(numericPart);
        }

        if (normalized.endsWith("K")) {

            String numericPart =
                    normalized.substring(0, normalized.length() - 1);

            return Double.parseDouble(numericPart) / 1024.0;
        }

        return null;
    }

    private AppType parseType(String value) {

        return switch (value.trim().toLowerCase(Locale.ENGLISH)) {

            case "free" -> AppType.FREE;

            case "paid" -> AppType.PAID;

            default -> null;
        };
    }

    private BigDecimal parsePrice(String value) {

        String normalized = value
                .trim()
                .replace("$", "");

        BigDecimal price = new BigDecimal(normalized);

        if (price.compareTo(BigDecimal.ZERO) < 0) {
            return null;
        }

        return price;
    }

    private LocalDate parseDate(String value) {

        try {

            return LocalDate.parse(
                    value.trim(),
                    DATE_FORMATTER
            );

        } catch (DateTimeParseException exception) {

            /*
             * Example:
             *
             * January 7, 2018 -> valid
             * 12345            -> invalid
             * abc              -> invalid
             */
            return null;
        }
    }

    private boolean isBlank(String value) {

        return value == null || value.trim().isEmpty();
    }
}