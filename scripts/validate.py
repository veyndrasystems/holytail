#!/usr/bin/env python3

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "holytail"
SKILL = PLUGIN / "skills" / "holytail"
EXPECTED_AUTHOR = {
    "name": "Veyndra Systems",
    "email": "veyndra-operator@users.noreply.github.com",
    "url": "https://github.com/veyndrasystems",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def require_files() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "agents.toml",
        ROOT / "agents" / "holytail.md",
        ROOT / "agents" / "semanticreviewer.toml",
        PLUGIN / "plugin.json",
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / "hooks" / "hooks.json",
        PLUGIN / "hooks" / "holytail-routing.cjs",
        PLUGIN / "profiles" / "holytail.md",
        PLUGIN / "profiles" / "semanticreviewer.md",
        SKILL / "SKILL.md",
        SKILL / "agents" / "openai.yaml",
        SKILL / "references" / "semantic-contract.md",
        SKILL / "references" / "delivery.md",
        SKILL / "references" / "review.md",
        SKILL / "references" / "routing-context.md",
        SKILL / "references" / "soulmate-dotagents.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")

    stale = [ROOT / "SKILL.md", ROOT / "skills", ROOT / "references", ROOT / "fragments"]
    present = [str(path.relative_to(ROOT)) for path in stale if path.exists()]
    if present:
        fail(f"stale pre-package paths remain: {', '.join(present)}")


def validate_manifests() -> None:
    portable = load_json(PLUGIN / "plugin.json")
    native = load_json(PLUGIN / ".codex-plugin" / "plugin.json")
    if not isinstance(portable, dict) or not isinstance(native, dict):
        fail("plugin manifests must be JSON objects")

    if "$schema" in portable:
        fail("dotagents 3.0.1 compatibility manifest must remain generalized legacy format")
    for manifest in (portable, native):
        if manifest.get("name") != "holytail":
            fail("plugin name mismatch")
        if manifest.get("version") != "0.1.0":
            fail("plugin version mismatch")
        if manifest.get("author") != EXPECTED_AUTHOR:
            fail("plugin author metadata mismatch")

    if native.get("skills") != "./skills/":
        fail("Codex plugin must declare ./skills/")
    if "hooks" in native:
        fail("use Codex default hooks/hooks.json discovery; omit manifest hooks")
    if portable.get("skills") != "./skills" or portable.get("hooks") != "./hooks/hooks.json":
        fail("dotagents compatibility manifest must declare portable skills and hooks")
    interface = native.get("interface")
    if not isinstance(interface, dict):
        fail("Codex plugin interface is required")
    for field in ("displayName", "shortDescription", "developerName", "category", "capabilities"):
        if not interface.get(field):
            fail(f"Codex plugin interface.{field} is required")

    deployment = load_toml(ROOT / "agents.toml")
    if deployment.get("version") != 1:
        fail("agents.toml version must be 1")
    if set(deployment.get("agents", [])) != {"claude", "codex"}:
        fail("agents.toml must target Claude and Codex")
    plugins = deployment.get("plugins", [])
    if len(plugins) != 1 or plugins[0].get("path") != "plugins/holytail":
        fail("agents.toml must deploy the nested Holytail plugin")
    subagents = {item.get("name"): item for item in deployment.get("subagents", [])}
    expected_paths = {
        "holytail": "agents/holytail.md",
        "semanticreviewer": "agents/semanticreviewer.toml",
    }
    if {name: subagents.get(name, {}).get("path") for name in expected_paths} != expected_paths:
        fail("agents.toml subagent paths do not match authored sources")
    declarations = [*plugins, *deployment.get("subagents", [])]
    if any(item.get("ref") != "9f9c9cc37c6b2c678733bc7296b59724bc1de390" for item in declarations):
        fail("all deployment declarations must pin the packaged source commit")


def validate_skill() -> None:
    source = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", source, flags=re.DOTALL)
    if not match:
        fail("SKILL.md must begin with YAML frontmatter")
    frontmatter = match.group(1)
    if not re.search(r"^name:\s*holytail\s*$", frontmatter, flags=re.MULTILINE):
        fail("SKILL.md frontmatter name must be holytail")
    if not re.search(r"^description:\s*\S", frontmatter, flags=re.MULTILINE):
        fail("SKILL.md frontmatter description is required")

    required_phrases = [
        "Holytail :<FULL|ECO|MODE-UNBOUND> · <INLINE|FORMAL> · evidence=agent_declared",
        "The contract compiler is the user or an explicitly authorized lead",
        "A configured Soulmate workflow overrides this heuristic",
        "Missing decisive evidence is `blocked`, not approval",
    ]
    for phrase in required_phrases:
        if phrase not in source:
            fail(f"SKILL.md is missing contract phrase: {phrase}")

    openai_yaml = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    short = re.search(r'^\s*short_description:\s*"([^"]+)"\s*$', openai_yaml, re.MULTILINE)
    if not short or not 25 <= len(short.group(1)) <= 64:
        fail("openai.yaml short_description must be 25-64 characters")
    if "$holytail" not in openai_yaml:
        fail("openai.yaml default prompt must explicitly invoke $holytail")


