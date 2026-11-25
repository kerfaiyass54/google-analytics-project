package com.googleanalytics.identity.controller;

import com.googleanalytics.identity.dto.PasswordChangeRequest;
import com.googleanalytics.identity.dto.ProfileResponse;
import com.googleanalytics.identity.dto.ProfileUpdateRequest;
import com.googleanalytics.identity.dto.SessionResponse;
import com.googleanalytics.identity.service.ProfileService;
import com.googleanalytics.identity.service.SessionService;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/profile")
public class ProfileController {
    private final ProfileService profiles;
    private final SessionService sessions;
    public ProfileController(ProfileService profiles, SessionService sessions) { this.profiles = profiles; this.sessions = sessions; }

    @GetMapping
    public ProfileResponse me(@AuthenticationPrincipal Jwt jwt) {
        return profiles.getProfile(jwt.getSubject());
    }

    @PutMapping
    public ProfileResponse update(@AuthenticationPrincipal Jwt jwt, @Valid @RequestBody ProfileUpdateRequest request) {
        return profiles.updateProfile(jwt.getSubject(), request);
    }

    @PutMapping("/password")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void changePassword(@AuthenticationPrincipal Jwt jwt, @Valid @RequestBody PasswordChangeRequest request) {
        profiles.changePassword(jwt.getTokenValue(), request);
    }

    @GetMapping("/sessions")
    public List<SessionResponse> mySessions(@AuthenticationPrincipal Jwt jwt) {
        return sessions.findUserSessions(jwt.getSubject());
    }
}
