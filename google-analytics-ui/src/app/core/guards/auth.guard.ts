import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

import { keycloak } from '../auth/keycloak';

export const authGuard: CanActivateFn = () => {
  const router = inject(Router);

  if (keycloak.authenticated) {
    return true;
  }

  return router.createUrlTree(['/']);
};
