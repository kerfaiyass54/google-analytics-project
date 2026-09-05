package com.googleanalytics.analyticsforgoogle.controllers;

import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppRequest;
import com.googleanalytics.analyticsforgoogle.dtos.GooglePlayAppResponse;
import com.googleanalytics.analyticsforgoogle.services.GooglePlayAppService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/google-play-apps")
@RequiredArgsConstructor
public class GooglePlayAppController {

    private final GooglePlayAppService service;

    // =========================================================
    // CREATE
    // =========================================================

    @PostMapping
    public ResponseEntity<GooglePlayAppResponse> create(
            @Valid @RequestBody GooglePlayAppRequest request
    ) {

        GooglePlayAppResponse response =
                service.create(request);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(response);
    }

    // =========================================================
    // GET DETAILS
    // =========================================================

    @GetMapping("/{id}")
    public ResponseEntity<GooglePlayAppResponse> getDetails(
            @PathVariable Long id
    ) {

        GooglePlayAppResponse response =
                service.getDetails(id);

        return ResponseEntity.ok(response);
    }

    // =========================================================
    // GET ALL - PAGINATED
    // =========================================================

    @GetMapping
    public ResponseEntity<Page<GooglePlayAppResponse>> findAll(
            @PageableDefault(
                    size = 20,
                    sort = "app",
                    direction = Sort.Direction.ASC
            )
            Pageable pageable
    ) {

        /*
         * Prevent clients from requesting an excessively
         * large number of records.
         */
        if (pageable.getPageSize() > 100) {

            pageable = Pageable.ofSize(100)
                    .withPage(pageable.getPageNumber());
        }

        Page<GooglePlayAppResponse> response =
                service.findAll(pageable);

        return ResponseEntity.ok(response);
    }

    // =========================================================
    // UPDATE
    // =========================================================

    @PutMapping("/{id}")
    public ResponseEntity<GooglePlayAppResponse> update(
            @PathVariable Long id,
            @Valid @RequestBody GooglePlayAppRequest request
    ) {

        GooglePlayAppResponse response =
                service.update(id, request);

        return ResponseEntity.ok(response);
    }

    // =========================================================
    // DELETE
    // =========================================================

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @PathVariable Long id
    ) {

        service.delete(id);

        return ResponseEntity.noContent().build();
    }
}