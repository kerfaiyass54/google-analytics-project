package com.googleanalytics.analyticsforgoogle.dtos;


import com.googleanalytics.analyticsforgoogle.enums.AppType;

import java.math.BigDecimal;
import java.time.LocalDate;

public record GooglePlayAppResponse(

        Long id,

        String app,

        String category,

        Double rating,

        Long reviews,

        Double sizeMb,

        String installs,

        AppType type,

        BigDecimal price,

        String contentRating,

        String genres,

        LocalDate lastUpdated,

        String currentVersion,

        String androidVersion
) {
}