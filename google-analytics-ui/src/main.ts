import { bootstrapApplication } from '@angular/platform-browser';

import { App } from './app/app';
import { appConfig } from './app/app.config';
import { keycloak } from './app/core/auth/keycloak';

async function bootstrap(): Promise<void> {
  try {
    await keycloak.init({
      onLoad: 'login-required',
      checkLoginIframe: false,
    });

    console.log('Keycloak initialized:', keycloak.authenticated);
  } catch (error) {
    console.error('Keycloak initialization failed:', error);
  }

  await bootstrapApplication(App, appConfig);
}

bootstrap().catch((error) => {
  console.error('Angular bootstrap failed:', error);
});
