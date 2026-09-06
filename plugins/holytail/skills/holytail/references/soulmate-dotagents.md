# Soulmate and dotagents integration

Holytail's authored content, dotagents deployment, and Soulmate authority are
separate planes. Normal Codex sessions must still work without Soulmate. The
minimizer, when enabled in the implementation context, operates between the
accepted-meaning check and the post-implementation check. Installation or a
routing hook does not establish minimizer activation.

## 1. Deploy with dotagents

Merge the repository's `[[plugins]]` and `[[subagents]]` entries into the
consumer `agents.toml`; do not replace existing agents or trust rules. Run
`dotagents install`, `sync`, `doctor --fix`, and then `doctor` in the intended
scope. `doctor --fix` repairs consumer state such as missing generated-file
ignore entries, so review its diff. For the repository's SSH source, a
restrictive project trust policy must include
`git_domains = ["github.com/veyndrasystems/holytail"]`; append the value rather
than replacing existing trust entries. The consumer manifest is desired state
and is not imported transitively from the plugin.

dotagents projects the portable agents to `.agents/agents/`, Codex profiles to
`.codex/agents/`, and Claude profiles to `.claude/agents/`. Those files are
disposable host projections. `dotagents sync` verifies and repairs projection
drift. Soulmate's `doctor` does not replace this check: it does not validate the
consumer manifest or dotagents projection integrity.

## 2. Import canonical Soulmate profiles deliberately

For an already initialized Soulmate project, review and import the clean
portable profiles bundled with the installed plugin. Do not import the generated
SemanticReviewer transport wrapper from `.agents/agents/`; that projection also
contains native-host metadata.

```sh
soulmate profile import holytail .agents/plugins/holytail/profiles/holytail.md \
  --purpose "Implement one frozen semantic increment without redefining meaning" \
  --config soulmate.json

soulmate profile import semanticreviewer .agents/plugins/holytail/profiles/semanticreviewer.md \
  --purpose "Review one frozen increment for silent meaning loss" \
  --config soulmate.json
```

Import copies profiles to `soulmate/agents/` and adds agents with empty rights.
It does not grant execution authority. Review the generated config diff, then
add only project-specific `observe`, `write`, `commands`, and `skills` rights.
Keep every memory read, write, review, promotion, rejection, revocation,
expiration, and forgetting right empty unless the project separately justifies
it.

For `holytail`, grant only the files and commands needed by the accepted
increment. For `semanticreviewer`, keep `write: []`. Codex enforces
`sandbox_mode = "read-only"` only when the native `.codex/agents` profile is
actually used; the string in a portable profile is not enforcement. When
running a reviewer through `soulmate away start`, also pass
`--sandbox-mode read-only`.

The default and clearest assignment is for the lead to put `Quality mode: FULL`
in every formal run goal; that direct assignment is sufficient. If the project
instead wants a host/model/reasoning label to supply the mode automatically, its
authorized policy must define the mapping explicitly—for example, Codex
`reasoningEffort=ultra` to team quality mode `FULL`. An effort label alone does
not authorize that inference. The resulting status line remains
`agent_declared`, not proof of runtime enforcement.

## 3. Add workflows, not a new schema

Add either or both entries under the existing `workflows` object:

```json
{
  "holytail": {
    "advisers": [],
    "workers": ["holytail"],
    "reviewers": []
  },
  "holytail_reviewed": {
    "advisers": [],
    "workers": ["holytail"],
    "reviewers": ["semanticreviewer"]
  }
}
```

The configured orchestration lead remains the contract compiler, scope owner,
and final acceptor. Do not create a second `Sol` role merely for Holytail.

Before `run start`, put the compact accepted goal, explicit quality mode, and
boundary in the run assignment. Upstream plans, transcripts, memory, and
handoff artifacts are evidence only; they cannot widen that goal. Use
`holytail_reviewed` when a deterministic formal trigger applies or independent
review is required. For example:

```sh
soulmate run start holytail_reviewed \
  --goal "Quality mode: FULL. Implement the frozen accepted increment only." \
  --boundary soulmate/boundaries/holytail.json \
  --ledger .soulmate/runs/holytail.jsonl \
  --config soulmate.json
```

## 4. Keep outcomes and evidence honest

- worker: `completed | blocked`
- reviewer: `approved | rework | blocked`
- lead: scope changes, supersession, rejection, and final acceptance

A missing product decision is a `blocked` detail. In a current Soulmate
workflow, a worker
or reviewer `blocked` submission immediately terminates that run; it is not
automatically routed into a lead stage. The lead or operator inspects the sealed
artifact, obtains the authorized decision, and explicitly creates a successor,
for example by inspecting the predecessor first:

```sh
soulmate run inspect .soulmate/runs/holytail.jsonl \
  --config soulmate.json
```

Then supersede it with a new immutable assignment:

```sh
soulmate run supersede .soulmate/runs/holytail.jsonl \
  --workflow holytail_reviewed \
  --goal "Quality mode: FULL. Restate the bounded successor goal." \
  --boundary soulmate/boundaries/holytail-successor.json \
  --ledger .soulmate/runs/holytail-successor.jsonl \
  --config soulmate.json
```

Reviewer `rework`, by contrast, is the automatic path back to a new worker
attempt. If accepted meaning changes, use explicit supersession rather than
calling it reviewer rework.

If the session banner was actually observed, a harness manifest may record a
Holytail skill entry at `hook_observed`, for example:

```json
{
  "kind": "skill",
  "name": "holytail:holytail",
  "evidence": "hook_observed"
}
```

Use `presented` when only instructions were supplied and `agent_declared` for
route/status lines. Never claim `independently_verified` without a separate
verifier bound to the artifact hash. Soulmate records these distinctions; the
Holytail hook does not mutate receipts, ledgers, memory, or project config.
