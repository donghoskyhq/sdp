# Sky Dev Platform (SDP)

SDP is an internal self-service platform for creating and running Sky software projects. This
repository currently contains the minimum platform skeleton only: a Next.js Web application, a
FastAPI core API, an RQ worker, PostgreSQL configuration, and a Redis-backed queue.

GitHub repository creation, Harness management, controlled update pull requests, and deployment
provisioning for Railway, Vercel, or AWS Amplify are intentionally out of scope for this initial
commit.

## Architecture

```text
Next.js Web
    -> FastAPI Core API
        -> PostgreSQL
    -> Python Worker (through Redis Queue)
        -> PostgreSQL
```

The Web status page calls FastAPI from the Next.js server through `API_BASE_URL`. In Railway this can
be a private service URL, so no internal API address is sent to the browser.

## Repository layout

```text
apps/web/                 Next.js App Router frontend
services/core/            FastAPI API and Python worker
services/core/src/api/    API routes and Alembic environment
services/core/src/worker/ Worker entry point and placeholder jobs
infra/railway/            Railway service setup notes
docker-compose.yml        Full local container stack
```

## Prerequisites

- Node.js 20.9 or newer and npm
- Python 3.12 or newer
- Docker with Docker Compose (for PostgreSQL and Redis, or the full container stack)

## Configuration

Copy the example file for local development:

```bash
cp .env.example .env
```

The checked-in values are local-only defaults. Keep real secrets in local `.env` files or the target
platform's secret manager; `.env` files are ignored by Git.

## Run locally with native Web/API/Worker processes

Start PostgreSQL and Redis:

```bash
docker compose up -d postgres redis
```

Install the Web dependencies and run Next.js:

```bash
npm --prefix apps/web install
npm run web:dev
```

In another terminal, create the Python environment and install the API/worker package:

```bash
python3.12 -m venv services/core/.venv
source services/core/.venv/bin/activate
python -m pip install -e 'services/core[dev]'
set -a
source .env
set +a
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Run the worker in another activated terminal after exporting the same environment variables:

```bash
source services/core/.venv/bin/activate
set -a
source .env
set +a
python -m worker.main
```

Open the Web app at <http://localhost:3000>, FastAPI documentation at
<http://localhost:8000/docs>, and the API health endpoint at <http://localhost:8000/health>.

## Run the full stack with Docker Compose

```bash
docker compose up --build
```

This builds the same Web, API, and Worker Dockerfiles intended for Railway and starts PostgreSQL and
Redis. Stop the stack with `docker compose down`. Add `-v` only when you intentionally want to remove
local database and Redis volumes.

## Worker placeholder job

The worker consumes the `default` queue. To enqueue the non-provisioning placeholder while the worker
is running:

```bash
source services/core/.venv/bin/activate
set -a
source .env
set +a
python -c 'from redis import Redis; from rq import Queue; from shared.config import get_settings; s = get_settings(); Queue(s.queue_name, connection=Redis.from_url(str(s.redis_url))).enqueue("worker.jobs.provision_project", "example-project")'
```

The worker logs both receipt and completion. The job does not call GitHub, Harness, Railway, Vercel,
or AWS Amplify.

## Validation

Frontend checks:

```bash
npm run web:lint
npm run web:typecheck
npm run web:build
```

Python checks (with `services/core[dev]` installed):

```bash
ruff check services/core/src services/core/tests
mypy --config-file services/core/pyproject.toml
pytest -c services/core/pyproject.toml services/core/tests
```

## Railway

See [infra/railway/README.md](infra/railway/README.md) for the four service definitions, Dockerfile
selection, internal service URLs, and required variables. This repository does not contain Railway
credentials and does not create or deploy Railway resources.
