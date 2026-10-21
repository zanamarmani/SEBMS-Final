# MODE: IMPLEMENT

Default mode. Use when building features, fixing bugs, adding functionality, making any code change.

---

## Workflow

**1. Understand** — Read relevant existing code. Identify patterns, conventions, what must change vs. stay the same. Do not start coding without understanding.

**2. Plan** (non-trivial changes) — Define minimal change. Identify affected files. Identify risks (use Risk Assessment from core.md). State plan explicitly for HIGH/CRITICAL risk before proceeding.

**3. Change** — Implement minimum required change. Follow existing conventions. Apply relevant module rules. Apply all 5 Absolute Gates. No unrelated refactoring. No unrelated dependencies.

**4. Verify** — Run verification protocol:
1. Static: syntax, imports, types, linting
2. Functional: run relevant tests
3. Security: auth, tenant boundaries, secrets
4. Data: transactions, constraints, migrations
5. Operational: logs, health checks, timeouts
6. Diff: review final change for unintended edits

**5. Report** — Use Output Format from core.md. Label every claim with evidence labels.

---

## Stop When
Requested behavior implemented + relevant tests pass + diff clean + no critical issue remains.

Do NOT continue into: unrelated refactoring, speculative optimization, architecture redesign, unrequested features.
