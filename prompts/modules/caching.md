# MODULE: REDIS & CACHING

Load when: Redis, Memcached, in-memory caching, cache invalidation, stampede protection.

---

## Core Rule
Use caching only when it provides a real, measurable benefit. Caching introduces complexity — do not add speculatively.

## Cache Design — Every Entry Defines
- **Key structure**: namespaced, collision-free — `service:entity:id`
- **TTL**: explicit expiration, never infinite unless intentional
- **Invalidation strategy**: who invalidates it and when?
- **Stale-data behavior**: acceptable staleness or must be exact?
- **Failure behavior**: what if Redis is unavailable?

## Multi-Tenancy Isolation
Always namespace by tenant: `tenant:{id}:user:{id}:permissions`
A cache entry from tenant A must NEVER be served to tenant B — even generic-looking keys.

## Invalidation Strategies
- **TTL expiry** — simplest, acceptable staleness
- **Write-through** — update cache on every write (consistency, write cost)
- **Cache-aside** — invalidate on write, repopulate on next read
- **Event-driven** — invalidate via event on data change

Never introduce caching without defining invalidation.

## Stampede Protection — Choose Simplest That Works
- Jittered TTLs — randomize expiration to spread load (often sufficient)
- Stale-while-revalidate — serve stale while refreshing in background
- Request coalescing / locking — only one request repopulates
- Background refresh — proactively refresh before expiry

Do not automatically introduce distributed locks for stampede protection.

## Redis Failure Handling
- Caching: fall through to DB on Redis unavailability (acceptable perf degradation)
- Rate limiting: define fail-open or fail-closed explicitly (security vs availability)
- Distributed locks: do not proceed if lock required for correctness

## Redis as Queue / Pub-Sub
Understand delivery guarantees. Design consumers for idempotency. Monitor queue depth. Set `maxmemory-policy` appropriate for use case.

## Source of Truth
Only use cache as authoritative source when: intentional architectural decision + persistence configured (AOF/RDB) + recovery behavior defined. Never as a replacement for a real database.
