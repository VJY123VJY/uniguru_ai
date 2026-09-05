# TANTRA Runtime Deployment Proof

## Validation Scope

This artifact records the deployment configuration currently present in the UniGuru repository.

It does not claim successful production deployment.

## Docker Runtime

The repository contains:

- `Dockerfile`
- `docker-compose.yml`

The application container exposes port `8000`.

The Docker runtime starts the UniGuru API through:

`uvicorn service.api:app`

## Compose Services

The current Compose configuration defines:

- `uniguru-api`
- `node-backend`
- `nginx`
- `certbot`

The services share the `uniguru_net` Docker network.

## UniGuru API

The API container is configured with:

- host: `0.0.0.0`
- port: `8000`

## Runtime Health

The application has already been validated locally through:

- `/health` → `ok`
- `/ready` → `ready`
- `/health/live` → `alive`

## CI

The repository contains the TANTRA GitHub Actions workflow:

`.github/workflows/tantra-runtime-ci.yml`

The workflow validates:

- dependency installation
- automated tests
- TANTRA capability metadata
- positive runtime execution
- negative safety-gate execution
- repository whitespace

## Production Validation Status

Status:

`PENDING`

The following still require validation in the target deployment environment:

1. Container startup.
2. Service-to-service connectivity.
3. Public/API accessibility.
4. Production `/health`.
5. Production `/ready`.
6. Production `/health/live`.
7. Positive TANTRA curriculum execution.
8. Negative TANTRA safety-gate execution.
9. Production configuration.
10. Observer verification.

## Evidence Boundary

This document is deployment-readiness evidence only.

It must not be interpreted as proof that production deployment has been completed.

## Current Assessment

The repository contains a deployable Docker/Compose configuration and CI validation.

Target-environment production deployment remains an outstanding closure activity.
