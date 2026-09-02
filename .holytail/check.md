# Holytail post-check

This artifact is implementation evidence, not independent review, final
acceptance, or objective truth.

## Snapshot binding

- Accepted artifact: `.holytail/accepted.md`
- Contract ID: `holytail-ponytail-layer-v1`
- Contract SHA-256: `672d29feb8245767b4ca87b89dad5a0c530931364a79c201672d9797f0de2149`
- Implementation base revision: `7c437f2cada0fa2dd5ac775e0f6183666577e1ef`
- Implementation snapshot: reproducible working-tree diff from the base,
  excluding this check artifact and the accepted artifact
- Implementation diff SHA-256: `b35f3b334ee2b1acd323add58b6eec1a0bcedf6a3d2b731347eb92eef1434747`
- Digest formula: `git diff --binary 7c437f2cada0fa2dd5ac775e0f6183666577e1ef -- . ':(exclude).holytail/accepted.md' ':(exclude).holytail/check.md' | sha256sum`

## Invariant-level findings

| Invariant | Finding | Evidence |
|---|---|---|
| I1 | Holytail contains no minimization ladder or minimization behavior. | Validator and source checks |
| I2 | Ponytail remains active and is not treated as conflicting state. | README and routing source |
| I3 | Ponytail labels do not assign Holytail axes. | Validator mutation checks |
| I4 | Unassigned quality remains `MODE-UNBOUND`. | Status-contract source checks |
| I5 | `full` and `FULL` remain distinct values. | Axis mutation checks |
| I6 | `ultra` is not a Holytail route, mode, or escalation trigger. | Axis mutation checks |
| I7 | The accepted artifact is read before minimization in the standalone path. | Skill and artifact checks |
| I8 | The post-check is produced after implementation in the standalone path. | This artifact and validator |
| I9 | The post-check identifies the accepted artifact and implementation snapshot. | Snapshot binding above |
| I10 | Soulmate remains optional authority and final acceptor when present. | Skill and profile checks |
| I11 | No competing Soulmate run format is introduced. | Source inspection |
| I12 | No third-party plugin state is mutated. | Repository diff scope |
| I13 | Hook order does not imply authority or precedence. | Status-contract checks |
| I14 | Hook and status assertions are not reported as independent verification. | Evidence wording checks |
| I15 | No measured preservation claim is added without reproducible results. | README and benchmark checks |
| I16 | Tracked public artifacts contain no local home paths, private identifiers, or restricted workflow notes. | Repository validator mutation checks and pre-publication scan |

## Evidence limits and semantic remainder

The checks cover the authored snapshot and focused negative mutations. They do
not establish real-session trust, runtime behavior, semantic preservation, or
independent review. Publishable benchmark results and release publication
remain outside this implementation snapshot and require maintainer action.
