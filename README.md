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

## Goal

Turn financial text into useful sentiment signals while keeping the application architecture easy to experiment with and extend.

## Status

Active development. Model, API, and frontend work may evolve as experiments are evaluated.
