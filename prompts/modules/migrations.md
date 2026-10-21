# MODULE: DATABASE MIGRATIONS

Load when: schema changes, data migrations, adding/removing columns or tables, index changes, any DB evolution in a live system.

---

## Core Rule
A bad migration on production can cause downtime, data loss, or irreversible corruption. Every migration is HIGH-RISK by default.

## Requirements
Every migration must be: version-controlled, deterministic, reviewable, safe, tested in staging.

## Production Safety — Check Before Every Migration

**Lock analysis:**
- Will this lock the table? How large is the table?
- PostgreSQL: `ADD COLUMN ... DEFAULT NULL` = instant. `ADD COLUMN ... DEFAULT <non-null>` = locks table (old PG versions).
- Adding NOT NULL without default = table lock.
- Creating index → use `CREATE INDEX CONCURRENTLY`.

**Rollback strategy:**
- Can this be reversed? If yes: write the rollback migration.
- If no: document recovery procedure + verify backup exists.

**Timing:**
- How long on production data volume? Off-peak hours needed? Batching required?

## Dangerous Operations

| Operation | Risk | Mitigation |
|---|---|---|
| DROP TABLE | Critical / Irreversible | Backup + verify no refs + soft-delete first |
| DROP COLUMN | Critical / Irreversible | Expand-contract pattern |
| RENAME COLUMN | Breaking | Expand-contract pattern |
| ADD NOT NULL (no default) | Table lock | Add nullable → backfill → add constraint |
| CREATE INDEX | Lock | Use CONCURRENT |
| Large table backfill | Long lock | Batch in chunks |

## Zero-Downtime Pattern (Expand-Contract)
1. **Expand** — add new structure (nullable column, new table, new index). Deploy code writing to both old and new.
2. **Migrate** — backfill data in batches.
3. **Contract** — remove old structure after all code migrated. Separate deployment.

Never drop a column/table that live code still references.

## Deployment Order
- Backward-compatible migration (add): deploy migration → deploy code.
- Removing old structure: verify no live references → deploy migration.
- Breaking change: maintenance window or coordinated cutover.

Never deploy code requiring a migration before that migration runs on production.

## Pre-Migration Checklist
- [ ] Reversible? Rollback migration written?
- [ ] Will it lock a large table? Safer approach possible?
- [ ] All referenced objects still used by live code?
- [ ] Backup available before destructive changes?
- [ ] Tested in staging with production-scale data?
- [ ] Deployment order correct?
- [ ] Large tables: batching required?
- [ ] Migration deterministic (safe to re-run)?
