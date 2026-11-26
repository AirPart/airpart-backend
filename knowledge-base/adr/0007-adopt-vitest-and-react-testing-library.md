# ADR 0007 — Adopt Vitest and React Testing Library

- **Status:** Proposed
- **Date:** 2026-11-26
- **Decision owner:** Mohammad Hosein Ajorloo (Lead Developers)
- **Scope:** Frontend testing in `frontend/` (`@airpart/frontend`)
- **Related issue:** https://github.com/AirPart/airpart-backend/issues/121
- **Supersedes:** —

---

## 1. Context

The AirPart monorepo contains a frontend workspace at `frontend/`, identified as
`@airpart/frontend`. The project needs a repeatable way to run automated
frontend tests.

The current branch is:

`121-chore/setup-automated-testing-infrastructure-with-vitest-and-react-testing-library`

Vitest has been configured or introduced in the frontend workspace. A test run
has not yet completed successfully. The latest reported run failed while
loading `src/test/setup.ts`, because it imports `./mocks/server` and that module
could not be resolved.

A manual Rollup package installation allowed Vitest to start, but the
installation also showed a Rollup version mismatch. This workaround is not
evidence that the dependency installation is correct or reproducible.

The task's exact acceptance criteria and issue URL were not provided when this
ADR was drafted. They must be added before the decision is accepted and before
implementation is considered complete.

## 2. Decision Drivers

The weights below are provisional. Review them against the task's acceptance
criteria before accepting this ADR.

| #   | Driver                                 | Weight | Why it matters                                                                                             |
| --- | -------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| D1  | Fit with the existing frontend tooling | 3      | The test runner should work with the frontend's existing build and development setup.                      |
| D2  | Component-testing support              | 3      | The project needs to test user-visible React behavior, not only isolated utility functions.                |
| D3  | Reproducible local and CI installation | 3      | Developers and CI should be able to install dependencies and run tests without manual package workarounds. |
| D4  | Maintainability and documentation      | 2      | The test setup should be understandable and straightforward to maintain.                                   |

## 3. Options Considered

### Option A — Vitest and React Testing Library

- **Strengths:**
  - Vitest is designed to work with Vite-based projects.
  - React Testing Library supports testing React components through user-facing
    behavior.
  - The existing branch and setup work are already oriented around these tools.
- **Weaknesses:**
  - The current test setup has an unresolved import for `./mocks/server`.
  - The Rollup workaround exposed a version mismatch and does not establish
    reproducible installation.
  - The setup still needs to be validated with the actual task acceptance
    criteria.
- **Official documentation:**
  - Vitest: <https://vitest.dev/>
  - React Testing Library: <https://testing-library.com/docs/react-testing-library/intro/>

### Option B — Jest and React Testing Library

- **Strengths:**
  - Jest is a widely documented JavaScript testing framework.
  - React Testing Library can be used to test React components.
- **Weaknesses:**
  - It introduces a different test-runner setup from the current Vite-oriented
    work.
  - It would require evaluating and configuring compatibility with this
    frontend workspace.
- **Official documentation:**
  - Jest: <https://jestjs.io/docs/getting-started>
  - React Testing Library: <https://testing-library.com/docs/react-testing-library/intro/>

### Option C — Keep the current status quo without a frontend test runner

- **Strengths:**
  - No new test-runner configuration or dependencies are required immediately.
- **Weaknesses:**
  - Automated frontend tests cannot be run through a standard test setup.
  - Regressions in frontend behavior would not be covered by this testing
    infrastructure.
- **Official documentation:** Not applicable; this option does not adopt a test framework.

## 4. Comparison

The scores below are provisional estimates on a 1–5 scale. They are not
benchmarks. Each cell shows `score × weight = weighted score`. Re-score the
options after reviewing the task's acceptance criteria and testing the
dependency installation on a clean environment.

