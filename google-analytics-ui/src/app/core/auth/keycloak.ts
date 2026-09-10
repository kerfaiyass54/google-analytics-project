import Keycloak from 'keycloak-js';

export const keycloak = new Keycloak({
  url: 'http://localhost:8280',
  realm: 'google-analytics',
  clientId: 'google-analytics-frontend',
});
