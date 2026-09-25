# FinSight AI

A financial sentiment intelligence project built around a custom Transformer-based NLP pipeline.

## Project layout

```text
project/
├── frontend/   # web client
├── backend/    # Python API / model layer
└── package.json
```

## Local development

```bash
npm install
npm run dev
```

The repository also exposes `npm run frontend` and `npm run backend` for separate development servers.

## API readiness check

The backend exposes `GET /ready`.

- `200 OK` means the API and required model state are ready.
- `503 Service Unavailable` means the process is running but the model is not ready.
- Use `/ready` for readiness decisions and keep liveness checks separate.

## Reporting model issues

For reproducible model or API issues, include:

1. Exact command or endpoint.
2. Minimal shareable input.
3. Expected output.
4. Actual output.
5. Model/version or configuration, when known.
6. Whether the issue reproduces consistently.

Never include API keys, credentials, private customer data, or other secrets.

## Suggested verification flow

Before opening a bug report, run the readiness check and record the response:

```bash
curl -i http://localhost:8000/ready
```

For model behavior changes, compare the same input against the known model/configuration and include the smallest reproducible example in the report.

## Goal

Turn financial text into useful sentiment signals while keeping the application architecture easy to experiment with and extend.

## Status

Active development. Model, API, and frontend work may evolve as experiments are evaluated.
