package com.googleanalytics.analyticsforgoogle.services;


import com.googleanalytics.analyticsforgoogle.entities.GooglePlayApp;
import com.googleanalytics.analyticsforgoogle.repositories.GooglePlayAppRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class GooglePlayAppImportService {

    private static final String DATASET =
            "googleplaystore.csv";

    private static final int EXPECTED_COLUMNS = 13;

    private final GooglePlayAppRepository repository;
    private final GooglePlayAppCleaner cleaner;

    @Transactional
    public void importIfEmpty() {

        /*
         * IMPORTANT:
         *
         * If the table already contains data,
         * the CSV is not processed.
         */
        if (repository.count() > 0) {

            log.info(
                    "Google Play Store table already contains data. "
                            + "Import skipped."
            );

            return;
        }

        log.info("Google Play Store table is empty.");
        log.info("Starting dataset cleaning and import...");

        List<GooglePlayApp> validApps = new ArrayList<>();

        int totalRows = 0;
        int invalidRows = 0;
        int duplicateRows = 0;

        /*
         * Used to remove duplicated applications.
         */
        Set<String> existingApps = new HashSet<>();

        try (
                BufferedReader reader = new BufferedReader(
                        new InputStreamReader(
                                new ClassPathResource(DATASET)
                                        .getInputStream(),
                                StandardCharsets.UTF_8
                        )
                );

                CSVParser parser = CSVFormat.DEFAULT.builder()
                        .setHeader()
                        .setSkipHeaderRecord(true)
                        .setIgnoreEmptyLines(true)
                        .setTrim(true)
                        .build()
                        .parse(reader)
        ) {

            for (CSVRecord record : parser) {

                totalRows++;

                /*
                 * Check the number of columns.
                 */
                if (record.size() != EXPECTED_COLUMNS) {

                    invalidRows++;

                    log.debug(
                            "Skipping row {}: expected {} columns, found {}.",
                            record.getRecordNumber(),
                            EXPECTED_COLUMNS,
                            record.size()
                    );

                    continue;
                }

                try {

                    String app =
                            record.get("App").trim();

                    /*
                     * Remove duplicate applications.
                     */
                    String duplicateKey =
                            app.toLowerCase(Locale.ENGLISH);

                    if (!existingApps.add(duplicateKey)) {

                        duplicateRows++;

                        continue;
                    }

                    GooglePlayApp cleanedApp =
                            cleaner.clean(
                                    record.get("App"),
                                    record.get("Category"),
                                    record.get("Rating"),
                                    record.get("Reviews"),
                                    record.get("Size"),
                                    record.get("Installs"),
                                    record.get("Type"),
                                    record.get("Price"),
                                    record.get("Content Rating"),
                                    record.get("Genres"),
                                    record.get("Last Updated"),
                                    record.get("Current Ver"),
                                    record.get("Android Ver")
                            );

                    /*
                     * null means:
                     *
                     * - missing data
                     * - invalid date
                     * - invalid number
                     * - invalid size
                     * - invalid price
                     * - invalid type
                     * - invalid rating
                     */
                    if (cleanedApp == null) {

                        invalidRows++;

                        continue;
                    }

                    validApps.add(cleanedApp);

                } catch (RuntimeException exception) {

                    invalidRows++;

                    log.debug(
                            "Skipping malformed row {}.",
                            record.getRecordNumber(),
                            exception
                    );
                }
            }

            repository.saveAll(validApps);

            log.info("========================================");
            log.info("Google Play Store import completed.");
            log.info("Total rows       : {}", totalRows);
            log.info("Valid rows       : {}", validApps.size());
            log.info("Invalid rows     : {}", invalidRows);
            log.info("Duplicate rows   : {}", duplicateRows);
            log.info("Inserted rows    : {}", validApps.size());
            log.info("========================================");

        } catch (Exception exception) {

            log.error(
                    "Google Play Store dataset import failed.",
                    exception
            );

            throw new IllegalStateException(
                    "Unable to import Google Play Store dataset.",
                    exception
            );
        }
    }
}