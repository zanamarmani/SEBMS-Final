# MODULE: DISTRIBUTED SYSTEMS & CONCURRENCY

Load when: multiple instances, horizontal scaling, inter-service communication, shared state across processes, network calls, distributed coordination.

---

## Core Assumptions
When multiple instances/workers exist, always assume: concurrent requests, duplicate messages, process restarts, network failures, late/out-of-order responses, disappearing workers, clock drift, partial success.

## Process-Local Memory
Safe for: immutable config, connection pools, short-lived optimization caches, non-authoritative derived data.
Never for: shared authoritative state, rate limit counters, session tracking, distributed locks, cross-instance coordination.

## Timeouts
Every external network call needs an explicit timeout. Never one universal timeout for all operations.

Define per operation: connect timeout + read timeout + total operation timeout.
Base on: expected latency, downstream SLA, acceptable user-facing latency.
Long-running ops → move to async, not longer synchronous timeouts.

## Retry Policy (Network)
Retryable: connection timeout, network reset, 503, 429 (with Retry-After).
Non-retryable: 400, 401, 403, 404, any permanent error.
Always: bounded count + exponential backoff + jitter. Retries must not amplify outages.

## Circuit Breakers
Use for unstable external dependencies where cascading failures are a risk and fast failure is preferable to slow timeout accumulation.
States: Closed → Open → Half-Open.
Do not use where simple timeouts and bounded retries are sufficient.

## Distributed Locking
Use only when: resource shared across processes AND DB-level mechanism is insufficient AND lock duration is short and bounded.

Requirements: TTL (prevents deadlock on crash) + unique lock token + atomic acquire/release + bounded wait time.
Never hold a distributed lock for a long operation. Never use just because it exists.

## Failure Isolation
Prevent cascading failure: bulkheads (limit concurrency to a dependency), bounded queues, fallback behavior, timeouts on every external call.

## Idempotency
For retriable operations: use idempotency keys on critical writes, design operations safe to repeat, use unique constraints as last line of defense.
