# Holytail delivery

Use this structure for the formal worker. It is implementation evidence, not
reviewer approval, lead acceptance, or objective truth. The worker writes only
its uniquely scoped delivery at the assigned destination. The lead alone writes
`.holytail/check.md` for standalone formal work; workers do not write that check
or record final acceptance.

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

Bind the delivery to an immutable contract identity and implementation snapshot.
Do not use a mutable branch label. Disclose every uncommitted and untracked
file included in or excluded from the reviewed digest, including evidence files
that are excluded to avoid self-reference.

## Outcome

```text
Worker outcome: completed | blocked
Reason:
```

A missing product decision is a `blocked` detail. The worker does not return
final acceptance or invent another top-level outcome.

## Implemented boundary and responsibilities

- Changed files and responsibilities:
- Mechanism and failure behavior:
- Dependencies, compatibility, and migration:
- Authority, persistence, security, and rollback boundaries:

Describe only work inside the accepted boundary. Keep the active implementation
workflow's mechanism ownership explicit; this delivery does not assign an
implementation economy or replace a user's active tool.

## Semantic traceability

| Contract item | Invariant | Implementation location | Test or observable evidence |
|---|---|---|---|
| | | | |

## Contract deviations and rejected contract violations

List any deviation from the accepted contract with its owner and decision. If
there is no deviation, say so. Record rejected shortcuts only when they would
violate an accepted invariant or boundary, and name the meaning that would be
lost.

## Semantic remainder

| Deferred meaning | Source | Owner | Blocking? | Status | Reason/evidence needed | Trigger |
|---|---|---|---:|---|---|---|
| | | | | | | |

`completed` is impossible while a blocking accepted invariant is in remainder.
Moving accepted meaning to remainder requires its decision owner's authorization
and a superseding contract.

## Blockers and decision details

| Contract item | Missing decision or evidence | Authorized owner | Next authorized action |
|---|---|---|---|
| | | | |

## Tests and evidence

List exact commands, results, skipped checks, failures, unknowns, and evidence
limits. A passing command supports only the cases it observed. Keep hook
execution, agent assertion, independent verification, reviewer outcome, and
final acceptance as separate evidence states.

## Risk and compatibility notes

Cover authority, trust boundaries, privacy, persistence, migration, runtime and
host assumptions, rollback, external effects, and future options closed. State
whether any third-party or installed state changed.
