package com.googleanalytics.identity.repository;

import com.googleanalytics.identity.entity.IdentitySession;
import java.time.Instant;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface IdentitySessionRepository extends JpaRepository<IdentitySession, String> {
    List<IdentitySession> findByUserIdOrderByStartedAtDesc(String userId);
    List<IdentitySession> findByStatus(String status);
    long countByStatus(String status);
    long countByStartedAtAfter(Instant since);
    @Query("select s from IdentitySession s where s.userId = :userId and s.status = 'ACTIVE'")
    List<IdentitySession> findActiveByUserId(String userId);
}
