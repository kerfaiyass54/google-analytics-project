package com.googleanalytics.analyticsforgoogle.security;

import lombok.RequiredArgsConstructor;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;

import org.springframework.security.config.annotation.web.builders.HttpSecurity;

import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;

import org.springframework.security.config.http.SessionCreationPolicy;

import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final KeycloakJwtAuthenticationConverter
            keycloakJwtAuthenticationConverter =
            new KeycloakJwtAuthenticationConverter();

    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http
    ) throws Exception {

        http
                // -------------------------------------------------
                // REST API
                // -------------------------------------------------

                .csrf(csrf ->
                        csrf.disable()
                )

                // -------------------------------------------------
                // Stateless JWT authentication
                // -------------------------------------------------

                .sessionManagement(session ->
                        session.sessionCreationPolicy(
                                SessionCreationPolicy.STATELESS
                        )
                )

                // -------------------------------------------------
                // Authorization
                // -------------------------------------------------

                .authorizeHttpRequests(authorize -> authorize

                        // Public endpoints
                        .requestMatchers(
                                "/",
                                "/error",
                                "/actuator/health"
                        ).permitAll()

                        // Swagger
                        .requestMatchers(
                                "/swagger-ui/**",
                                "/swagger-ui.html",
                                "/v3/api-docs/**"
                        ).permitAll()

                        // -------------------------------------------------
                        // ADMIN ONLY
                        // -------------------------------------------------

                        .requestMatchers(
                                org.springframework.http.HttpMethod.PUT,
                                "/api/google-play-apps/**"
                        ).hasRole("ADMIN")

                        .requestMatchers(
                                org.springframework.http.HttpMethod.DELETE,
                                "/api/google-play-apps/**"
                        ).hasRole("ADMIN")

                        // -------------------------------------------------
                        // AUTHENTICATED USERS
                        // -------------------------------------------------

                        .requestMatchers(
                                "/api/google-play-apps/**"
                        ).authenticated()

                        // -------------------------------------------------
                        // EVERYTHING ELSE
                        // -------------------------------------------------

                        .anyRequest()
                        .authenticated()
                )

                // -------------------------------------------------
                // JWT
                // -------------------------------------------------

                .oauth2ResourceServer(
                        oauth2 ->
                                oauth2.jwt(
                                        jwt ->
                                                jwt.jwtAuthenticationConverter(
                                                        keycloakJwtAuthenticationConverter
                                                )
                                )
                );

        return http.build();
    }
}