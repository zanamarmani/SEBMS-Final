# MODE: DEBUG

Use when investigating a bug, error, unexpected behavior, or system failure.

---

## Workflow

**1. Reproduce** — Exact failure: what happened vs. expected? Always or intermittent? Smallest reproducing case? Do NOT assume cause — find evidence first.

**2. Trace** — Follow the actual code path. Read code, do not rely on memory. Identify where behavior diverges. Use logs, stack traces, test output as evidence.

**3. Root Cause** — Find actual root cause, not symptom. Ask "why" until true cause is found. State root cause explicitly before proposing fix. Uncertain → label [INFERRED] or [ASSUMED].

**4. Fix** — Fix root cause, not symptom. Minimum change required. Follow IMPLEMENT mode for code change. No unrelated changes.

**5. Regression Test** — Write test that fails before fix and passes after. Not optional for non-trivial bugs. Documents what was broken and proves it is fixed.

**6. Verify** — Confirm original failure no longer reproduces. Run full relevant test suite. Inspect diff for unintended changes.

---

## Discipline
Never apply a fix without understanding the cause. Never claim fixed without evidence. If root cause cannot be determined: say so, describe what was found, state what is needed to continue.

## Common Bug Patterns
Race condition · N+1 query · Missing auth check · Missing transaction · Retry without idempotency · Wrong isolation level · Incorrect 4xx treated as retryable · Timezone mismatch · Silent exception swallowing

---

## Report Format
```
## Bug
[description of failure]

## Root Cause
[OBSERVED/INFERRED] [exact cause]

## Fix
[what changed and why]

## Regression Test
[OBSERVED] Test written: [name] — confirms fix

## Verification
[OBSERVED] Test suite: X passed, 0 failed
[UNVERIFIED] Production behavior: not tested
```
