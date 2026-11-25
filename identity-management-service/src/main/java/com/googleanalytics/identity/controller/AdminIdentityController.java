package com.googleanalytics.identity.controller;

import com.googleanalytics.identity.dto.ProfileResponse;
import com.googleanalytics.identity.dto.SessionSummaryResponse;
import com.googleanalytics.identity.entity.IdentityUser;
import com.googleanalytics.identity.repository.IdentityUserRepository;
import com.googleanalytics.identity.service.SessionService;
import java.util.List;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin")
@PreAuthorize("hasRole('ADMIN')")
public class AdminIdentityController {
    private final IdentityUserRepository users;
    private final SessionService sessions;
    public AdminIdentityController(IdentityUserRepository users, SessionService sessions) { this.users = users; this.sessions = sessions; }

    @GetMapping("/users")
    public List<ProfileResponse> users() {
        return users.findAll().stream().map(this::toResponse).toList();
    }

    @GetMapping("/sessions/summary")
    public SessionSummaryResponse sessionSummary() {
        return sessions.summary();
    }

    private ProfileResponse toResponse(IdentityUser user) {
        return new ProfileResponse(user.getId(), user.getUsername(), user.getEmail(), user.getFirstName(),
            user.getLastName(), user.isEnabled(), user.isEmailVerified(), user.getCreatedAt());
    }
}
