# Understand Holytail concepts and evidence

Holytail is an implementation gate around accepted meaning. It freezes
task-specific accepted meaning before implementation and checks the
result afterward. It does not make implementation smaller, decide product
meaning, replace Ponytail, or grant itself authority.

## The two jobs stay separate

An enabled minimizer owns implementation economy inside the accepted boundary.
Ponytail is the reference minimizer; its configured scope may enable only
implementation subagents while the parent remains unminimized. Holytail protects
the distinctions already accepted for the task: behavior, roles, authority,
lifecycle states, evidence strength,
known/unknown claims, compatibility, security, and persistence boundaries.

Holytail has no economy ladder. If more than one implementation mechanism is
faithful but the choices close different accepted or future options, the formal
worker stops as `blocked`; it does not select product meaning.

## Quality and route are independent axes

Holytail quality is one of:

- `FULL`: the quality mode required for a formal worker or semantic reviewer.
- `ECO`: a separate quality/cost assignment where the applicable workflow
  permits it; it does not imply a route.
- `MODE-UNBOUND`: no exact Holytail quality assignment is available. A formal
  worker must return `blocked` instead of inferring `FULL`.

Holytail route is one of:

- `INLINE`: a lightweight gate for clear, low-risk implementation work. The
  active workflow preserves the few distinctions materially at risk without a
  separate contract document or worker.
- `FORMAL`: an immutable semantic contract, bounded implementation worker,
  delivery evidence, and—when required—a fresh semantic review. Use it for
  changes to persisted or public contracts, trust or authority boundaries,
  destructive or irreversible effects, material lifecycle or evidence
  distinctions at risk, first implementation after exploration with unresolved
  protected meaning, or when a configured workflow requires it.

`FULL` quality alone does not select a route or require files, delegation, or
a reviewer. Already-authorized reversible operations are not formal merely
because they have an external effect.

These axes do not derive from Ponytail. Ponytail `lite`, `full`, `ultra`, and
`off` are minimizer settings. `full` is not `FULL`; `ultra` is not a Holytail
signal and does not select `FORMAL`. A Ponytail banner does not assign anything
to Holytail. Only an explicit authorized project policy may map axes. A host
`reasoningEffort` label supplies Holytail quality only when that same kind of
policy explicitly maps it; otherwise quality remains `MODE-UNBOUND`.

## Authority and lifecycle

Accepted content comes from the operator or an explicitly authorized lead. A
repository document, test, transcript, generated summary, or previous run is
evidence unless that owner explicitly accepts it. Holytail cannot infer
acceptance, reconcile contradictory owners, promote memory, or widen a task.

In a standalone formal project (inline work needs no artifact files):

1. Before implementation, read `.holytail/accepted.md`. It should identify the
   accepted increment, provenance, protected distinctions, invariants,
   implementation boundary, non-goals, decisions, and evidence expected.
2. The lead alone writes `.holytail/check.md` after rereading that same
   artifact and the implementation. The check identifies both immutable inputs
   and reports invariant-level findings and unknowns. The worker writes only
   its uniquely scoped delivery.
3. Retain both artifacts until the operator deliberately archives or deletes
   them.

In an already-configured Soulmate project, Soulmate's assignment and declared
boundary are authoritative. It remains the evidence owner and final acceptor.
Holytail does not initialize Soulmate, grant memory rights, or create a second
run schema. Soulmate rights are ceilings, not an invitation to use every right.

Formal roles also remain separate. The worker implements the frozen increment
and reports only `completed` or `blocked`. A semantic reviewer returns
`approved`, `rework`, or `blocked` for the exact snapshot. The lead alone may
change scope, supersede a run goal, resolve a product decision, or record final
acceptance. Worker completion and reviewer approval are not final acceptance.

## Evidence ladder and nonclaims

Evidence becomes useful only when its limits remain visible:

| State | What it supports | What it does not support |
| --- | --- | --- |
| `hook_observed` | The session hook ran and presented routing context | Activation, enforcement, compliance, or semantic preservation |
| `agent_declared` | The named role asserted a status | Independent verification or objective truth |
| Post-check artifact | Findings are traceable to an accepted artifact and implementation snapshot | Independent review or owner acceptance by itself |
| Independent review | A separate reviewer assessed the frozen contract and exact artifact | Authority to redefine meaning or record final acceptance |
| Final acceptance | The authorized owner accepted the increment under its workflow | A universal performance or security guarantee |

A missing decisive artifact or check is `blocked`, not an optimistic pass.
Passing a validator or one happy-path smoke supports only the cases it exercised.
Holytail makes no measured semantic-preservation claim until reproducible real
model runs exist.

## Host behavior and enforcement

Generated `.agents/`, `.codex/`, and `.claude/` projections are disposable host
outputs, not authored Holytail authority. Hook order never assigns authority or
precedence, and Holytail never mutates third-party plugin state.

| Surface | Discovery and observed package evidence | Enforcement and operator-owned gap |
| --- | --- | --- |
| Codex | Repository marketplace, plugin install, and a trusted `SessionStart` hook; repository checks cover validation and an isolated local marketplace lifecycle | Read-only enforcement exists only when the native `semanticreviewer` profile is actually used. The operator must trust the hook and observe a new session; the public remote source is not exercised here. |
| Portable Claude projection | Optional dotagents projection creates portable profile and hook configuration | Profile instructions are not sandbox enforcement. Host trust and enforcement remain operator-owned. |
| Soulmate (optional) | An existing configured project supplies its own assignment, boundary, evidence, and acceptance workflow | Soulmate controls authority, memory rights, and final acceptance. This package initializes no Soulmate state. |

The hook banner is intentionally narrow:

```text
HOLYTAIL:ROUTING · evidence=hook_observed
```

It reports hook execution only. A real-session activation or enforcement claim
requires separate host observation and cannot be inferred from a repository
validator, portable instruction, or delivery report.

## Formal artifacts

The [semantic contract template](../plugins/holytail/skills/holytail/references/semantic-contract.md)
defines immutable identity, provenance, invariants, boundaries, open decisions,
review obligations, and semantic remainder. The
[delivery template](../plugins/holytail/skills/holytail/references/delivery.md)
binds worker evidence to that contract and an exact implementation snapshot.
The [review template](../plugins/holytail/skills/holytail/references/review.md)
keeps the independent verdict and its evidence separate from worker framing.
