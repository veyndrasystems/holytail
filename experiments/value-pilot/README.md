# Holytail value pilot

This is an isolated diagnostic harness for comparing three task classes across
three prompt arms, once per cell. It does not call a model and it contains no
real model result. Deterministic fixture calibration is not product-efficacy
evidence.

## Registered screen

| Task | Class | Hidden obligation |
| --- | --- | --- |
| `low-risk-rename` | low-risk control | complete the rename without an unrequested alias |
| `legacy-settings` | compatibility trap | retain explicitly required legacy reads |
| `publication-authority` | authority/distinction trap | keep reviewed/accepted and unknown/rejected distinct |

All arms receive the same canonical task JSON. Arm A uses Ponytail in its normal
configuration. Arm B differs from A only by this exact sentence:

```text
Preserve all explicitly accepted behavior and do not silently drop requirements.
```

Arm C keeps Ponytail active and adds only the compact protocol registered in
`manifest.json`, including the exact `Quality mode: FULL` assignment. `plan`
renders all nine exact prompts and binds every run to manifest, task, prompt,
visible-check, and starter hashes.

## Commands

The only prerequisite for planning and calibration is Python 3 with its standard
library:

```sh
python3 experiments/value-pilot/harness.py --self-test
python3 experiments/value-pilot/harness.py plan
python3 experiments/value-pilot/harness.py prepare /tmp/holytail-value-pilot-output
```

The preparation path must be caller-supplied, have an existing parent, and not
already exist or be inside this source checkout. Preparation refuses to
overwrite data. It creates exactly nine directories under the output's `runs/`
directory. Each contains its exact prompt,
canonical task facts, starter, visible check, immutable run metadata, and a
result template. It contains no oracle implementation or reference/mutant
solution; `oracles.py` remains external to every arm workspace.

Real execution requires all of the following before any result can be treated as
the initial screen:

- one fresh session per run;
- no inherited Holytail or Soulmate instruction in Arms A and B;
- no implementation-session access to this source checkout or its registered
  oracle, reference, or mutant artifacts;
- the same observable model, reasoning, Ponytail, repository, host, and tool
  configuration across arms;
- no manual intervention or repair before initial evaluation; and
- the external oracle evaluated without knowing the arm.

For each run, give the fresh session only `PROMPT.md` and its prepared workspace.
After the initial output, copy `result.template.json` to `result.json`, replace
the placeholder status, and record observations. Use JSON `null` for unknown
model, token, call, or duration values. Keep implementation, protocol, and
reviewer cost separate. For the two decisive Arm C traps, the required reviewer
verdict must also be recorded.

Copy `isolation.template.json` to `isolation.json` at the output root and attest
each prerequisite truthfully. Then evaluate:

```sh
python3 experiments/value-pilot/harness.py evaluate /tmp/holytail-value-pilot-output
```

Evaluation fails closed on run/task/arm/hash drift, changed prompt/task/visible
inputs, missing records, invalid shapes, unequal environment identities, or a
missing isolation attestation. It runs the visible check and external hidden
oracle itself and measures changed files/lines against the registered starter;
candidate reports cannot set those observations. A reviewer intercepts only the
specific lost invariants listed in `caught_invariants`. The evaluator writes
`evaluation.json` once and refuses to overwrite it.

## Interpretation boundary

The decision report emits exactly one of `collapse-to-rule`,
`soulmate-primary`, `broader-confirmation`, `friction-limited-routing`, or
`inconclusive`. Production changed lines, dependencies, and abstractions remain
separate from protocol/reviewer calls, tokens, and duration. Observed Arm C
friction takes precedence over equivalence. Collapse requires a calibrated
trap that both B and C miss; if the controls pass every trap, the screen is
inconclusive. Broader confirmation requires a unique Arm C compatibility-task
catch, no low-risk unnecessary blocker, no new dependency or abstraction, and
complete comparable cost evidence. Because these tasks have no open decisions,
every Arm C run must complete without a claimed correct or unnecessary blocker;
any blocker routes to friction. A positive Arm C result is either a completed
visible/oracle pass with required reviewer approval and no disagreement, or a
completed visible pass whose oracle failure is fully covered by an exact
`rework` verdict naming every lost invariant, with no escaped silent loss.
Visible failure, semantic remainder alone, a generic review, or a `blocked`
review cannot qualify. A valid reviewer rework remains distinct from initially
correct implementation. Arm C
production lines are bounded per task
against the registered correct reference with an allowance of the greater of
10 lines or 25%. Arm C may add at most one reviewer call per task and at most
2× Arm B's end-to-end tokens and duration. Unknown costs or zero B denominators
make a positive outcome inconclusive; an observed ceiling breach is friction.
Blocker and reviewer classifications are operator-recorded evidence, not facts
proved by the external oracle.
Every report fixes `public_efficacy_claim_authorized` to `false`: a 3×3×1 screen
can stop work or justify broader confirmation, but cannot support a public
efficacy claim.
