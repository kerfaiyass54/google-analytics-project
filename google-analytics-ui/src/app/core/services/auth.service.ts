import { Injectable, computed, inject } from '@angular/core';

import { keycloak } from '../auth/keycloak';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  readonly authenticated = computed(() => keycloak.authenticated ?? false);

  readonly username = computed(() => keycloak.tokenParsed?.['preferred_username'] ?? null);

  readonly roles = computed<string[]>(
    () => keycloak.tokenParsed?.['realm_access']?.['roles'] ?? [],
  );

  readonly isAdmin = computed(() => this.roles().includes('ADMIN'));

  readonly isUser = computed(() => this.roles().includes('USER'));

  async login(): Promise<void> {
    await keycloak.login({
      redirectUri: window.location.origin,
    });
  }

  async logout(): Promise<void> {
    await keycloak.logout({
      redirectUri: window.location.origin,
    });
  }

  async refreshToken(): Promise<boolean> {
    try {
      await keycloak.updateToken(30);
      return true;
    } catch (error) {
      console.error('Failed to refresh Keycloak token:', error);
      return false;
    }
  }

  getToken(): string | undefined {
    return keycloak.token;
  }
}
