# Holytail delivery

Use this structure for the formal worker. It is implementation evidence, not
reviewer approval or lead acceptance.

## Immutable inputs and output

```text
Delivery/run ID:
Worker context ID:
Contract path@revision:
Contract SHA-256:
Implementation base revision:
Reviewed commit/tree or diff SHA-256:
Working tree dirty state:
```

Do not use a mutable branch label as the reviewed artifact identity. List
uncommitted and untracked material included or excluded from the digest.

## Outcome

```text
Worker outcome: completed | blocked
Reason:
```

A missing product decision is a `blocked` detail. The worker does not return
final acceptance or invent another top-level outcome.

## Minimal implementation

- Changed files and responsibilities:
- Mechanism and failure behavior:
- Dependencies, compatibility, and migration:
- Why this is the smallest faithful step:

## Semantic traceability

| Contract item | Invariant | Implementation location | Test or observable evidence |
|---|---|---|---|
| | | | |

## Simplifications applied

For each material simplification, record what was removed, why it carried no
accepted meaning, the preserving invariant, and observable evidence.

## Semantic remainder

| Deferred meaning | Source | Owner | Blocking? | Status | Reason/evidence needed | Trigger |
|---|---|---|---:|---|---|---|
| | | | | | | |

`completed` is impossible while a blocking accepted invariant is in remainder.
Moving accepted meaning here requires its decision owner's authorization and a
superseding contract.

## Rejected simplifications

For each, record the shortcut, why it was rejected, and the meaning it would
have lost.

## Blockers and decision details

| Contract item | Missing decision or evidence | Authorized owner | Smallest next action |
|---|---|---|---|
| | | | |

## Tests and evidence

List tests added and run, exact commands, results, skipped checks, failures,
unknowns, and evidence limits. A passing test supports only exercised cases.

## Risk and compatibility notes

Cover trust boundaries, authority, privacy, persistence, migration, runtime and
host assumptions, rollback, external effects, and future options closed.
