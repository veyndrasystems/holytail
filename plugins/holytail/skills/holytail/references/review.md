# Semantic equivalence review

Use a fresh reviewer only when independent review can materially change
acceptance or the configured workflow requires it. The reviewer must not share
the implementation context or write authority.

## Immutable inputs

```text
Reviewer run/context ID:
Reviewer identity/profile SHA-256:
Contract path@revision:
Contract SHA-256:
Implementation base revision:
Reviewed commit/tree or diff SHA-256:
Working tree dirty state:
Delivery/run ID and SHA-256:
Test evidence identities:
```

Bind all inputs to the same snapshot. If any required identity is missing,
mutable, contradictory, or changed during review, return `blocked`. Worker
delivery is secondary evidence; begin from the contract and artifact.

## Verdict

Use exactly one:

- `approved`: every blocking invariant in the accepted increment is represented
  and supported by decisive evidence
- `rework`: meaning is frozen, but implementation or evidence can be corrected
  without changing it
- `blocked`: an immutable input, decisive evidence, or authorized decision is
  missing, contradictory, or stale

A meaning change requires the lead or decision owner to supersede the goal; it
is not rework. A missing decision is a `blocked` detail, not a separate reviewer
verdict. Reviewer approval remains role-scoped evidence, not final acceptance.

## Traceability

| Contract item | Implemented? | Independently exercised? | Finding and exact evidence |
|---|---:|---:|---|
| | | | |

## Review questions

- Did the problem or accepted meaning change?
- Were protected distinctions and negative requirements preserved?
- Was an open decision selected silently?
- Did role, authority, memory, file, process, or content authority widen?
- Are raw references reachable and unknowns still explicit?
- Are public behavior, persisted formats, migration, paths, permissions,
  deployment assumptions, rollback, and unattended execution consistent?
- Does each decisive test exercise the claimed invariant?

## Semantic remainder assessment

Confirm each remainder item has a source, owner, blocking flag, status, reason,
and trigger. Approval is impossible if a blocking accepted invariant was
deferred or accepted meaning moved without its decision owner.

## Required rework or blocked detail

Name the failed invariant, exact evidence gap, affected immutable source, and
smallest observable correction or authorized decision. Include residual
uncertainty and the smallest decisive next check.
