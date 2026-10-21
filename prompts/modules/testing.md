# MODULE: TESTING

Load when: writing tests, verifying behavior, regression coverage, test strategy.

---

## Core Rules
Tests must validate real behavior. Do not create tests to increase count. Do not fabricate results. Do not claim tests pass without running them.

## Testing Levels

**Unit** — business logic, utilities, validation, deterministic behavior. Mock externals. Fast (milliseconds). Cover: happy path, edge cases, error cases, boundaries.

**Integration** — DB behavior, Redis, queues, ORM queries. Use real test DB/Redis. Verify constraints enforced, transactions correct.

**API** — full HTTP request/response cycle. Include: authenticated, unauthenticated, forbidden requests. Include: valid input, invalid input, edge cases. Verify: status codes, response structure, error messages.

**Regression** — write for every non-trivial bug fix. Test the exact broken scenario. Proves the fix.

**Concurrency** — for race conditions, locking, idempotency, concurrent writes. Simulate concurrent requests. Verify constraints prevent invalid states.

## Authorization Test Pattern
Every endpoint with authorization must have:
```
1. Authenticated + authorized → 200 OK
2. Unauthenticated → 401
3. Authenticated + wrong tenant/user → 403 or 404
4. Authenticated + correct tenant + insufficient role → 403
```
Never assume authorization is tested if only the happy path exists.

## Test Quality
- Independent (order doesn't matter). Deterministic (same result every run).
- Test behavior, not implementation details.
- Use factories/fixtures, not hardcoded data.

## Failure & Recovery Testing
For failure-sensitive systems test: timeouts (mock slow dep), retries (mock transient failure), idempotency (call twice, verify identical result), partial failure (first op succeeds, second fails — check state).
Do not assume resilience works because it exists in code.

## Coverage
Focus on: all business logic branches, all authorization paths, all error paths, all integration boundaries.
100% coverage with shallow tests < 70% with meaningful tests.
