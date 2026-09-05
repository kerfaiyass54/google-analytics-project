package com.googleanalytics.analyticsforgoogle.mapper;


import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppRequest;
import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppResponse;
import com.googleanalytics.analyticsforgoogle.entities.GooglePlayApp;
import org.springframework.stereotype.Component;

@Component
public class GooglePlayAppMapper {

    public GooglePlayApp toEntity(
            GooglePlayAppRequest request
    ) {

        return GooglePlayApp.builder()
                .app(request.app().trim())
                .category(request.category().trim())
                .rating(request.rating())
                .reviews(request.reviews())
                .sizeMb(request.sizeMb())
                .installs(request.installs().trim())
                .type(request.type())
                .price(request.price())
                .contentRating(request.contentRating().trim())
                .genres(request.genres().trim())
                .lastUpdated(request.lastUpdated())
                .currentVersion(request.currentVersion().trim())
                .androidVersion(request.androidVersion().trim())
                .build();
    }

    public GooglePlayAppResponse toResponse(
            GooglePlayApp entity
    ) {

        return new GooglePlayAppResponse(
                entity.getId(),
                entity.getApp(),
                entity.getCategory(),
                entity.getRating(),
                entity.getReviews(),
                entity.getSizeMb(),
                entity.getInstalls(),
                entity.getType(),
                entity.getPrice(),
                entity.getContentRating(),
                entity.getGenres(),
                entity.getLastUpdated(),
                entity.getCurrentVersion(),
                entity.getAndroidVersion()
        );
    }

    public void updateEntity(
            GooglePlayApp entity,
            GooglePlayAppRequest request
    ) {

        entity.setApp(request.app().trim());
        entity.setCategory(request.category().trim());
        entity.setRating(request.rating());
        entity.setReviews(request.reviews());
        entity.setSizeMb(request.sizeMb());
        entity.setInstalls(request.installs().trim());
        entity.setType(request.type());
        entity.setPrice(request.price());
        entity.setContentRating(request.contentRating().trim());
        entity.setGenres(request.genres().trim());
        entity.setLastUpdated(request.lastUpdated());
        entity.setCurrentVersion(request.currentVersion().trim());
        entity.setAndroidVersion(request.androidVersion().trim());
    }
}