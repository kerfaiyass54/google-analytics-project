package com.googleanalytics.identity.service;

import com.googleanalytics.identity.dto.SessionResponse;
import com.googleanalytics.identity.dto.SessionSummaryResponse;
import com.googleanalytics.identity.entity.IdentitySession;
import com.googleanalytics.identity.repository.IdentitySessionRepository;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.List;
import java.util.stream.IntStream;
import org.springframework.stereotype.Service;

@Service
public class SessionService {
    private final IdentitySessionRepository sessions;
    public SessionService(IdentitySessionRepository sessions) { this.sessions = sessions; }

    public List<SessionResponse> findUserSessions(String userId) {
        return sessions.findByUserIdOrderByStartedAtDesc(userId).stream().map(this::toResponse).toList();
    }

    public SessionSummaryResponse summary() {
        LocalDate today = LocalDate.now(ZoneOffset.UTC);
        List<SessionSummaryResponse.DailySessionCount> daily = IntStream.rangeClosed(6, 0).mapToObj(offset -> {
            LocalDate day = today.minusDays(offset);
            var start = day.atStartOfDay(ZoneOffset.UTC).toInstant();
            var end = day.plusDays(1).atStartOfDay(ZoneOffset.UTC).toInstant();
            long active = sessions.countByStartedAtAfter(start) - sessions.countByStartedAtAfter(end);
            long closed = sessions.findByStatus("CLOSED").stream()
                .filter(s -> s.getClosedAt() != null && !s.getClosedAt().isBefore(start) && s.getClosedAt().isBefore(end)).count();
            return new SessionSummaryResponse.DailySessionCount(day.toString(), Math.max(active, 0), closed);
        }).toList();
        return new SessionSummaryResponse(sessions.countByStatus("ACTIVE"), sessions.countByStatus("CLOSED"), daily);
    }

    private SessionResponse toResponse(IdentitySession s) {
        return new SessionResponse(s.getId(), s.getIpAddress(), s.getStartedAt(), s.getLastAccessAt(),
            s.getClosedAt(), s.getStatus(), s.getClients());
    }
}
