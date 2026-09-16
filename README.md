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

Install the frontend dependencies first, then run the two development servers:

```bash
npm install
npm run dev
```

The repository also exposes separate commands:

```bash
npm run frontend   # frontend dev server
npm run backend    # backend API on port 8000
```

If the frontend and backend are started separately, confirm the backend is reachable on port 8000 before testing API-backed screens.

## API readiness check

The backend exposes `GET /ready` as a lightweight readiness check. A healthy response indicates that the API can serve requests and that the required model state is available. Use this endpoint from local checks or deployment health probes instead of treating the process being reachable as proof that inference is ready.

## Goal

Turn financial text into useful sentiment signals while keeping the application architecture easy to experiment with and extend.

## Status

Active development. Model, API, and frontend work may evolve as experiments are evaluated.

## Troubleshooting

- If `npm run dev` fails, run `npm install` again and check the Node.js version expected by the project dependencies.
- If API-backed pages cannot connect, start the backend separately and verify port 8000 is available.
- If `/ready` reports an unavailable model, check the backend model-loading configuration before testing inference endpoints.
- When model behavior changes, record the input and expected sentiment outcome so regressions are easier to reproduce.

## Reproducibility note

When reporting a model or API issue, include the relevant command, a minimal input example, the expected result, and the observed result. Avoid including API keys, account credentials, or other sensitive data.
