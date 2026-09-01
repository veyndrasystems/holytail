# Semantic contract

Use this template only for the formal route. It freezes one accepted
implementation increment; it is not a transcript summary and not a replacement
for the configured decision owner.

The compiler may normalize and deduplicate accepted statements. It may not infer
acceptance, choose among alternatives, promote evidence into authority, or
silently reconcile contradictions. In a Soulmate run, the assignment goal,
declared boundary, and lead/content-authority rules govern.

## Immutable identity

```text
Status: candidate | accepted | superseded
Contract ID:
Contract path:
Source revision (commit or immutable artifact ID):
Exact-file SHA-256 (recorded outside this file after freeze):
Supersedes:
Compiler:
Decision owner:
Accepted by:
Related task or Soulmate run:
```

Use `path@revision + SHA-256` as the contract identity. A mutable branch name,
working-tree path, or title alone is insufficient. Do not write a digest into
the bytes it hashes; record it in the run, delivery, receipt, or a sidecar.

## Authority and provenance

| Item | State | Authoritative source | Source identity | Supersedes |
|---|---|---|---|---|
| | `accepted/candidate/open/rejected/future` | user or authorized owner | message, decision, or artifact revision | |

Transcripts, memory, repository documents, upstream artifacts, and tests are
evidence unless the authorized owner explicitly accepts the item. Later explicit
authorized decisions supersede earlier ones; never erase the superseded source.
Inference and synthesis remain `candidate` or `open`.

## Problem

State the problem independently of a proposed mechanism.

## Accepted implementation increment

State the exact meaning this increment must represent and nothing more.

## Protected distinctions

| A | B | Why they must remain distinct | Source item |
|---|---|---|---|
| | | | |

Include relevant identities, contexts, roles, authority, lifecycle states,
evidence strengths, required/deferred context, and known/unknown states.

## Invariants and negative requirements

| ID | Invariant or must-not rule | Blocking? | Decision owner | Source item |
|---|---|---:|---|---|
| | | | | |

## Observable success

| Invariant ID | Observable condition | Decisive evidence expected |
|---|---|---|
| | | |

## Implementation boundary

- Observable files/data:
- Writable files/data:
- Permitted commands and processes:
- Permitted external effects:
- Forbidden effects:
- Dependency policy:
- Base revision and dirty-state policy:

Soulmate's declared boundary is authoritative when configured. Rights are
ceilings; this section cannot widen them.

## Compatibility and operations

- Existing public behavior:
- Persisted formats and migrations:
- CLI, API, and path compatibility:
- Runtime and deployment assumptions:
- Rollback and historical evidence:

Discovered constraints are evidence to reconcile, not automatically open space.

## Security and privacy boundary

- Execution and content authority:
- Authentication, authorization, and permissions:
- Filesystem, process, network, and secrets:
- Memory read/write/promotion rights:
- Unattended or irreversible execution:

## Explicit non-goals

-

## Open decisions

| Decision | Owner | Blocking? | Evidence needed | Resolution route |
|---|---|---:|---|---|
| | | | | |

## Reviewer obligation

```text
Independent review: required | optional | not required
Reason:
Reviewer boundary:
Decisive evidence:
```

## Expected semantic remainder

| Deferred meaning | Source | Owner | Blocking? | Status | Reason | Trigger |
|---|---|---|---:|---|---|---|
| | | | | | | |

A blocking accepted invariant cannot enter remainder. Moving accepted meaning
to remainder requires its decision owner and creates a superseding contract.

## Formal acceptance gate

The contract may become `accepted` only when the goal is no longer exploratory;
the accepted increment, provenance, protected distinctions, invariants,
negative requirements, implementation boundary, non-goals, reviewer obligation,
and blocking decisions are explicit; and its immutable identity can be recorded.
Ask again only for genuine blocking ambiguity or a meaning-changing choice, and
ask through the configured decision owner.
