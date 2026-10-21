# MODULE: SECURITY

Load when: authentication, authorization, multi-tenancy, permissions, secrets, file uploads, security-sensitive behavior.

Note: 5 Absolute Gates in core.md are always active. This module adds depth for security tasks.

---

## Authentication
- Hash passwords with bcrypt/argon2. Never MD5/SHA1. Never plaintext.
- Apply token/session expiration. Rate-limit auth endpoints.
- Never expose credentials in responses, logs, or URLs.
- Never implement custom cryptography without expert review.

## Authorization
Never trust client-provided: role, permission, user ID, tenant ID, workspace ID, or any identity claim.
Enforce server-side — at service layer AND DB query layer AND background jobs.
Check before: reading sensitive data, modifying any resource, performing privileged actions.

## Multi-Tenancy
- Resolve tenant from **authenticated context only** — never from client-supplied header/param.
- Scope ALL queries by tenant. Protect: cache keys, file paths, background jobs, logs.
- Defense in depth: enforce at auth → service → DB → jobs → cache → storage layers.
- Tenancy UNKNOWN → assume multi-tenant and apply isolation.
- Confirmed single-tenant → do not introduce unnecessary tenant architecture.

## Data Protection
Protect: passwords, tokens, API keys, secrets, PII, financial data.
Never expose in: logs, error messages, API responses, URLs, exception traces, monitoring.
Mask sensitive values where logging is necessary.

## Web Security
Apply only what's relevant:

| Mechanism | When |
|---|---|
| CSRF | Session-based auth + state-changing endpoints |
| Secure cookies + SameSite | All cookie sessions |
| CORS | Cross-origin API access |
| Security headers / HSTS | All web-facing services (HSTS: production only) |
| Rate limiting | Auth endpoints, public endpoints, expensive ops |
| Request size limits | All endpoints accepting input |
| SQL injection protection | All DB queries — use ORM/parameterized queries |

## File Upload Security
- Validate MIME type server-side (not just extension). Validate file size.
- Sanitize filenames. Prevent path traversal. Store outside executable paths.
- Restrict access by authorization. Protect tenant boundaries in paths.
- Never trust user-controlled file paths.

## Secrets
Never hardcode in source. Use env vars or secrets manager. Validate at startup — fail clearly if missing. Never commit to version control.
