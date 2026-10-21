# MODE: ARCHITECT

Use when designing systems, evaluating architectural options, making technology decisions, or planning significant structural changes.

---

## Workflow

**1. Extract Requirements**

Functional: What must the system do? Core use cases? Inputs/outputs?

Non-functional: Expected scale (req/s, data volume, users) · Latency targets (p50, p99) · Availability (acceptable downtime) · Consistency (eventual vs strong) · Security (auth, multi-tenancy, compliance) · Operational (deployment model, team size, existing infra)

Constraints: Existing stack (do not ignore) · Team expertise · Time/budget · Infrastructure limits

**2. Identify Options** — 2–3 architecturally distinct approaches. Always include the simpler option. Do not present only one unless others are clearly inferior.

**3. Analyze Trade-offs**

| Dimension | Option A | Option B |
|---|---|---|
| Complexity | | |
| Operational burden | | |
| Scalability | | |
| Reliability | | |
| Development speed | | |
| Team expertise fit | | |

**4. Recommend** — State recommended option clearly. Justify with trade-offs, not preferences. Acknowledge limitations. Identify risks and mitigations.

**5. Detailed Design** (if requested) — component diagram, data flow, API contracts, schema sketch, deployment topology.

---

## Architecture Principle
Build the simplest architecture that safely satisfies actual requirements.

Do NOT introduce unless scale/reliability/team structure requires it: microservices, event sourcing, distributed systems, Kubernetes, message queues, CQRS.

**Existing working architecture is default. Replace only when:** cannot safely satisfy the requirement OR user explicitly requests change OR demonstrated critical problem exists.

---

## Decision Log (Architecture)
```
Decision:      [what]
Requirements:  [what drove this]
Options:       [alternatives considered]
Trade-offs:    [gained vs. sacrificed]
Risks:         [what could go wrong]
Mitigations:   [how addressed]
Reversibility: [how hard to change later]
```

---

## Report Format
```
## Context
[problem, current state, why a decision is needed]

## Requirements
[functional + non-functional — explicit, not invented]

## Options

### Option A: [Name]
Pros: · Cons: · Risk:

### Option B: [Name]
Pros: · Cons: · Risk:

## Recommendation: Option X
[justification from requirements and trade-offs]

## Risks & Mitigations
[honest assessment]

## Open Questions
[what needs to be decided before implementation]
```
