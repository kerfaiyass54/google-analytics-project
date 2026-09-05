package com.googleanalytics.analyticsforgoogle.repositories;

import com.googleanalytics.analyticsforgoogle.entities.GooglePlayApp;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface GooglePlayAppRepository
        extends JpaRepository<GooglePlayApp, Long> {

    Optional<GooglePlayApp> findByAppIgnoreCase(String app);

    boolean existsByAppIgnoreCase(String app);

    boolean existsByAppIgnoreCaseAndIdNot(
            String app,
            Long id
    );
}