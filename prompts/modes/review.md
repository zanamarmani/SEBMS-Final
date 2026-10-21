# MODE: REVIEW

Use when reviewing existing code, a PR, or a proposed change — without implementing anything.

---

## Workflow

**1. Understand Scope** — What is being reviewed? What context (existing system, critical path)? What level of review needed?

**2. Inspect** — Read actual implementation, not just the summary. Understand what it does, not just what it should do. Trace: happy path, error path, edge cases.

**3. Classify Issues**

| Severity | Meaning |
|---|---|
| CRITICAL | Must fix before merge — security, data loss, correctness |
| HIGH | Should fix before merge — reliability, wrong behavior |
| MEDIUM | Should address — maintainability, missing coverage |
| LOW | Suggestion — minor improvement |
| NITPICK | Optional — cosmetic, preference |

**4. Risk Rate** — Apply Risk Assessment (Impact × Reversibility × Exposure) to each issue. Identify what blocks merge vs. improvement suggestions.

**5. Report** — Structured findings below.

---

## Review Areas
Correctness: edge cases handled? error cases handled? state transitions valid?
Security: auth enforced? tenant isolation maintained? secrets protected? input validated?
Data: transactions correct? constraints in place? concurrent writes protected? migration safe?
Reliability: failures handled? retries bounded? timeouts defined? async idempotency correct?
Maintainability: readable? complexity justified? existing architecture respected?
Testing: authorization paths tested (including unauthorized)? failure scenarios tested?
Scope: unrelated changes present? diff size appropriate?

---

## Report Format
```
## Review Summary
[1–3 sentences: overall assessment]

## Critical (must fix)
1. [File:line] Description | Risk: [I×R×E] | Fix: [how]

## High (should fix)
1. [File:line] Description | Fix: [how]

## Medium (consider)
1. [File:line] Description

## Suggestions
1. [LOW/NITPICK] Description

## Verdict
[ ] Approve
[ ] Approve with minor fixes
[ ] Request changes — address Critical/High before merge
[ ] Block — fundamental design issue requires rework
```