def validate_reviewer() -> None:
    reviewer = load_toml(ROOT / "agents" / "semanticreviewer.toml")
    if reviewer.get("name") != "semanticreviewer":
        fail("reviewer name mismatch")
    if reviewer.get("sandbox_mode") != "read-only":
        fail("Codex semantic reviewer must enforce read-only sandbox mode")
    instructions = reviewer.get("developer_instructions", "")
    for phrase in (
        "SemanticReviewer :FULL · REVIEW · evidence=agent_declared",
        "return `blocked`",
        "Do not edit files",
    ):
        if phrase not in instructions:
            fail(f"semantic reviewer instructions missing: {phrase}")

    portable = (PLUGIN / "profiles" / "semanticreviewer.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "SemanticReviewer :FULL · REVIEW · evidence=agent_declared",
        "profile text is\nnot sandbox enforcement",
        "return `blocked`",
        "Do not edit files",
    ):
        if phrase not in portable:
            fail(f"portable semantic reviewer is missing: {phrase}")
    if "sandbox_mode =" in portable or "developer_instructions =" in portable:
        fail("portable semantic reviewer must not contain native TOML transport metadata")

    shared_marker = "Begin every response with:"
    if shared_marker not in instructions or shared_marker not in portable:
        fail("semantic reviewer shared instruction marker is missing")
    native_tail = instructions.split(shared_marker, 1)[1]
    portable_tail = portable.split(shared_marker, 1)[1]
    if native_tail != portable_tail:
        fail("portable and native semantic reviewer instructions have drifted")

    worker_source = (ROOT / "agents" / "holytail.md").read_bytes()
    worker_profile = (PLUGIN / "profiles" / "holytail.md").read_bytes()
    if worker_source != worker_profile:
        fail("portable Soulmate worker profile must match the authored worker")


def validate_markdown_links() -> None:
    markdown_files = [ROOT / "README.md", ROOT / "agents" / "holytail.md"]
    markdown_files.extend(PLUGIN.rglob("*.md"))
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    broken: list[str] = []
    for source in markdown_files:
        text = source.read_text(encoding="utf-8")
        for target in link_pattern.findall(text):
            if target.startswith(("http://", "https://", "#")):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (source.parent / clean).resolve().exists():
                broken.append(f"{source.relative_to(ROOT)} -> {target}")
    if broken:
        fail(f"broken relative Markdown links: {', '.join(broken)}")


def run_hook(event: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PLUGIN_ROOT"] = str(PLUGIN)
    return subprocess.run(
        ["node", str(PLUGIN / "hooks" / "holytail-routing.cjs")],
        input=json.dumps({"hook_event_name": event, "session_id": "validation"}),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def validate_hooks() -> None:
    hooks = load_json(PLUGIN / "hooks" / "hooks.json")
    if not isinstance(hooks, dict):
        fail("hooks.json must be an object")
    configured = hooks.get("hooks", {})
    if set(configured) != {"SessionStart"}:
        fail("hooks.json must configure SessionStart only")
    raw = json.dumps(hooks, ensure_ascii=False)
    if "${CLAUDE_PLUGIN_ROOT}/hooks/holytail-routing.cjs" not in raw:
        fail("shared hook command must resolve from CLAUDE_PLUGIN_ROOT")
    if '%CLAUDE_PLUGIN_ROOT%\\\\hooks\\\\holytail-routing.cjs' not in raw:
        fail("shared hook must provide a Windows command override")

    session = run_hook("SessionStart")
    if session.returncode != 0:
        fail(f"SessionStart hook failed: {session.stderr.strip()}")
    output = json.loads(session.stdout)
    if output.get("systemMessage") != "HOLYTAIL:ROUTING · evidence=hook_observed":
        fail("SessionStart hook banner mismatch")
    specific = output.get("hookSpecificOutput", {})
    if specific.get("hookEventName") != "SessionStart":
        fail("SessionStart hook event mismatch")
    context = specific.get("additionalContext", "")
    if "INLINE" not in context or "FORMAL" not in context or "Hook order is not authority" not in context:
        fail("SessionStart hook context is incomplete")

    subagent = run_hook("SubagentStart")
    if subagent.returncode != 0 or subagent.stdout:
        fail("routing hook must ignore SubagentStart to preserve dedicated profiles")

    unrelated = run_hook("PostToolUse")
    if unrelated.returncode != 0 or unrelated.stdout:
        fail("routing hook must ignore unrelated events")


def main() -> int:
    require_files()
    validate_manifests()
    validate_skill()
    validate_reviewer()
    validate_markdown_links()
    validate_hooks()
    print("Holytail package validation: OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"Holytail package validation: FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
