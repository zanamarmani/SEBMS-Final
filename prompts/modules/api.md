# MODULE: API ENGINEERING

Load when: REST APIs, HTTP endpoints, request/response contracts, versioning, rate limiting.

---

## Contracts & Validation
- Define clear input/output contracts before implementation.
- Validate ALL external input server-side. Never trust client data.
- Validate type, format, range, presence, and body size.
- Reject oversized payloads early.

## HTTP Status Codes
- `200` OK · `201` Created · `204` No Content
- `400` Bad Request · `401` Unauthenticated · `403` Forbidden · `404` Not Found
- `409` Conflict · `422` Unprocessable · `429` Rate Limited · `500` Server Error
- Never return `200` for a failed operation.

## Response Rules
- Consistent error structure across all endpoints.
- Never leak stack traces, internal IDs, or infrastructure details.
- Preserve existing response fields — do not rename/remove without versioning.
- New optional fields may be added safely.

## Pagination
- Always paginate large collections. Never return unbounded lists.
- Cursor-based for large/frequently updated data; offset for small stable data.
- Always include pagination metadata: `total`, `next_cursor`, `has_more`.

## Rate Limiting
- Apply to: auth endpoints, resource-intensive ops, public/unauthenticated endpoints.
- Return `429` with `Retry-After` header.

## Idempotency
Use `Idempotency-Key` for: payments, orders, resource creation with side effects, retryable requests.

Requires: key scope + request fingerprinting + result persistence with TTL + concurrency protection + duplicate response behavior.

Do NOT add to every endpoint blindly.

## Versioning
Consider when breaking changes to request/response structure are required. Follow existing project convention.

## Logging
Log: request ID, user ID (if safe), tenant ID (if safe), operation, duration, status, error code.
Never log: passwords, tokens, API keys, full bodies with sensitive data, PII.
