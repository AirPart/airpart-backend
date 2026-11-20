# ADR 0005 — Frontend Serving and Container Topology

- **Status:** Proposed
- **Date:** 2026-11-20
- **Decision owner:** Lead Software Engineer
- **Scope:** Frontend deployment, Docker container topology, and Nginx reverse proxy routing
- **Related issue:** https://github.com/AirPart/airpart-backend/issues/100
- **Supersedes:** —

---

## 1. Context

The AirPart ERP application consists of a Django REST backend (`backend/`), a Vite/React SPA frontend (`frontend/`), and shared TypeScript types (`packages/api-types/`). Currently, `docker compose up` only starts the backend API, leaving the frontend without containerization. Developers must run two manual development servers, and production-like container topology remains unverified.

To ship a containerized environment, we must decide how the frontend static assets and Single Page Application (SPA) routing are served in Docker and production environments, specifically addressing API proxying (`/api/`), deep routing (SPA fallback), and asset caching.

## 2. Decision Drivers

| #   | Driver                           | Weight | Why it matters                                                                                                          |
| --- | -------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------- |
| D1  | Bundle & Monorepo Build Context  | 5      | Frontend relies on `@airpart/api-types` workspace; container build must support monorepo root context without breaking. |
| D2  | SPA Deep Routing Support         | 4      | Direct access or browser refresh on deep routes (e.g., `/parts/catalog/123`) must not return 404.                       |
| D3  | Same-Origin API Proxying         | 4      | Avoids complex CORS configurations in development and production by proxying `/api/` directly through Nginx.            |
| D4  | Production Performance & Caching | 3      | Long-lived caching for hashed Vite assets (`/assets/`) and no caching for `index.html`.                                 |
| D5  | Operational Simplicity           | 3      | Easy local testing with Docker Compose and predictable resource usage.                                                  |

## 3. Options Considered

### Option A — Nginx Same-Origin Reverse Proxy (Chosen)

- **Strengths:** Single entrypoint on port 8080, Nginx serves SPA static files and proxies `/api/` to Django backend cleanly, eliminates CORS overhead, native SPA fallback via `try_files`.
- **Weaknesses:** Requires managing an Nginx configuration file and multi-stage Docker build.
- **Official documentation:** https://nginx.org/en/docs/

### Option B — Django Static / Template Serving

- **Strengths:** Only one container/process for serving static web files if integrated into Django's static files storage.
- **Weaknesses:** Sub-optimal for high-concurrency SPA asset delivery, complicates Vite asset pipeline integration, forces Django to handle client-side routing fallbacks.
- **Official documentation:** https://docs.djangoproject.com/en/5.2/howto/static-files/

### Option C — Standalone CDN / Object Storage (S3/MinIO) + Separate API Gateway

- **Strengths:** Ultimate scalability for static assets.
- **Weaknesses:** Massive over-engineering for current ERP scale, introduces external cloud dependencies or complex MinIO bucket provisioning in local Docker compose.
- **Official documentation:** https://docs.aws.amazon.com/s3/

## 4. Comparison

| Criterion                   | Weight | Option A (Nginx Proxy) | Option B (Django Static) | Option C (CDN/Object Storage) |
| --------------------------- | ------ | ---------------------- | ------------------------ | ----------------------------- |
| D1 (Monorepo Build Context) | 5      | 5 (25)                 | 4 (20)                   | 3 (15)                        |
| D2 (SPA Deep Routing)       | 4      | 5 (20)                 | 2 (8)                    | 4 (16)                        |
| D3 (Same-Origin Proxy)      | 4      | 5 (20)                 | 5 (20)                   | 2 (8)                         |
| D4 (Performance & Caching)  | 3      | 5 (15)                 | 3 (9)                    | 5 (15)                        |
| D5 (Operational Simplicity) | 3      | 4 (12)                 | 4 (12)                   | 1 (3)                         |
| **Weighted total**          | **19** | **92**                 | **69**                   | **57**                        |

## 5. Decision

We choose **Option A (Nginx Same-Origin Reverse Proxy)** using a multi-stage Docker build (`node:22-alpine` for building and `nginx:1.27-alpine` for serving).

The concrete architecture follows:

1. The Docker build context is set to the repository root to allow access to workspace dependencies (`packages/api-types`).
2. Nginx serves the SPA build artifacts from `/usr/share/nginx/html`.
3. Requests matching `/api/` are proxied to `http://backend:8000` without a trailing slash in `proxy_pass` to preserve the complete URI path.
4. SPA routing is handled via `try_files $uri $uri/ /index.html;`.
5. Static assets under `/assets/` include long-term caching headers, while `index.html` disables caching.

## 6. Consequences

### Positive

- Unified containerized stack runnable via `docker compose up`.
- Zero CORS friction in production/staging environments.
- Reliable asset hashing and performance optimization via Nginx.

### Negative / Risks

- Misconfigured `proxy_pass` trailing slashes could strip URI segments.

### Mitigations

- Enforce explicit `proxy_pass http://backend:8000;` without trailing slash in `nginx.conf` and verify via integration curls.

## 7. Rejected Options

| Option                        | Reason for rejection                                                                      |
| ----------------------------- | ----------------------------------------------------------------------------------------- |
| Option B (Django Static)      | Failed D2 (poor SPA fallback support) and D4 (sub-optimal asset delivery performance).    |
| Option C (CDN/Object Storage) | Failed D5 (operational complexity and over-engineering for local/initial ERP deployment). |

## 8. Proof of Concept / Validation

- **Branch:** `86-feat/frontend-dockerfile-topology`
- **Scope of the PoC:** Multi-stage frontend Dockerfile, Nginx configuration, Docker Compose integration.
- **Acceptance criteria:** `docker compose build` succeeds, `/api/` returns JSON, deep routes return `index.html`.
- **Evidence:** Local `docker compose` execution output and `curl` status verifications.

## 9. References

- Nginx Core Documentation: https://nginx.org/en/docs/
- Vite Production Build Guide: https://vite.dev/guide/build.html
- Docker Multi-stage Builds: https://docs.docker.com/build/building/multi-stage/

## 10. Review Trigger

Reopened if peak frontend asset traffic requires dedicated CDN distribution or if micro-frontend architecture splits the SPA into independently deployed modules.
