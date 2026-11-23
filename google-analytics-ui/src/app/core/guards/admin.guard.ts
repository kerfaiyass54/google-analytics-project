import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

import { keycloak } from '../auth/keycloak';

export const adminGuard: CanActivateFn = () => {
  const router = inject(Router);
  const roles = keycloak.tokenParsed?.['realm_access']?.['roles'] ?? [];

  if (keycloak.authenticated && roles.includes('ADMIN')) {
    return true;
  }

  return router.createUrlTree(['/']);
};
