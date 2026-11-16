# ADR NNNN — <Short, imperative title>

- **Status:** Proposed | Accepted | Rejected | Superseded by ADR-NNNN
- **Date:** YYYY-MM-DD
- **Decision owner:** <name or role>
- **Scope:** <module or layer this decision affects>
- **Related issue:** <full issue URL>
- **Supersedes:** <ADR-NNNN, or —>

---

## 1. Context

The situation, the constraints, and the problem that has to be solved. Write
this so that someone with no memory of the discussion can follow it. State
facts, not preferences.

## 2. Decision Drivers

What actually matters here, and how much. The weights are what make the
comparison in section 4 defensible instead of arbitrary.

| #   | Driver | Weight | Why it matters |
| --- | ------ | ------ | -------------- |
| D1  |        |        |                |

## 3. Options Considered

At least three, including the status quo where that is a real option.

### Option A — <name>

- **Strengths:**
- **Weaknesses:**
- **Official documentation:** <URL>

### Option B — <name>

...

## 4. Comparison

Score each option against each driver on a 1–5 scale, then multiply by the
weight. Show the arithmetic — a total with no visible working is not evidence.

| Criterion          | Weight | A   | B   | C   |
| ------------------ | ------ | --- | --- | --- |
|                    |        |     |     |     |
| **Weighted total** |        |     |     |     |

## 5. Decision

One explicit sentence stating what was chosen, followed by the concrete
architecture that follows from it. If the decision has parts, number them.

## 6. Consequences

### Positive

### Negative / Risks

### Mitigations

## 7. Rejected Options

Every option that lost, with the specific reason. "Not preferred" is not a
reason; name the criterion it failed.

| Option | Reason for rejection |
| ------ | -------------------- |

## 8. Proof of Concept / Validation

- **Branch:**
- **Scope of the PoC:**
- **Acceptance criteria:**
- **Evidence:** <test output, benchmark, link to CI run>

## 9. References

Official documentation for every option considered, plus any benchmark or
article that influenced the decision.

## 10. Review Trigger

The concrete conditions under which this decision is reopened. "If it stops
working" is not a trigger; "if write concurrency exceeds N" is.
