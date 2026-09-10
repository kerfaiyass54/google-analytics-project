import { bootstrapApplication } from '@angular/platform-browser';

import { App } from './app/app';
import { appConfig } from './app/app.config';
import { keycloak } from './app/core/auth/keycloak';

keycloak
  .init({
    onLoad: 'check-sso',
    checkLoginIframe: false,
  })
  .then(() => {
    bootstrapApplication(App, appConfig).catch((error) => {
      console.error('Angular bootstrap failed:', error);
    });
  })
  .catch((error) => {
    console.error('Keycloak initialization failed:', error);
  });
