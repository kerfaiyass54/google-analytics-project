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
import com.googleanalytics.analyticsforgoogle.services.NotificationEventPublisher;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class GooglePlayAppService {

    private final GooglePlayAppRepository repository;

    private final GooglePlayAppMapper mapper;

    private final NotificationEventPublisher notificationEventPublisher;

    // =========================================================
    // CREATE
    // =========================================================

    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    @Transactional
    public GooglePlayAppResponse create(
            GooglePlayAppRequest request,
            String ownerEmail
    ) {

        if (ownerEmail == null || ownerEmail.isBlank()) {
            throw new IllegalArgumentException("Authenticated user email is required.");
        }

        String appName = request.app().trim();

        if (repository.existsByAppIgnoreCase(appName)) {
            throw new DuplicateResourceException(
                    "Application '" + appName + "' already exists."
            );
        }

        GooglePlayApp entity = mapper.toEntity(request);
        entity.setEmail(ownerEmail.trim());
        GooglePlayApp saved = repository.save(entity);
        notificationEventPublisher.publishAfterCommit("APP_CREATED", saved.getId(), saved.getApp());
        return mapper.toResponse(saved);
    }

    // =========================================================
    // DETAILS (OWNERS OR ADMIN)
    // =========================================================

    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public GooglePlayAppResponse getDetails(
            Long id,
            String userEmail,
            boolean admin
    ) {
        return mapper.toResponse(findByIdForViewer(id, userEmail, admin));
    }

    // =========================================================
    // PAGINATION (OWNERS OR ADMIN)
    // =========================================================

    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    public Page<GooglePlayAppResponse> findAll(
            Pageable pageable,
            String userEmail,
            boolean admin
    ) {
        Page<GooglePlayApp> apps = admin
                ? repository.findAll(pageable)
                : repository.findGlobalAndOwnedApps(requireEmail(userEmail), pageable);

        return apps.map(mapper::toResponse);
    }

    // =========================================================
    // UPDATE (ADMIN ONLY)
    // =========================================================

    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public GooglePlayAppResponse update(
            Long id,
            GooglePlayAppRequest request
    ) {
        GooglePlayApp entity = findById(id);
        String appName = request.app().trim();

        if (repository.existsByAppIgnoreCaseAndIdNot(appName, id)) {
            throw new DuplicateResourceException(
                    "Application '" + appName + "' already exists."
            );
        }

        mapper.updateEntity(entity, request);
        notificationEventPublisher.publishAfterCommit("APP_UPDATED", entity.getId(), entity.getApp());
        return mapper.toResponse(entity);
    }

    // =========================================================
    // DELETE (ADMIN ONLY)
    // =========================================================

    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public void delete(Long id) {
        GooglePlayApp entity = findById(id);
        notificationEventPublisher.publishAfterCommit("APP_DELETED", entity.getId(), entity.getApp());
        repository.delete(entity);
    }

    // =========================================================
    // PRIVATE HELPERS
    // =========================================================

    private GooglePlayApp findByIdForViewer(
            Long id,
            String userEmail,
            boolean admin
    ) {
        GooglePlayApp app = findById(id);

        if (admin) {
            return app;
        }

        String email = requireEmail(userEmail);
        if (app.getEmail() != null && !app.getEmail().equalsIgnoreCase(email)) {
            // Return 404 rather than disclose that another user's record exists.
            throw new ResourceNotFoundException(
                    "Google Play application with id " + id + " was not found."
            );
        }

        return app;
    }

    private String requireEmail(String email) {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("Authenticated user email is required.");
        }
        return email.trim();
    }

    private GooglePlayApp findById(Long id) {
        return repository.findById(id)
                .orElseThrow(() ->
                        new ResourceNotFoundException(
                                "Google Play application with id " + id + " was not found."
                        )
                );
    }
}