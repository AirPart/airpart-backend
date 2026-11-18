# ADR 0004 — Adopt Monorepo Layout with Shared API Types Package

- **Status:** Proposed
- **Date:** 2026-11-18
- **Decision owner:** Mohammadhosein Ajorloo (Lead Developer)
- **Scope:** Repository structure, full-stack type synchronization, and project layout
- **Related issue:** https://github.com/AirPart/airpart-backend/issues/87
- **Supersedes:** —

---

## 1. Context

The AirPart ERP project is initiating its frontend development alongside an existing Django backend. As a solo-maintained repository, maintaining consistency between the backend API contract (Django domain models and DRF/API schemas) and the frontend TypeScript client types is critical. Duplicating types manually across separate repositories leads to drift, broken contracts, and high maintenance overhead. We need to decide how to structure the repository and synchronize data types between backend and frontend.

## 2. Decision Drivers

| #   | Driver                         | Weight | Why it matters                                                                                          |
| --- | ------------------------------ | ------ | ------------------------------------------------------------------------------------------------------- |
| D1  | Type Safety & Synchronization  | 5      | Frontend and backend must stay in sync without manual duplication.                                      |
| D2  | Operational Overhead           | 4      | As a solo developer, multi-repo CI/CD and package publishing add unnecessary friction.                  |
| D3  | Discoverability & Traceability | 3      | Keeping backend, frontend, and shared contracts in one timeline simplifies code reviews and atomic PRs. |
| D4  | Build Isolation                | 2      | Independent test and build commands must remain functional without cross-pollution.                     |

## 3. Options Considered

### Option A — Monorepo with Shared Types Package (Chosen)

- **Strengths:** Single repository for backend, frontend, and shared type definitions; atomic commits updating both API and client; zero-publish overhead for shared packages.
- **Weaknesses:** Requires root-level workspace tooling and careful separation of dependency boundaries.
- **Official documentation:** https://docs.npmjs.com/cli/v10/using-npm/workspaces

### Option B — Polyrepo (Separate Backend and Frontend Repositories)

- **Strengths:** Strict boundary enforcement; independent repository lifecycles.
- **Weaknesses:** High overhead for a solo developer; requires publishing shared types to a registry or copying files manually; coordination overhead for contract updates.
- **Official documentation:** N/A

### Option C — Backend-Embedded Frontend (Django Templates / Static Serving)

- **Strengths:** Simplest possible deployment; single codebase from day one.
- **Weaknesses:** Poor modern frontend DX (React/Next.js/Vite); manual DOM manipulation or cumbersome asset pipelines; weak TypeScript integration with API contracts.
- **Official documentation:** https://docs.djangoproject.com/

## 4. Comparison

| Criterion            | Weight | Option A (Monorepo) | Option B (Polyrepo) | Option C (Django Templates) |
| -------------------- | ------ | ------------------- | ------------------- | --------------------------- |
| D1 (Type Safety)     | 5      | 5 (25)              | 3 (15)              | 2 (10)                      |
| D2 (Overhead)        | 4      | 4 (16)              | 1 (4)               | 5 (20)                      |
| D3 (Traceability)    | 3      | 5 (15)              | 2 (6)               | 4 (12)                      |
| D4 (Build Isolation) | 2      | 4 (8)               | 5 (10)              | 5 (10)                      |
| **Weighted total**   |        | **64**              | **35**              | **52**                      |

## 5. Decision

1. Adopt a Monorepo structure containing a `backend/` directory for the Django application, a `frontend/` directory for the web client, and a `packages/api-types/` shared package for API contracts and TypeScript types.
2. Establish a workspace root configuration to manage dependencies and testing seamlessly.
3. Ensure backend domain models (`User`, `Role`) serve as the single source of truth for generating or validating shared client types.

## 6. Consequences

### Positive

- Guaranteed type synchronization between backend API responses and frontend client models.
- Single atomic PRs for features crossing the full-stack boundary.
- Zero overhead of publishing shared packages to external registries.

### Negative / Risks

- Root directory structure changes require updating Docker and CI paths.
- Potential coupling if workspace boundaries are not respected.

### Mitigations

- Keep strict separation between backend python code, frontend typescript code, and shared contract packages.
- Configure workspace test runners to execute backend pytest and frontend checks independently.

## 7. Rejected Options

| Option           | Reason for rejection                                                                                             |
| ---------------- | ---------------------------------------------------------------------------------------------------------------- |
| Polyrepo         | Failed on D2 (Operational Overhead) due to excessive solo-developer friction and release coordination.           |
| Django Templates | Failed on D1 (Type Safety) due to lack of native modern SPA TypeScript type generation and developer experience. |

## 8. Proof of Concept / Validation

- **Branch:** `87-docs/adr-monorepo-architecture`
- **Scope of the PoC:** Domain models validated, workspace structure planned.
- **Acceptance criteria:** ADR written, indexed, and committed independently before workspace restructuring.
- **Evidence:** Clean git status, passing backend pytest suite.

## 9. References

- Monorepo patterns and practices: https://monorepo.tools
- npm Workspaces: https://docs.npmjs.com/cli/v10/using-npm/workspaces

## 10. Review Trigger

If team size expands beyond 5 concurrent full-stack developers or if independent release lifecycles between backend and frontend become a hard business requirement.
