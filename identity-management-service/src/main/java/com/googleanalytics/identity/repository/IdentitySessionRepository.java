package com.googleanalytics.identity.repository;

import com.googleanalytics.identity.entity.IdentitySession;
import java.time.Instant;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface IdentitySessionRepository extends JpaRepository<IdentitySession, String> {
    List<IdentitySession> findByUserIdOrderByStartedAtDesc(String userId);
    List<IdentitySession> findByStatus(String status);
    long countByStatus(String status);
    long countByStatusAndStartedAtGreaterThanEqualAndStartedAtLessThan(String status, Instant from, Instant to);
}
