# API Error Handling

Keep API errors predictable so the frontend and deployment checks can distinguish invalid input, unavailable dependencies, and unexpected failures.

## Response categories

- `4xx`: the request cannot be processed because of client input or authorization state.
- `503`: the service is reachable but a required dependency or model is not ready.
- `5xx`: an unexpected server-side failure occurred.

## Client behavior

Frontend code should treat the HTTP status as the primary signal and avoid parsing error-message text to decide what to do. Display a user-safe message and keep implementation details out of responses intended for end users.

## Debugging checklist

1. Record the request path and HTTP status.
2. Reproduce with the smallest valid input.
3. Check `/ready` when the failure may be related to model availability.
4. Inspect server logs for the underlying exception.
5. Remove credentials and personal data before sharing logs in an issue.

## Design rule

Use stable status codes and structured error fields rather than changing response text as an implicit API contract.