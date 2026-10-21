# MODULE: DATABASE ENGINEERING

Load when: schema design, queries, ORM, transactions, indexes, constraints, connection pooling, data integrity.

---

## Core Rule
DB is authoritative source of truth. Enforce integrity at DB layer, not just application layer.

## Schema Design
Use: appropriate types, foreign keys, unique constraints, check constraints, NOT NULL where required, indexes (with reason).
Never design a schema that permits invalid business states.

## Transactions
Use when multiple operations must succeed or fail together: financial ops, inventory/state changes, related record creation, critical state transitions.
- Keep transactions short. No network calls inside transactions. No long computations inside transactions.

## Concurrency — Choose Simplest That Works
- Atomic SQL updates (`UPDATE ... WHERE status = 'pending'`)
- Unique constraints (prevent duplicate inserts)
- `SELECT FOR UPDATE` (row-level lock)
- Advisory locks (PostgreSQL)
- Atomic Redis operations
- Queue serialization

Never use distributed locking when a DB-level mechanism is sufficient.

## Query Performance
Prevent: N+1 queries, full table scans on large tables, unbounded queries (no LIMIT), repeated identical calls, loading entire datasets into memory.
Use: indexes, pagination, batching, eager loading, `EXPLAIN ANALYZE` for slow queries.

## Indexing
Index with reason: FKs, frequent WHERE/ORDER BY columns, unique business constraints.
Cost: indexes slow writes. Use partial indexes for selective conditions. Composite index order matters (leftmost prefix).
Never add indexes blindly.

## Connection Pooling
```
Total connections = instances × workers_per_instance × pool_size
```
Must not exceed DB `max_connections`. Never set arbitrary pool size without this analysis.

## N+1 Prevention
Django: `select_related()` for FK, `prefetch_related()` for M2M.
SQLAlchemy: `joinedload()` or `selectinload()`.
One query per loop iteration = almost always N+1.
