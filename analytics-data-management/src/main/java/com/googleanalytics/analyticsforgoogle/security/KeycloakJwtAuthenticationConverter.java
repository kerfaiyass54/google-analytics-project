package com.googleanalytics.analyticsforgoogle.security;

import org.springframework.core.convert.converter.Converter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import static java.util.stream.Collectors.toList;

public class KeycloakJwtAuthenticationConverter
        implements Converter<Jwt, AbstractAuthenticationToken> {

    private static final String REALM_ACCESS = "realm_access";

    private static final String ROLES = "roles";

    private static final String ROLE_PREFIX = "ROLE_";

    @Override
    public AbstractAuthenticationToken convert(
            Jwt jwt
    ) {

        Collection<SimpleGrantedAuthority> authorities =
                extractAuthorities(jwt);

        return new JwtAuthenticationToken(
                jwt,
                authorities,
                extractPrincipal(jwt)
        );
    }

    private Collection<SimpleGrantedAuthority> extractAuthorities(
            Jwt jwt
    ) {

        Map<String, Object> realmAccess =
                jwt.getClaimAsMap(REALM_ACCESS);

        if (realmAccess == null) {
            return Collections.emptyList();
        }

        Object rolesObject =
                realmAccess.get(ROLES);

        if (!(rolesObject instanceof Collection<?> roles)) {
            return Collections.emptyList();
        }

        return roles.stream()
                .filter(String.class::isInstance)
                .map(String.class::cast)
                .map(String::toUpperCase)
                .map(role ->
                        new SimpleGrantedAuthority(
                                ROLE_PREFIX + role
                        )
                )
                .collect(toList());
    }

    private String extractPrincipal(
            Jwt jwt
    ) {

        String preferredUsername =
                jwt.getClaimAsString(
                        "preferred_username"
                );

        if (preferredUsername != null
                && !preferredUsername.isBlank()) {

            return preferredUsername;
        }

        return jwt.getSubject();
    }
}