package com.googleanalytics.analyticsforgoogle.services;


import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppRequest;
import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppResponse;
import com.googleanalytics.analyticsforgoogle.entities.GooglePlayApp;
import com.googleanalytics.analyticsforgoogle.mapper.GooglePlayAppMapper;
import com.googleanalytics.analyticsforgoogle.repositories.GooglePlayAppRepository;
import lombok.RequiredArgsConstructor;
import org.apache.kafka.common.errors.DuplicateResourceException;
import org.apache.kafka.common.errors.ResourceNotFoundException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class GooglePlayAppService {

    private final GooglePlayAppRepository repository;

    private final GooglePlayAppMapper mapper;

    // =========================================================
    // CREATE
    // =========================================================

    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    @Transactional
    public GooglePlayAppResponse create(
            GooglePlayAppRequest request
    ) {

        String appName =
                request.app().trim();

        if (repository.existsByAppIgnoreCase(appName)) {

            throw new DuplicateResourceException(
                    "Application '" +
                            appName +
                            "' already exists."
            );
        }

        GooglePlayApp entity =
                mapper.toEntity(request);

        GooglePlayApp savedEntity =
                repository.save(entity);

        return mapper.toResponse(
                savedEntity
        );
    }

    // =========================================================
    // DETAILS
    // =========================================================

    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public GooglePlayAppResponse getDetails(
            Long id
    ) {

        return mapper.toResponse(
                findById(id)
        );
    }

    // =========================================================
    // PAGINATION
    // =========================================================

    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public Page<GooglePlayAppResponse> findAll(
            Pageable pageable
    ) {

        return repository
                .findAll(pageable)
                .map(mapper::toResponse);
    }

    // =========================================================
    // UPDATE
    // =========================================================

    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public GooglePlayAppResponse update(
            Long id,
            GooglePlayAppRequest request
    ) {

        GooglePlayApp entity =
                findById(id);

        String appName =
                request.app().trim();

        if (repository
                .existsByAppIgnoreCaseAndIdNot(
                        appName,
                        id
                )) {

            throw new DuplicateResourceException(
                    "Application '" +
                            appName +
                            "' already exists."
            );
        }

        mapper.updateEntity(
                entity,
                request
        );

        return mapper.toResponse(
                entity
        );
    }

    // =========================================================
    // DELETE
    // =========================================================

    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public void delete(
            Long id
    ) {

        GooglePlayApp entity =
                findById(id);

        repository.delete(entity);
    }

    // =========================================================
    // PRIVATE
    // =========================================================

    private GooglePlayApp findById(
            Long id
    ) {

        return repository
                .findById(id)
                .orElseThrow(() ->
                        new ResourceNotFoundException(
                                "Google Play application with id "
                                        + id
                                        + " was not found."
                        )
                );
    }
}
