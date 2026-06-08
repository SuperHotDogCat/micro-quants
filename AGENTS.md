# AGENTS.md

## Domain
This is a risk calculation system.

The system is used for financial analytics and risk-sensitive workloads.
Correctness, reproducibility, auditability, and operational safety are higher priority than raw feature velocity.

The AI agent acts as an engineering assistant only.
The AI agent MUST NOT autonomously operate financial workflows.

---

## Critical Rules

- Numerical stability is critical
- Do not change RNG behavior
- Maintain reproducibility

Additionally:

- Do not silently change floating-point precision
- Do not introduce nondeterministic execution
- Do not change random seeds without explicit approval
- Avoid hidden state mutations
- Avoid time-dependent behavior
- Preserve deterministic ordering in parallel execution

Any change affecting:
- Monte Carlo simulation
- pricing outputs
- VaR results
- scenario generation
- stochastic processes

requires explicit human review.

---

## Architecture

- Separate pricing logic and infrastructure
- Avoid tight coupling

Additionally:

- Separate domain logic from orchestration logic
- Business logic MUST NOT depend on infrastructure details
- Services MUST communicate through stable interfaces only
- Avoid direct database sharing between domains
- Prefer immutable event-based communication
- Avoid hidden side effects across services

Preferred patterns:
- Hexagonal Architecture
- CQRS
- Event-Driven Architecture
- Capability-based APIs

Avoid:
- distributed transactions
- shared mutable state
- deep synchronous RPC chains
- implicit dependencies

---

## Performance

- Minimize memory allocation
- Prefer batch processing

Additionally:

- Avoid unnecessary tensor/data copies
- Reuse buffers where safe
- Preserve cache locality
- Avoid excessive serialization/deserialization
- Prefer vectorized operations
- Avoid per-request model initialization
- Minimize synchronization points in parallel execution

Performance optimizations MUST NOT:
- change numerical behavior
- reduce reproducibility
- bypass validation
- weaken auditability

---

## Compliance and Safety

The agent MUST NOT:

- provide investment advice wording
- generate guaranteed-return claims
- bypass approval workflows
- modify production financial records directly
- access customer PII without approval
- execute production trades
- disable audit logging

Potentially regulated actions MUST:
- require human approval
- emit audit logs
- pass policy validation

When uncertain about compliance:
- stop execution
- escalate to humans
- fail closed

Never guess legal or regulatory interpretations.

---

## Data Access Rules

Allowed:
- synthetic datasets
- anonymized analytics
- schema metadata
- non-production environments

Restricted:
- raw customer data
- production credentials
- encryption keys
- private trading records

The agent MUST use approved APIs only.
Direct production SQL access is prohibited.

---

## Code Generation Requirements

Generated code MUST:
- include structured logging
- include timeout handling
- include retry limits
- include explicit error handling
- include deterministic behavior where applicable
- include tracing/audit hooks

Generated code SHOULD:
- isolate side effects
- minimize global state
- favor pure functions
- expose typed interfaces

Generated code MUST NOT:
- silently swallow exceptions
- introduce hidden retries
- hardcode secrets
- bypass policy checks

---

## Auditability

Important operations MUST emit:
- timestamp
- actor identity
- request ID
- correlation ID
- policy evaluation results
- affected resources

Audit logs MUST be append-only.

The system MUST support:
- replayability
- traceability
- rollback analysis

---

## Deployment Rules

The agent MAY:
- generate deployment configs
- generate CI/CD workflows
- propose infrastructure changes

The agent MUST NOT:
- deploy directly to production
- modify IAM policies autonomously
- disable monitoring
- change firewall/network rules
- rotate secrets automatically

Human review is REQUIRED for:
- production deployment
- schema migration
- pricing model changes
- risk logic changes
- compliance logic changes
- authentication/authorization changes

---

## Operational Philosophy

Prioritize:
1. correctness
2. reproducibility
3. auditability
4. safety
5. performance

over:
- convenience
- autonomy
- aggressive optimization

When tradeoffs exist:
- prefer explicitness over magic
- prefer isolation over coupling
- prefer deterministic behavior over opportunistic optimization
- prefer recoverability over availability
