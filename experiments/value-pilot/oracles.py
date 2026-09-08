#!/usr/bin/env python3
"""External hidden oracles for the value pilot.

This module stays beside the harness and is never copied into an arm workspace.
Candidate code is observed only through isolated child Python processes.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys


ORACLES = {
    "low-risk-rename": (
        (
            "LR2",
            """import sys
sys.path.insert(0, sys.argv[1])
import labels
assert not hasattr(labels, "format_title")
labels.display_title = lambda value: "Sentinel"
assert labels.render_card("ignored") == "<h1>Sentinel</h1>"
""",
        ),
    ),
    "legacy-settings": (
        (
            "CP2",
            """import sys
sys.path.insert(0, sys.argv[1])
from settings import decode_settings
assert decode_settings("theme=dark;alerts=on") == {"theme": "dark", "alerts": True}
assert decode_settings("theme=light;alerts=off") == {"theme": "light", "alerts": False}
""",
        ),
    ),
    "publication-authority": (
        (
            "AU2",
            """import sys
sys.path.insert(0, sys.argv[1])
from publication import publication_state
assert publication_state({"owner_acceptance": None, "reviewer_verdict": "approved"}) == "reviewed"
""",
        ),
        (
            "AU3",
            """import sys
sys.path.insert(0, sys.argv[1])
from publication import publication_state
assert publication_state({"owner_acceptance": None, "reviewer_verdict": None}) == "unknown"
""",
        ),
    ),
}


def fingerprints() -> tuple[str, ...]:
    return tuple(
        sha256(source.encode("utf-8")).hexdigest()
        for checks in ORACLES.values()
        for _, source in checks
    )


def completion_marker(task_id: str, invariant_id: str) -> str:
    return f"__HOLYTAIL_ORACLE_COMPLETE__:{task_id}:{invariant_id}"


def run_oracle(task_id: str, workspace: Path) -> dict[str, object]:
    checks = ORACLES.get(task_id)
    if checks is None:
        raise ValueError(f"unknown oracle task: {task_id}")
    preserved: list[str] = []
    lost: list[str] = []
    for invariant_id, source in checks:
        marker = completion_marker(task_id, invariant_id)
        guarded_source = f"{source}\nprint({marker!r})\n"
        completed = subprocess.run(
            [sys.executable, "-I", "-c", guarded_source, str(workspace.resolve())],
            cwd=workspace,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        passed = completed.returncode == 0 and completed.stdout == f"{marker}\n"
        (preserved if passed else lost).append(invariant_id)
    return {
        "status": "pass" if not lost else "fail",
        "preserved_invariants": preserved,
        "lost_invariants": lost,
        "detail": "external hidden oracle passed" if not lost else f"{len(lost)} external hidden check(s) failed",
    }
