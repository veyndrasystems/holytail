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
- Implementation diff SHA-256: `24af966ad4256b7633c4476749a591186fda3bc88da790e3592883bf71da2f2e`
- Digest formula: `git diff --binary 7c437f2cada0fa2dd5ac775e0f6183666577e1ef -- . ':(exclude).holytail/accepted.md' ':(exclude).holytail/check.md' | sha256sum`

## Invariant-level findings

| Invariant | Finding | Evidence |
|---|---|---|
| I1 | Holytail contains no minimization ladder or minimization behavior. | `scripts/validate.py` |
| I2 | Ponytail remains active and is not treated as conflicting state. | `README.md` |
| I3 | Ponytail labels do not assign Holytail axes. | `tests/test_validate.py` |
| I4 | Unassigned quality remains `MODE-UNBOUND`. | `agents/holytail.md` |
| I5 | `full` and `FULL` remain distinct values. | `tests/test_validate.py` |
| I6 | `ultra` is not a Holytail route, mode, or escalation trigger. | `tests/test_validate.py` |
| I7 | The accepted artifact is read before minimization in the standalone path. | `plugins/holytail/skills/holytail/SKILL.md` |
| I8 | The post-check is produced after implementation in the standalone path. | `.holytail/check.md` |
| I9 | The post-check identifies the accepted artifact and implementation snapshot. | `.holytail/check.md` |
| I10 | Soulmate remains optional authority and final acceptor when present. | `plugins/holytail/skills/holytail/SKILL.md` |
| I11 | No competing Soulmate run format is introduced. | `scripts/validate.py` |
| I12 | No third-party plugin state is mutated. | `scripts/validate.py` |
| I13 | Hook order does not imply authority or precedence. | `plugins/holytail/skills/holytail/references/routing-context.md` |
| I14 | Hook and status assertions are not reported as independent verification. | `scripts/validate.py` |
| I15 | No measured preservation claim is added without reproducible results. | `README.md` |
| I16 | Tracked public artifacts contain no local home paths, private identifiers, or restricted workflow notes. | `scripts/validate.py` |

## Evidence limits and semantic remainder

The checks cover the authored snapshot and focused negative mutations. They do
not establish real-session trust, runtime behavior, semantic preservation, or
independent review. Publishable benchmark results and release publication
remain outside this implementation snapshot and require maintainer action.
