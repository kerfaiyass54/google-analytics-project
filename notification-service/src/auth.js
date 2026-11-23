import { createRemoteJWKSet, jwtVerify } from 'jose';

const issuer = process.env.KEYCLOAK_ISSUER || 'http://localhost:8280/realms/google-analytics';
const jwksUrl = process.env.KEYCLOAK_JWKS_URL || 'http://localhost:8280/realms/google-analytics/protocol/openid-connect/certs';
const jwks = createRemoteJWKSet(new URL(jwksUrl));

export async function authenticate(req, res, next) {
  try {
    const token = req.headers.authorization?.replace(/^Bearer\s+/i, '');
    if (!token) return res.status(401).json({ message: 'Bearer token required.' });
    const { payload } = await jwtVerify(token, jwks, { issuer });
    const realm = payload.realm_access?.roles || [];
    const client = payload.resource_access?.['google-analytics-api']?.roles || [];
    const roles = [...new Set([...realm, ...client].map(role => String(role).toUpperCase()))];
    const role = roles.includes('ADMIN') ? 'ADMIN' : roles.includes('USER') ? 'USER' : null;
    if (!role) return res.status(403).json({ message: 'A supported application role is required.' });
    req.identity = { userId: String(payload.sub), role };
    next();
  } catch {
    return res.status(401).json({ message: 'Invalid or expired access token.' });
  }
}