| Criterion                              | Weight | A — Vitest + RTL | B — Jest + RTL | C — Status quo |
| -------------------------------------- | -----: | ---------------: | -------------: | -------------: |
| Fit with existing frontend tooling     |      3 |       5 × 3 = 15 |      3 × 3 = 9 |      2 × 3 = 6 |
| Component-testing support              |      3 |       4 × 3 = 12 |     4 × 3 = 12 |      1 × 3 = 3 |
| Reproducible local and CI installation |      3 |        2 × 3 = 6 |      3 × 3 = 9 |     5 × 3 = 15 |
| Maintainability and documentation      |      2 |        4 × 2 = 8 |      4 × 2 = 8 |      2 × 2 = 4 |
| **Weighted total**                     |        |           **41** |         **38** |         **28** |

## 5. Decision

**Proposed decision:** Adopt Vitest as the test runner and React Testing Library
for React component tests in `frontend/`, provided that the setup can be
installed and run reproducibly and satisfies the task's acceptance criteria.

The concrete architecture, if accepted, is:

1. Keep the test-runner configuration within the `frontend/` workspace.
2. Use Vitest to discover and execute frontend tests.
3. Use React Testing Library for component-level tests focused on
   user-observable behavior.
4. Ensure test setup imports resolve to files that exist in the repository.
5. Verify installation and test execution from a clean dependency install
   without manually adding platform-specific packages.
6. Add or update tests according to the task's acceptance criteria once those
   criteria are available.

## 6. Consequences

### Positive

- Frontend tests can be run through a dedicated test runner.
- React component behavior can be tested using user-facing queries and
  interactions.
- The chosen tools align with the Vite-based frontend direction, subject to
  successful clean-install validation.

### Negative / Risks

- The current test setup is not yet validated: `src/test/setup.ts` cannot
  resolve `./mocks/server`.
- The manual Rollup package workaround exposed a version mismatch. It may hide
  or complicate the underlying dependency installation issue.
- The actual task acceptance criteria are not included in this draft, so the
  selected test scope may need revision.

### Mitigations

- Resolve the missing `./mocks/server` import by either adding the intended
  module or correcting/removing the import, according to the intended test
  setup.
- Investigate and fix the Rollup optional-dependency/version mismatch in the
  package manifests and lockfile; do not rely on a manual local installation.
- Run the test command after a clean install in the frontend workspace and in
  CI.
- Add the task's issue URL and acceptance criteria before changing the ADR
  status from `Proposed` to `Accepted`.

## 7. Rejected Options

| Option                                                     | Reason for rejection                                                                                                                                                                                         |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Jest and React Testing Library                             | Not selected provisionally because the current work is already oriented around Vitest and Vite. Reconsider if the task's acceptance criteria or clean-install validation show a concrete advantage for Jest. |
| Keep the current status quo without a frontend test runner | Not selected provisionally because it does not provide a standard way to execute automated frontend tests.                                                                                                   |

## 8. Proof of Concept / Validation

- **Branch:** `121-chore/setup-automated-testing-infrastructure-with-vitest-and-react-testing-library`
- **Scope of the PoC:** Run Vitest in `frontend/` and verify that the React
  Testing Library setup and test files can be loaded and executed.
- **Acceptance criteria:** TODO — copy or link the exact acceptance criteria
  from the task. They were not included in the information available for this
  draft.
- **Evidence:**
  - A manual installation of `@rollup/rollup-linux-x64-gnu@4.68.7` allowed
    Vitest `v5.1.2` to start.
  - That run reported `No test files found`.
  - A later test run reported that `src/test/setup.ts` could not resolve
    `./mocks/server`.
  - The manual Rollup installation showed a version mismatch with the installed
    Rollup package.
  - **Conclusion:** Validation is incomplete. No successful test suite run or
    clean-install result has been reported.

## 9. References

- Vitest documentation: <https://vitest.dev/>
- React Testing Library documentation: <https://testing-library.com/docs/react-testing-library/intro/>
- Jest documentation: <https://jestjs.io/docs/getting-started>

## 10. Review Trigger

Reopen this decision if any of the following occurs:

- The task's acceptance criteria require a test runner or testing approach
  incompatible with Vitest and React Testing Library.
- Vitest cannot be installed and run reliably from a clean checkout using the
  committed manifests and lockfile, without manual package installation.
- The frontend build tooling changes in a way that makes the current Vitest
  integration unsuitable.
- The team adopts a repository-wide testing standard that conflicts with this
  decision.
