#!/usr/bin/env python3

from __future__ import annotations

import json
from hashlib import sha256
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "holytail"
SKILL = PLUGIN / "skills" / "holytail"
CATALOG = ROOT / ".agents" / "plugins" / "marketplace.json"
EXPECTED_DEPLOYMENT_REF = "93482adfb3f1c6b6fa97f2c2ad193e5899f6fa2c"
EXPECTED_AUTHOR = {
    "name": "Veyndra Systems",
    "email": "veyndra-operator@users.noreply.github.com",
    "url": "https://github.com/veyndrasystems",
}


MACHINE_LOCAL_HOME_PATTERNS = (
    ("unix-or-macos-home-path", re.compile(r"/(?:home|Users|root|var/root)/[^/\s]+(?:/|$)")),
    ("windows-user-profile-path", re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s]+(?:[\\/]|$)")),
)

INTERNAL_ROUTING_NOTE_PATTERNS = (
    (
        "delegation-or-assignment-logistics",
        re.compile(
            r"\bdelegat\w*\b[^\n.!?]{0,40}\bto\b|"
            r"\bassign(?:ed|ment)\b[^\n.!?]{0,80}\b(?:to|by)\b|"
            r"\b(?:delegat\w*|assign(?:ed|ment))\b[^\n.!?]{0,120}"
            r"\b(?:worker|agent|model|reviewer|logistic\w*|detail\w*|"
            r"instruction\w*|context\w*|route\w*)\b|"
            r"\b(?:worker|agent|model|reviewer)\b[^\n.!?]{0,120}"
            r"\b(?:delegat\w*|assign(?:ed|ment))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "internal-model-worker-routing",
        re.compile(
            r"\binternal\b[^\n.!?]{0,120}\b(?:model|worker|agent|reviewer)\b|"
            r"\b(?:model|worker|agent|reviewer)\b[^\n.!?]{0,120}\binternal\b",
            re.IGNORECASE,
        ),
    ),
    (
        "execution-routing-logistics",
        re.compile(
            r"\b(?:worker|agent|model|reviewer)\s+(?:run|routing|context|id)\b|"
            r"\b(?:run|routing|context|id)\s+(?:for\s+)?(?:worker|agent|model|reviewer)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "passive-routing-logistics",
        re.compile(
            r"\brout\w*\s+to\s+(?:(?:the|a)\s+)?(?:model|worker|agent|reviewer)\b|"
            r"\b(?:model|worker|agent|reviewer)\s+was\s+rout\w*\b",
            re.IGNORECASE,
        ),
    ),
)


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def assert_no_machine_local_home_paths(source: str, label: str = "public source") -> None:
    """Reject machine-local home paths without exposing matching content."""
    for pattern_class, pattern in MACHINE_LOCAL_HOME_PATTERNS:
        if pattern.search(source):
            fail(f"{label} contains disallowed public path class: {pattern_class}")


def assert_no_internal_routing_notes(source: str, label: str = "workflow artifact") -> None:
    """Reject explicit execution-routing logistics without exposing the note."""
    for pattern_class, pattern in INTERNAL_ROUTING_NOTE_PATTERNS:
        if pattern.search(source):
            fail(f"{label} contains disallowed public note class: {pattern_class}")


def validate_public_privacy() -> None:
    """Check text in tracked working-tree files before public publication."""
    try:
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            check=True,
            capture_output=True,
        ).stdout.split(b"\0")
    except (OSError, subprocess.CalledProcessError) as error:
        fail(f"could not enumerate tracked public files: {error}")

    for raw_path in tracked:
        if not raw_path:
            continue
        path = ROOT / os.fsdecode(raw_path)
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        assert_no_machine_local_home_paths(str(source), str(path.relative_to(ROOT)))


def require_files() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CHANGELOG.md",
        ROOT / ".holytail" / "accepted.md",
        ROOT / ".holytail" / "check.md",
        ROOT / "scripts" / "benchmark.py",
        CATALOG,
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
        PLUGIN / "assets" / "icon.svg",
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
        fail("dotagents compatibility manifest must remain generalized legacy format")
    for manifest in (portable, native):
        if manifest.get("name") != "holytail":
            fail("plugin name mismatch")
        if manifest.get("version") != "0.1.0":
            fail("plugin version mismatch")
        if manifest.get("author") != EXPECTED_AUTHOR:
            fail("plugin author metadata mismatch")
        if manifest.get("license") != "MIT":
            fail("plugin license must be MIT")

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
    for field in ("composerIcon", "logo", "logoDark"):
        if not isinstance(interface.get(field), str) or not (PLUGIN / interface[field].removeprefix("./")).is_file():
            fail(f"Codex plugin interface.{field} must point to a local asset")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts or not all(
        isinstance(prompt, str) and "$holytail:holytail" in prompt for prompt in prompts
    ):
        fail("Codex plugin default prompts must invoke $holytail:holytail")

    catalog = load_json(CATALOG)
    if not isinstance(catalog, dict) or catalog.get("name") != "holytail":
        fail("repo marketplace catalog name mismatch")
    if catalog.get("interface", {}).get("displayName") != "Holytail":
        fail("repo marketplace display name mismatch")
    entries = catalog.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        fail("repo marketplace must contain one plugin")
    entry = entries[0]
    if (entry.get("name"), entry.get("category")) != ("holytail", "Developer Tools"):
        fail("repo marketplace plugin metadata mismatch")
    if entry.get("source") != {"source": "local", "path": "./plugins/holytail"}:
        fail("repo marketplace source mismatch")
    if entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
        fail("repo marketplace policy mismatch")

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
    if any(item.get("ref") != EXPECTED_DEPLOYMENT_REF for item in declarations):
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
    if "$holytail:holytail" not in openai_yaml:
        fail("openai.yaml default prompt must explicitly invoke $holytail:holytail")


def check_axis_collision(source: str, label: str = "status-bearing source") -> None:
    """Check that Ponytail labels cannot be interpreted as Holytail axes."""
    normalized = " ".join(source.split())
    required = (
        "Ponytail `lite`, `full`, `ultra`, and `off`",
        "`full` is not `FULL`",
        "`ultra` is not a Holytail signal",
        "explicit authorized project policy",
        "MODE-UNBOUND",
        "reasoningEffort",
    )
    for phrase in required:
        if phrase not in normalized:
            fail(f"{label} is missing axis-contract phrase: {phrase}")
    if re.search(r"(?i)(disable|turn off|do not use).*Ponytail", source):
        fail(f"{label} tells users to disable Ponytail")
    if re.search(r"Ponytail[^.\n]*(assign|trigger)[^.\n]*Holytail", source, re.I):
        fail(f"{label} allows Ponytail to assign or trigger Holytail")
    level_to_axis = re.compile(
        r"`?(?:lite|full|ultra|off)`?\b"
        r"(?P<relation>[^.!?;]{0,220}?)"
        r"`?(?:FULL|ECO|INLINE|FORMAL)`?\b"
    )
    mapping_verb = re.compile(
        r"\b(?:assign(?:s|ed|ing)?|map(?:s|ped|ping)?|mean(?:s|t)?|"
        r"set(?:s|ting)?|select(?:s|ed|ing)?|suppl(?:y|ies|ied|ying)|"
        r"trigger(?:s|ed|ing)?|impl(?:y|ies|ied|ying)|becom(?:e|es|ing)?|"
        r"rout(?:e|es|ed|ing)?|escalat(?:e|es|ed|ing)?|"
        r"choose(?:s|n|ing)?|determin(?:e|es|ed|ing)?|"
        r"designat(?:e|es|ed|ing)?|force(?:s|d|ing)?|"
        r"configur(?:e|es|ed|ing)?|enabl(?:e|es|ed|ing)?|"
        r"activat(?:e|es|ed|ing)?|pick(?:s|ed|ing)?|is)\b",
        re.I,
    )
    def statement_context(start: int) -> str:
        tail = normalized[start:]
        end = re.search(r"[.!?;]", tail)
        return tail[:end.end() if end else len(tail)]

    def mapping_is_negated(relation: str) -> bool:
        verbs = list(mapping_verb.finditer(relation))
        if not verbs:
            return False
        nearest = verbs[-1]
        prefix = relation[:nearest.start()]
        suffix = relation[nearest.end():]
        if nearest.group(0).lower() == "is" and re.match(
            r"\s+(?:not|unrelated)\b", suffix, re.I
        ):
            return True
        clause = re.split(r"\b(?:and|but|however|yet)\b", prefix, flags=re.I)[-1]
        return bool(
            re.search(
                r"(?:does\s+not|do\s+not|did\s+not|cannot|can\s+not|can't|never)"
                r"(?:[\s,]+\w+){0,12}\s*$",
                clause.strip(),
                re.I,
            )
        )

    def positive_policy(statement: str) -> bool:
        lower = statement.lower()
        policy = "explicit authorized project policy"
        if policy not in lower:
            return False
        if re.search(
            r"\b(?:without|no|not|never|unless|absent|lack\w*)\b"
            r"[^.!?;]{0,80}\bexplicit authorized project policy\b",
            lower,
        ):
            return False
        return bool(
            re.search(
                r"\b(?:only\s+(?:under|with|if)|provided\s+that|when|if)\b"
                r"[^.!?;]{0,100}\bexplicit authorized project policy\b",
                lower,
            )
        )

    for match in level_to_axis.finditer(normalized):
        relation = match.group("relation")
        statement = statement_context(match.start())
        if (
            mapping_verb.search(relation)
            and not mapping_is_negated(relation)
            and not positive_policy(statement)
        ):
            fail(f"{label} contains a direct Ponytail-to-Holytail axis mapping")

    mixed_clause = re.compile(
        r"`?(?:lite|full|ultra|off)`?\b"
        r"(?P<first>[^.!?;]{0,220}?)"
        r"`?(?:FULL|ECO|INLINE|FORMAL)`?\b"
        r"(?P<later>[^.!?;]{0,220}?)"
        r"`?(?:FULL|ECO|INLINE|FORMAL)`?\b"
    )
    for match in mixed_clause.finditer(normalized):
        first = match.group("first")
        later = match.group("later")
        if (
            mapping_verb.search(first)
            and mapping_is_negated(first)
            and re.search(r"\b(?:and|but|however|yet)\b", later, re.I)
            and mapping_verb.search(later)
            and not mapping_is_negated(later)
            and not positive_policy(statement_context(match.start()))
        ):
            fail(f"{label} contains a mixed Ponytail-to-Holytail axis mapping")


def validate_status_contracts() -> None:
    sources = {
        "skill": (SKILL / "SKILL.md").read_text(encoding="utf-8"),
        "routing": (SKILL / "references" / "routing-context.md").read_text(encoding="utf-8"),
        "worker": (ROOT / "agents" / "holytail.md").read_text(encoding="utf-8"),
        "worker profile": (PLUGIN / "profiles" / "holytail.md").read_text(encoding="utf-8"),
        "reviewer": (ROOT / "agents" / "semanticreviewer.toml").read_text(encoding="utf-8"),
        "reviewer profile": (PLUGIN / "profiles" / "semanticreviewer.md").read_text(encoding="utf-8"),
    }
    for label, source in sources.items():
        check_axis_collision(source, label)
        for phrase in ("hook_observed", "agent_declared", "Hook order is not authority"):
            if phrase not in source:
                fail(f"{label} is missing evidence boundary: {phrase}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check_axis_collision(readme, "README")
    forbidden = (
        "Holytail includes its own economy ladder",
        "turn off that generic activation",
        "self-contained minimizer",
    )
    for phrase in forbidden:
        if phrase.lower() in readme.lower() or any(phrase.lower() in text.lower() for text in sources.values()):
            fail(f"forbidden Holytail economy language remains: {phrase}")
    for phrase in ("Ponytail makes the agent write less.", "Holytail checks that it did not drop"):
        if phrase not in " ".join(readme.split()):
            fail(f"README anchor missing: {phrase}")
    if "$holytail:holytail" not in readme:
        fail("README must use the installed $holytail:holytail skill name")


def check_guidance_boundaries(
    source: str, label: str, *, inline: bool = False, writer: bool = False,
) -> None:
    """Pin known routing/ownership regressions; this is prose lint, not model proof."""
    normalized = " ".join(source.split())
    required = []
    if inline:
        required.extend((
            "Already-authorized reversible operations are not formal merely because they have an external effect",
            "`FULL` quality alone does not select a route",
        ))
    if writer:
        required.extend((
            "lead alone writes `.holytail/check.md`",
            "worker writes only its uniquely scoped delivery",
        ))
    for phrase in required:
        if phrase not in normalized:
            fail(f"{label} is missing routing/ownership boundary: {phrase}")

    regressions = (
        r"\b(?:keep Ponytail active|Ponytail (?:remains|stays|is always) active)\b",
        r"\b(?:user's |parent's )?(?:already-active minimizer|minimizer remains active)\b",
        r"\b(?:deletion, publication, external side effect|deletion or external/irreversible effects)\b",
        r"\b(?:external (?:side )?effects?) (?:alone )?(?:requires?|triggers?|forces?) `?FORMAL\b",
        r"\b(?:escalate|use `?FORMAL`?) for (?:any |all )?external (?:side )?effects?\b",
        r"`?FULL`? quality (?:alone )?(?:requires?|triggers?|forces?) `?FORMAL\b",
        r"\bworker (?:also )?(?:writes?|updates?|owns?) `?\.holytail/check\.md",
        r"\bminimizer and writes `?\.holytail/check\.md",
    )
    for pattern in regressions:
        if re.search(pattern, normalized, re.I):
            fail(f"{label} contains a routing/ownership regression")


def check_worker_blocking_boundary(source: str, label: str) -> None:
    normalized = " ".join(source.split()).lower()
    for phrase in (
        "accepted or explicitly protected options",
        "irreversible choice falls outside assignment authority",
        "reversible mechanism choices that do not close an accepted or explicitly protected option remain within worker authority",
    ):
        if phrase not in normalized:
            fail(f"{label} is missing worker blocking boundary: {phrase}")
    if "future options" in normalized:
        fail(f"{label} retains hypothetical future-option blocking")


def validate_guidance_boundaries() -> None:
    inline_paths = {
        ROOT / "README.md",
        ROOT / "docs" / "concepts-and-evidence.md",
        SKILL / "SKILL.md",
        SKILL / "references" / "routing-context.md",
    }
    writer_paths = inline_paths | {
        ROOT / "agents" / "holytail.md",
        PLUGIN / "profiles" / "holytail.md",
        SKILL / "references" / "delivery.md",
    }
    for path in writer_paths | {SKILL / "references" / "soulmate-dotagents.md"}:
        check_guidance_boundaries(
            path.read_text(encoding="utf-8"), str(path.relative_to(ROOT)),
            inline=path in inline_paths, writer=path in writer_paths,
        )
    for path in (
        ROOT / "agents" / "holytail.md",
        PLUGIN / "profiles" / "holytail.md",
        SKILL / "SKILL.md",
        ROOT / "docs" / "concepts-and-evidence.md",
    ):
        check_worker_blocking_boundary(path.read_text(encoding="utf-8"), str(path.relative_to(ROOT)))


def _single_binding(source: str, pattern: str, label: str) -> str:
    matches = re.findall(pattern, source, flags=re.MULTILINE)
    if len(matches) != 1:
        fail(f"workflow artifact is stale: {label} binding must appear exactly once")
    return matches[0]


def _reachable_evidence(evidence: str, repo_root: Path) -> None:
    references = re.findall(r"`([^`]+)`", evidence)
    if not references:
        fail("workflow artifact is stale: invariant evidence has no repo-relative path")
    root = repo_root.resolve()
    for reference in references:
        relative = PurePosixPath(reference)
        if (
            not reference
            or "\\" in reference
            or relative.is_absolute()
            or ".." in relative.parts
        ):
            fail("workflow artifact is stale: invariant evidence path is malformed")
        target = (root / relative).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            fail("workflow artifact is stale: invariant evidence path is unreachable")
        if not target.is_file():
            fail("workflow artifact is stale: invariant evidence path is unreachable")


def _invariant_ids(accepted: str, check: str, repo_root: Path) -> tuple[list[str], list[str]]:
    accepted_ids = re.findall(r"^-\s+(I\d+):\s+\S", accepted, flags=re.MULTILINE)
    if not accepted_ids or len(accepted_ids) != len(set(accepted_ids)):
        fail("workflow artifact is stale: accepted invariant set is malformed or duplicated")

    section = re.search(
        r"^## Invariant-level findings\s*$\n(?P<table>.*?)(?=^## |\Z)",
        check,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not section:
        fail("workflow artifact is stale: invariant findings table is missing")
    rows: list[str] = []
    header_seen = False
    for line in section.group("table").splitlines():
        if not line.strip().startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if columns == ["Invariant", "Finding", "Evidence"]:
            if header_seen:
                fail("workflow artifact is stale: invariant table header is duplicated")
            header_seen = True
            continue
        if len(columns) == 3 and all(set(column) <= {"-", ":"} for column in columns):
            continue
        if len(columns) != 3 or not re.fullmatch(r"I\d+", columns[0]) or not columns[1] or not columns[2]:
            fail("workflow artifact is stale: invariant binding row is malformed")
        _reachable_evidence(columns[2], repo_root)
        rows.append(columns[0])
    if not header_seen or not rows or len(rows) != len(set(rows)):
        fail("workflow artifact is stale: invariant bindings are missing or duplicated")
    return accepted_ids, rows


def validate_snapshot_bindings(
    accepted: str,
    check: str,
    actual_diff_sha256: str,
    *,
    base_revision_exists: bool,
    repo_root: Path = ROOT,
) -> None:
    """Validate mechanical post-check bindings; this proves no semantic truth."""
    accepted_contract_id = _single_binding(
        accepted, r"^-\s+Contract ID:\s+`?([^`\n]+)`?\s*$", "accepted Contract ID"
    )
    check_contract_id = _single_binding(
        check, r"^-\s+Contract ID:\s+`?([^`\n]+)`?\s*$", "check Contract ID"
    )
    if check_contract_id != accepted_contract_id:
        fail("workflow artifact is stale: Contract ID does not match accepted artifact")

    declared_contract_sha256 = _single_binding(
        check, r"^-\s+Contract SHA-256:\s*`?([0-9a-f]{64})`?\s*$", "contract SHA-256"
    )
    actual_contract_sha256 = sha256(accepted.encode("utf-8")).hexdigest()
    if declared_contract_sha256 != actual_contract_sha256:
        fail("workflow artifact is stale: contract SHA-256 does not match accepted artifact")

    base_revision = _single_binding(
        check, r"^-\s+Implementation base revision:\s*`?([0-9a-f]{40})`?\s*$", "implementation base revision"
    )
    if not base_revision_exists:
        fail("workflow artifact is stale: implementation base revision is unavailable")
    declared_formula = _single_binding(
        check, r"^-\s+Digest formula:\s*`?(.+?)`?\s*$", "digest formula"
    )
    expected_formula = (
        f"git diff --binary {base_revision} -- . "
        "':(exclude).holytail/accepted.md' ':(exclude).holytail/check.md' | sha256sum"
    )
    if declared_formula != expected_formula:
        fail("workflow artifact is stale: digest formula is malformed")
    declared_diff_sha256 = _single_binding(
        check, r"^-\s+Implementation diff SHA-256:\s*`?([0-9a-f]{64})`?\s*$", "implementation diff SHA-256"
    )
    if declared_diff_sha256 != actual_diff_sha256:
        fail("workflow artifact is stale: implementation diff SHA-256 does not match checkout")

    accepted_ids, check_ids = _invariant_ids(accepted, check, repo_root)
    if set(accepted_ids) != set(check_ids):
        fail("workflow artifact is stale: accepted and checked invariant sets differ")


def validate_workflow_artifacts() -> None:
    accepted = (ROOT / ".holytail" / "accepted.md").read_text(encoding="utf-8")
    check = (ROOT / ".holytail" / "check.md").read_text(encoding="utf-8")
    assert_no_internal_routing_notes(accepted, ".holytail/accepted.md")
    assert_no_internal_routing_notes(check, ".holytail/check.md")
    for phrase in ("Contract ID:", "Implementation boundary", "I1", "I16"):
        if phrase not in accepted:
            fail(f"accepted artifact missing: {phrase}")
    for phrase in ("Contract SHA-256:", "Accepted artifact", "Implementation snapshot", "Invariant-level findings", "I1", "I16"):
        if phrase not in check:
            fail(f"post-check artifact missing: {phrase}")

    base_revision = _single_binding(
        check, r"^-\s+Implementation base revision:\s*`?([0-9a-f]{40})`?\s*$", "implementation base revision"
    )
    base_check = subprocess.run(
        ["git", "cat-file", "-e", f"{base_revision}^{{commit}}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    diff = subprocess.run(
        [
            "git", "diff", "--binary", base_revision, "--", ".",
            ":(exclude).holytail/accepted.md",
            ":(exclude).holytail/check.md",
        ],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if diff.returncode:
        fail("workflow artifact is stale: implementation diff could not be recomputed")
    validate_snapshot_bindings(
        accepted,
        check,
        sha256(diff.stdout).hexdigest(),
        base_revision_exists=base_check.returncode == 0,
        repo_root=ROOT,
    )

    benchmark_source = (ROOT / "scripts" / "benchmark.py").read_text(encoding="utf-8")
    for phrase in ("Arm A", "Arm B", "accepted_behaviors", "silent_drop", "status=not-run"):
        if phrase not in benchmark_source and phrase.lower() not in benchmark_source.lower():
            fail(f"benchmark scaffold missing: {phrase}")

def assert_no_economy_directives(source: str, label: str = "authored source") -> None:
    """Reject Holytail-owned economy directives while allowing active minimizer references."""
    patterns = (
        r"\bminimal implementation\b",
        r"\bminimum implementation\b",
        r"\bsmallest faithful (?:step|mechanism|implementation)\b",
        r"\bsimplifications applied\b",
        r"\brejected simplifications\b",
        r"\beconomy ladder\b",
        r"\bminimize only unconstrained\b",
        r"\bminimize expected (?:rework|code)\b",
        r"\bminimiz(?:e|es|ed|ing) (?:code|mechanism|implementation)\b",
        r"\bprefer in order:\s*\n?\s*1\.\s*no new mechanism\b",
    )
    for pattern in patterns:
        if re.search(pattern, source, re.I):
            fail(f"{label} contains a Holytail economy directive: {pattern}")


THIRD_PARTY_VERSION_PATTERNS = (
    re.compile(r"@sentry/dotagents@(?:[~^<>=]*v?)?\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z.-]+)?\b"),
    re.compile(r"@openai/codex@(?:[~^<>=]*v?)?\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z.-]+)?\b"),
    re.compile(r"\bdotagents\s+(?:(?:version|release)\s+)?v?\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z.-]+)?\b"),
    re.compile(r"\bCodex\s+(?:(?:version|release)\s+)?v?\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z.-]+)?\b"),
    re.compile(r"\bSoulmate\s+(?:(?:version|release)\s+)?v?\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z.-]+)?\b"),
)


def assert_no_third_party_version_pins(source: str, label: str = "authored source") -> None:
    """Reject exact ecosystem-version prose outside the smoke/CI allowlist."""
    for pattern in THIRD_PARTY_VERSION_PATTERNS:
        match = pattern.search(source)
        if match:
            fail(f"{label} contains a non-load-bearing third-party version pin: {match.group(0)}")


def validate_authoring_boundaries() -> None:
    mandatory = [
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        ROOT / "agents" / "holytail.md",
        ROOT / "agents" / "semanticreviewer.toml",
        PLUGIN / "profiles" / "holytail.md",
        PLUGIN / "profiles" / "semanticreviewer.md",
        SKILL / "SKILL.md",
        SKILL / "agents" / "openai.yaml",
        SKILL / "references" / "delivery.md",
        SKILL / "references" / "routing-context.md",
        SKILL / "references" / "soulmate-dotagents.md",
    ]
    for path in mandatory:
        source = path.read_text(encoding="utf-8")
        assert_no_economy_directives(source, str(path.relative_to(ROOT)))
        assert_no_third_party_version_pins(source, str(path.relative_to(ROOT)))

    allowed_pin_paths = {
        ROOT / "scripts" / "smoke-dotagents.sh",
        ROOT / ".github" / "workflows" / "ci.yml",
    }
    for path in ROOT.rglob("*"):
        if not path.is_file() or path in allowed_pin_paths or path.suffix in {".svg", ".pyc"}:
            continue
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        assert_no_third_party_version_pins(source, str(path.relative_to(ROOT)))


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
    markdown_files.extend((ROOT / "docs").rglob("*.md"))
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
    check_guidance_boundaries(context, "SessionStart output", inline=True, writer=True)
    if len(context.split()) > 400:
        fail("SessionStart routing exceeds the 400-word context budget; keep details in the skill")

    subagent = run_hook("SubagentStart")
    if subagent.returncode != 0 or subagent.stdout:
        fail("routing hook must ignore SubagentStart to preserve dedicated profiles")

    unrelated = run_hook("PostToolUse")
    if unrelated.returncode != 0 or unrelated.stdout:
        fail("routing hook must ignore unrelated events")


def main() -> int:
    require_files()
    validate_public_privacy()
    validate_manifests()
    validate_skill()
    validate_status_contracts()
    validate_guidance_boundaries()
    validate_workflow_artifacts()
    validate_authoring_boundaries()
    validate_reviewer()
    validate_markdown_links()
    validate_hooks()
    print("Holytail package validation: consistent (mechanical checks only)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"Holytail package validation: FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
