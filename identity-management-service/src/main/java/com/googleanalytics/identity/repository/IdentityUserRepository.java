package com.googleanalytics.identity.repository;

import com.googleanalytics.identity.entity.IdentityUser;
import org.springframework.data.jpa.repository.JpaRepository;

public interface IdentityUserRepository extends JpaRepository<IdentityUser, String> {}
