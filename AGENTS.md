# AGENTS.md

## Domain
This is a risk calculation system.

## Critical Rules
- Numerical stability is critical
- Do not change RNG behavior
- Maintain reproducibility

## Architecture
- Separate pricing logic and infrastructure
- Avoid tight coupling

## Performance
- Minimize memory allocation
- Prefer batch processing
