# API Readiness Contract

FinSight AI exposes two related service checks with different purposes.

## `/health`

Use `GET /health` for service health information. It returns a successful response while the API process is running and reports whether the model is loaded.

## `/ready`

Use `GET /ready` when a caller needs to know whether model-backed inference can be served.

| Response | Meaning |
| --- | --- |
| `200 OK` | API and model state are ready for inference. |
| `503 Service Unavailable` | API is running, but the model is not ready. |

Keep liveness and readiness checks separate in deployment configuration. A running process is not necessarily ready to serve model-backed requests.

## Troubleshooting

If `/ready` returns `503`, inspect model-loading configuration and startup logs before testing inference endpoints.