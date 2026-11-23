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
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.Collection;
import java.util.Map;

@RestController
@RequestMapping("/api/google-play-apps")
@RequiredArgsConstructor
public class GooglePlayAppController {

    private final GooglePlayAppService service;

    @PostMapping
    public ResponseEntity<GooglePlayAppResponse> create(
            @Valid @RequestBody GooglePlayAppRequest request,
            @AuthenticationPrincipal Jwt jwt
    ) {
        GooglePlayAppResponse response =
                service.create(request, jwt.getClaimAsString("email"));

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<GooglePlayAppResponse> getDetails(
            @PathVariable Long id,
            @AuthenticationPrincipal Jwt jwt
    ) {
        GooglePlayAppResponse response = service.getDetails(
                id,
                jwt.getClaimAsString("email"),
                isAdmin(jwt)
        );

        return ResponseEntity.ok(response);
    }

    @GetMapping
    public ResponseEntity<Page<GooglePlayAppResponse>> findAll(
            @PageableDefault(
                    size = 20,
                    sort = "app",
                    direction = Sort.Direction.ASC
            ) Pageable pageable,
            @AuthenticationPrincipal Jwt jwt
    ) {
        if (pageable.getPageSize() > 100) {
            pageable = Pageable.ofSize(100).withPage(pageable.getPageNumber());
        }

        Page<GooglePlayAppResponse> response = service.findAll(
                pageable,
                jwt.getClaimAsString("email"),
                isAdmin(jwt)
        );

        return ResponseEntity.ok(response);
    }

    @PutMapping("/{id}")
    public ResponseEntity<GooglePlayAppResponse> update(
            @PathVariable Long id,
            @Valid @RequestBody GooglePlayAppRequest request
    ) {
        return ResponseEntity.ok(service.update(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

    private boolean isAdmin(Jwt jwt) {
        Map<String, Object> realmAccess = jwt.getClaim("realm_access");
        if (realmAccess == null) {
            return false;
        }

        Object rolesClaim = realmAccess.get("roles");
        if (!(rolesClaim instanceof Collection<?> roles)) {
            return false;
        }

        return roles.stream().anyMatch(role -> "ADMIN".equals(role));
    }
}