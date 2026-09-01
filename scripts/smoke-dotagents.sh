#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
dotagents_version="${DOTAGENTS_VERSION:-3.0.1}"
codex_version="${CODEX_VERSION:-0.152.1}"
smoke_root="$(mktemp -d)"
consumer_root="${smoke_root}/consumer"

cleanup() {
  rm -rf -- "${smoke_root}"
}
trap cleanup EXIT

mkdir -p "${consumer_root}/vendor/holytail"
cp -R "${repo_root}/plugins" "${consumer_root}/vendor/holytail/plugins"
cp -R "${repo_root}/agents" "${consumer_root}/vendor/holytail/agents"
cp "${repo_root}/tests/fixtures/consumer/agents.toml" "${consumer_root}/agents.toml"
cp "${repo_root}/tests/fixtures/consumer/.gitignore" "${consumer_root}/.gitignore"

dotagents=(npx --yes "@sentry/dotagents@${dotagents_version}" --project)
(
  cd "${consumer_root}"
  "${dotagents[@]}" install
  "${dotagents[@]}" sync
  "${dotagents[@]}" doctor --fix
  "${dotagents[@]}" doctor
)

test -f "${consumer_root}/.agents/plugins/holytail/plugin.json"
test -f "${consumer_root}/.agents/plugins/holytail/hooks/hooks.json"
test -f "${consumer_root}/.agents/plugins/holytail/.claude-plugin/plugin.json"
test -f "${consumer_root}/.agents/plugins/holytail/.codex-plugin/plugin.json"
test -f "${consumer_root}/.agents/plugins/holytail/skills/holytail/SKILL.md"
test -f "${consumer_root}/.agents/plugins/holytail/profiles/holytail.md"
test -f "${consumer_root}/.agents/plugins/holytail/profiles/semanticreviewer.md"
test -f "${consumer_root}/.agents/agents/holytail.md"
test -f "${consumer_root}/.agents/agents/semanticreviewer.md"
test -f "${consumer_root}/.codex/agents/holytail.toml"
test -f "${consumer_root}/.codex/agents/semanticreviewer.toml"
test -f "${consumer_root}/.claude/agents/holytail.md"
test -f "${consumer_root}/.claude/agents/semanticreviewer.md"
test -f "${consumer_root}/.agents/plugins/marketplace.json"

grep -Fq 'sandbox_mode = "read-only"' \
  "${consumer_root}/.codex/agents/semanticreviewer.toml"
grep -Fq 'SemanticReviewer :FULL · REVIEW · evidence=agent_declared' \
  "${consumer_root}/.claude/agents/semanticreviewer.md"
grep -Fq 'profile text is' \
  "${consumer_root}/.agents/plugins/holytail/profiles/semanticreviewer.md"
if grep -Fq 'developer_instructions =' \
  "${consumer_root}/.agents/plugins/holytail/profiles/semanticreviewer.md"; then
  printf '%s\n' "clean Soulmate reviewer contains native transport metadata" >&2
  exit 1
fi
grep -Fq 'HOLYTAIL:ROUTING · evidence=hook_observed' \
  "${consumer_root}/.agents/plugins/holytail/hooks/holytail-routing.cjs"
grep -Fq '"hooks": "./hooks/hooks.json"' \
  "${consumer_root}/.agents/plugins/holytail/.claude-plugin/plugin.json"

if [[ "${HOLYTAIL_CODEX_SMOKE:-1}" == "1" ]]; then
  export CODEX_HOME="${smoke_root}/codex-home"
  mkdir -p "${CODEX_HOME}"
  codex=(npx --yes "@openai/codex@${codex_version}" plugin)
  (
    cd "${consumer_root}"
    "${codex[@]}" marketplace add . --json
    available_json="$("${codex[@]}" list --marketplace dotagents-local --available --json)"
    printf '%s' "${available_json}" | python3 -c \
      'import json,sys; data=json.load(sys.stdin); assert any(item["name"] == "holytail" for item in data["available"])'
    install_json="$("${codex[@]}" add holytail@dotagents-local --json)"
    installed_path="$(printf '%s' "${install_json}" | python3 -c \
      'import json,sys; print(json.load(sys.stdin)["installedPath"])')"
    test -f "${installed_path}/hooks/hooks.json"
    hook_json="$(printf '%s' '{"hook_event_name":"SessionStart","session_id":"smoke"}' \
      | CLAUDE_PLUGIN_ROOT="${installed_path}" \
        node "${installed_path}/hooks/holytail-routing.cjs")"
    printf '%s' "${hook_json}" | python3 -c \
      'import json,sys; data=json.load(sys.stdin); assert data["systemMessage"] == "HOLYTAIL:ROUTING · evidence=hook_observed"; assert data["hookSpecificOutput"]["hookEventName"] == "SessionStart"; assert data["hookSpecificOutput"]["additionalContext"]'
    list_json="$("${codex[@]}" list --json)"
    printf '%s' "${list_json}" | python3 -c \
      'import json,sys; data=json.load(sys.stdin); assert any(item["name"] == "holytail" and item["enabled"] for item in data["installed"])'
  )
fi

printf '%s\n' "Holytail dotagents smoke test: OK"
