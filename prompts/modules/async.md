# MODULE: ASYNC / QUEUES

Load when: Celery, background workers, task queues, job scheduling, message brokers (Redis, RabbitMQ, SQS).

---

## Core Rule
Never assume a background task executes exactly once. Design for at-least-once delivery.

## Every Task Must Be
- **Observable** — failures and completions logged and trackable
- **Bounded** — explicit `soft_time_limit` and `time_limit`
- **Intentional retries** — retry policy explicit, not default
- **Failure-recorded** — failures captured, not silently lost
- **Graceful shutdown** — handles SIGTERM cleanly

## Idempotency
Use when duplicate execution is possible: unique job IDs checked before execution, DB unique constraints, atomic state transitions (`UPDATE ... WHERE status = 'pending'`), idempotency records with TTL, task-level locks (only if DB mechanisms insufficient).
Do not depend on in-memory state for idempotency.

## Retry Policy
Retryable: network timeouts, temporary service unavailability, temp DB connection failures, rate limits (with Retry-After).
Non-retryable: validation failures, auth failures, permanent errors, non-idempotent ops without protection.

Always: bounded count (max 3–5) + exponential backoff + jitter. Never unbounded retries.

## Dead Letter Handling
Define: max retry count → dead-letter queue → alert on accumulation → manual inspection → replay capability.
Never allow jobs to retry forever.

## Worker Concurrency
```
Total DB connections = workers × concurrency × pool_size
```
Must not exceed DB limits. Understand before configuring.

## Bounded Execution
```python
@app.task(soft_time_limit=300, time_limit=360, max_retries=3, default_retry_delay=60)
```

## Transactional Outbox
Use when: DB state change must reliably trigger an async event AND lost events cause business problems.
Pattern: write outbox record in same transaction as state change → separate poller publishes → mark as published after delivery.
Do not use for trivial internal operations.

## Observability
Every task should log: task name/ID, sanitized inputs, start time, duration, retry count, final status, error detail on failure.
Monitor: queue depth, failed job rate, execution time (p50/p95/p99), dead-letter size.
