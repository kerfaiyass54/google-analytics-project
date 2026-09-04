package com.googleanalytics.analyticsforgoogle.configurations;


import com.googleanalytics.analyticsforgoogle.services.GooglePlayAppImportService;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class GooglePlayDatasetInitializer
        implements CommandLineRunner {

    private final GooglePlayAppImportService importService;

    @Override
    public void run(String... args) {

        importService.importIfEmpty();
    }
}