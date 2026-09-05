package com.googleanalytics.analyticsforgoogle.controllers;

import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppStatisticsResponse;
import com.googleanalytics.analyticsforgoogle.services.GooglePlayAppStatisticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/google-play-apps/statistics")
@RequiredArgsConstructor
public class GooglePlayAppStatisticsController {

    private final GooglePlayAppStatisticsService statisticsService;

    @GetMapping
    public ResponseEntity<GooglePlayAppStatisticsResponse> getStatistics() {

        return ResponseEntity.ok(
                statisticsService.getStatistics()
        );
    }
}