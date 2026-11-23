import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { keycloak } from '../auth/keycloak';

export const userGuard: CanActivateFn = () => {
  const router = inject(Router);
  const roles: string[] = keycloak.tokenParsed?.['realm_access']?.['roles'] ?? [];
  // ADMIN is intentionally excluded, even if the account also carries USER.
  return keycloak.authenticated && roles.includes('USER') && !roles.includes('ADMIN')
    ? true
    : router.createUrlTree(['/dashboard']);
};
