# MODULE: DEPLOYMENT & INFRASTRUCTURE

Load when: Docker, containers, environment config, CI/CD, deployment strategy, zero-downtime, infrastructure changes, production operations.

---

## Core Rule
Local development behavior ≠ production behavior. Production has multiple instances, load balancers, rolling restarts, and real traffic.

## Container Requirements
- Resource limits (CPU + memory) defined — not just requests.
- Non-root user. Health checks configured. Graceful shutdown handled.
- All config from environment variables — no hardcoded env-specific values.

## Graceful Shutdown
On SIGTERM: stop accepting new work → complete/checkpoint in-flight work → close DB/Redis connections → release locks → exit cleanly.
Celery: `CELERY_TASK_ACKS_LATE=True` + `CELERY_WORKER_PREFETCH_MULTIPLIER=1` for safe shutdown.

## Environment Configuration
All env-specific values from env vars or secrets manager. Validate at startup. Fail fast with clear error if required config missing. Log config state at startup (sanitized).

## Migration Deployment Order

| Scenario | Order |
|---|---|
| Backward-compatible (add column/table) | Migration → code deploy |
| Removing old structure | Verify no live references → migration |
| Breaking change | Maintenance window or coordinated cutover |

Never deploy code requiring a migration before that migration runs on production.
Test: "Can old code and new code run against the same DB simultaneously?"

## Zero-Downtime Requirements
- All migrations backward-compatible during rollout.
- Old and new code must run simultaneously during rolling deployment.
- New code must not assume a column exists that old migration didn't create.

## Rollback Strategy
Define before every deployment: can code be rolled back? Can migration be rolled back? If no to migration: document recovery procedure. Never deploy non-reversible migration without approval and recovery plan.

## Resource Sizing
```
Total DB connections = instances × workers × pool_size  (must not exceed max_connections)
```
Set memory/CPU limits based on profiling, not guessing. Verify disk rotation for logs and temp files.
