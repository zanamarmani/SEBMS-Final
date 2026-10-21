# MODE: AUDIT

Use for security/reliability audits or comprehensive system assessment. More thorough than REVIEW — covers entire system area, not just a diff.

---

## Workflow

**1. Define Scope** — What is being audited? What are the objectives (security, reliability, performance)? What is in/out of scope?

**2. Systematic Inspection** — Go through each dimension for the scope. Read actual code — do not assess from summaries or assumptions.

**3. Classify Findings**

| Severity | Meaning |
|---|---|
| CRITICAL | Exploitable vulnerability or data integrity risk — fix immediately |
| HIGH | Significant risk — fix before next production change |
| MEDIUM | Moderate risk — fix in next sprint |
| LOW | Minor risk — backlog |
| INFO | Observation, not a risk |

**4. Report** — Structured findings with evidence, risk, remediation.

---

## Security Audit Dimensions

**Authentication:** Passwords hashed (bcrypt/argon2)? Tokens signed and expiring? Auth endpoints rate-limited? Account lockout implemented? Session invalidation on logout? Credential resets secure?

**Authorization:** Enforced server-side on every endpoint AND background jobs? IDOR vulnerabilities possible? Privilege escalation paths possible? Least privilege applied?

**Multi-Tenancy:** All queries scoped by tenant? Tenant resolved from auth context only? Cache keys tenant-namespaced? File paths tenant-namespaced? Background jobs tenant-context-aware?

**Data Exposure:** Secrets excluded from logs and API responses? PII minimized? Error messages safe (no stack traces, no internal details)?

**Input Handling:** All input validated server-side? SQL injection prevented? Path traversal prevented? File upload secure? Request sizes limited?

**Dependencies:** Pinned? Known vulnerabilities checked? Justified?

---

## Reliability Audit Dimensions

**Error Handling:** Unexpected exceptions caught at boundary and logged? Errors never silently swallowed? Stable error codes used?

**Resilience:** Timeouts on all external calls? Retries bounded and jittered? Circuit breakers for unstable dependencies?

**Async:** Tasks bounded (time limits)? Retries bounded? Tasks idempotent? Dead-letter queues configured?

**Data Integrity:** Critical operations in transactions? Constraints enforced at DB level? Race conditions protected? Migrations safe?

---

## Report Format
```
## Audit: [Component]
## Scope: [what was audited]

## Executive Summary
[2–3 sentences: overall risk level and key findings]

## Critical Findings
### [CRIT-001] Title
Location: [file/component]
Risk: CRITICAL
Description: [vulnerability/risk]
Evidence: [OBSERVED/INFERRED] [how identified]
Remediation: [how to fix]

## High / Medium / Low Findings
[same format, abbreviated]

## Overall Risk Rating
[ ] Critical — immediate action  [ ] High — before next deploy
[ ] Medium — this sprint         [ ] Low — acceptable, backlog
```
