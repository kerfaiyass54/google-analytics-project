package com.googleanalytics.identity;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class IdentityManagementApplication {
    public static void main(String[] args) {
        SpringApplication.run(IdentityManagementApplication.class, args);
    }
}
