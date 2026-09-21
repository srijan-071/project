# Health-check contract

Use two endpoints with different operational meanings:

- `/health` answers whether the application process is running.
- `/ready` answers whether the application can safely receive normal traffic.

## Client guidance

Load balancers and orchestration probes should use `/ready` for traffic decisions. Use `/health` for basic process/liveness diagnostics.

A readiness failure should not be treated as an application crash. It can indicate that a dependency, migration, or required configuration is temporarily unavailable.

## Response expectations

Keep probe responses small and deterministic. Avoid exposing credentials, stack traces, dependency secrets, or internal topology in either endpoint.
