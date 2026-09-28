# Railway deployment preparation

This repository is prepared for four SDP application/data services. These instructions describe
configuration only; they do not create Railway resources or supply production credentials.

## Services

| Railway service | Source/root directory | Dockerfile or start command | Purpose |
| --- | --- | --- | --- |
| `sdp-web` | `apps/web` | `Dockerfile` | Next.js web service |
| `sdp-api` | `services/core` | `Dockerfile.api` | FastAPI core API |
| `sdp-worker` | `services/core` | `Dockerfile.worker` | RQ background worker |
| PostgreSQL | Railway managed service | Managed by Railway | Primary database |
| Redis | Railway managed service | Managed by Railway | Queue backend |

The API Dockerfile honors Railway's runtime `PORT`. The web image defaults to port `3000`; configure
Railway networking to route to that port. The worker does not expose an HTTP port.

The image start commands are:

- Web: `node server.js` from the Next.js standalone build.
- API: runs `alembic upgrade head`, then starts Uvicorn on `${PORT:-8000}`.
- Worker: `python -m worker.main`.

## Required variables

Use Railway service references rather than copying secret values between services.

### `sdp-web`

| Variable | Example shape | Notes |
| --- | --- | --- |
| `API_BASE_URL` | `http://sdp-api.railway.internal:8000` | Private API URL, used server-side by Next.js |
| `PORT` | `3000` | Optional; the image defaults to `3000` |

The browser requests the status page from `sdp-web`; the Next.js server calls FastAPI over Railway's
private network. Do not expose `API_BASE_URL` through a `NEXT_PUBLIC_*` variable.

### `sdp-api`

| Variable | Example shape | Notes |
| --- | --- | --- |
| `SDP_ENVIRONMENT` | `production` | Runtime environment label |
| `LOG_LEVEL` | `INFO` | Application log level |
| `DATABASE_URL` | Railway PostgreSQL reference | Must use a SQLAlchemy-compatible `postgresql+psycopg://` URL |
| `REDIS_URL` | Railway Redis reference | Typically `redis://...` |
| `CORS_ORIGINS` | `["https://sdp-web.example"]` | JSON array of allowed public Web origins |
| `PORT` | Supplied by Railway | Read by `Dockerfile.api` |

If Railway supplies a `postgresql://` URL, define `DATABASE_URL` as a reference-derived value with
the `postgresql+psycopg://` scheme expected by SQLAlchemy.

### `sdp-worker`

| Variable | Example shape | Notes |
| --- | --- | --- |
| `SDP_ENVIRONMENT` | `production` | Runtime environment label |
| `LOG_LEVEL` | `INFO` | Worker log level |
| `DATABASE_URL` | Same PostgreSQL reference as API | Project provisioning state |
| `REDIS_URL` | Same Redis reference as API | RQ connection |
| `QUEUE_NAME` | `default` | Queue consumed by the worker |
| `GITHUB_TOKEN` | secret | GitHub App installation or fine-grained token; worker only |
| `GITHUB_OWNER` | organization login | Owner for newly provisioned repositories |
| `GITHUB_OWNER_TYPE` | `organization` | Use `user` for a personal owner |
| `GITHUB_API_URL` | `https://api.github.com` | Override only for GitHub Enterprise Server |
| `GITHUB_REPOSITORY_PRIVATE` | `true` | Keep new repositories private by default |

## Internal connectivity

- `sdp-web` accesses `sdp-api` through `API_BASE_URL`, using the API service's Railway private DNS
  name and port.
- `sdp-api` and `sdp-worker` access managed PostgreSQL through `DATABASE_URL`.
- `sdp-api` and `sdp-worker` access managed Redis through `REDIS_URL`; the worker consumes
  `QUEUE_NAME`.
- Only `sdp-web` needs a public domain for this skeleton. Expose `sdp-api` publicly only if a future
  approved integration requires it; if exposed, set `CORS_ORIGINS` to the exact Web origin.

Railway tokens, provider credentials, generated passwords, private URLs containing credentials, and
other secrets must be stored in Railway variables. They must never be committed to this repository.
