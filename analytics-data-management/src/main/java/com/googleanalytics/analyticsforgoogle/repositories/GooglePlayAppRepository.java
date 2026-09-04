package com.googleanalytics.analyticsforgoogle.repositories;

import com.googleanalytics.analyticsforgoogle.entities.GooglePlayApp;
import org.springframework.data.jpa.repository.JpaRepository;

public interface GooglePlayAppRepository
        extends JpaRepository<GooglePlayApp, Long> {
}