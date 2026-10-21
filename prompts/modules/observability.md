# MODULE: OBSERVABILITY & LOGGING

Load when: logging, metrics, tracing, health checks, monitoring, making system behavior visible in production.

---

## Core Rule
Observability must answer: What happened? Where? For which request/user/tenant? How long? Which dependency failed? Was it retried? What was the outcome?

## Structured Logging
Prefer JSON in production.

Standard fields: `timestamp`, `level`, `service`, `environment`, `request_id`, `correlation_id`, `user_id` (if safe), `tenant_id` (if safe), `operation`, `duration_ms`, `status`, `error_code`.

Include only fields relevant to the event.

**Always log:** request start/end with duration, auth events (login/logout/failure), authz failures, background task start/completion/failure, external service calls (outcome + duration), critical business events.

**Never log:** passwords, tokens, API keys, secrets, full request bodies with sensitive data, unnecessary PII.

## Log Levels
- `ERROR` — unexpected failures needing human attention
- `WARNING` — expected failures, retries, degraded behavior
- `INFO` — normal significant events (startup, auth, key business events)
- `DEBUG` — detailed internal state (not in production hot paths by default)

Do not use ERROR for expected conditions.

## Request & Correlation IDs
Every request needs a unique `request_id`. Propagate `correlation_id` across service boundaries.
Propagate through: HTTP headers (`X-Request-ID`, `X-Correlation-ID`), background task parameters, log fields.

## Key Metrics

| Metric | Type | Purpose |
|---|---|---|
| Request rate | Counter | Traffic volume |
| Error rate | Counter | Health indicator |
| Request latency | Histogram | Performance, SLA |
| DB query duration | Histogram | DB performance |
| Cache hit/miss | Counter | Cache effectiveness |
| Queue depth | Gauge | Worker capacity |
| Task execution time | Histogram | Worker performance |

## Health Checks

**Liveness** — Is the process alive? Returns 200 if running. Must NOT check external dependencies. Used by orchestrators to decide on restart.

**Readiness** — Can this instance receive traffic? Returns 200 when all required deps available (DB, Redis, required config). Used by load balancer to route traffic.

Do not conflate. Do not make liveness fail on transient external issues.

## Distributed Tracing
For microservices/complex async: instrument with OpenTelemetry. Trace spans across HTTP, DB queries, queue messages. Use trace IDs to correlate logs across services.
