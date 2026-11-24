import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { keycloak } from '../auth/keycloak';

export const adminGuard: CanActivateFn = () => {
  const router = inject(Router);
  const realmRoles: string[] = keycloak.tokenParsed?.['realm_access']?.['roles'] ?? [];
  const apiRoles: string[] =
    keycloak.tokenParsed?.['resource_access']?.['google-analytics-api']?.['roles'] ?? [];
  const roles = new Set([...realmRoles, ...apiRoles]);
  return keycloak.authenticated && roles.has('ADMIN') ? true : router.createUrlTree(['/dashboard']);
};
