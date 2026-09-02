#!/usr/bin/env python3
"""Reproducible benchmark plan and deterministic fixture for Holytail.

Real model runs are intentionally not bundled: this command never fabricates a
preservation result. Arm A is the minimizer alone; Arm B is the same minimizer
plus Holytail. The fixture checks that the accepted-behavior metric is defined
and that a silent drop is observable.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    name: str
    accepted_behaviors: tuple[str, ...]


TASKS = (
    Task("preserve-validation", ("validate input", "report invalid input", "retain error context")),
    Task("preserve-lifecycle", ("start state", "finish state", "report failure state")),
    Task("preserve-authority", ("keep operator decision", "keep unknown explicit")),
)


def silent_drop_count(accepted: tuple[str, ...], observed: tuple[str, ...]) -> int:
    """Count accepted behaviors absent from an observed implementation."""
    return sum(behavior not in observed for behavior in accepted)


def self_test() -> None:
    task = TASKS[0]
    observed = ("validate input", "report invalid input")
    assert silent_drop_count(task.accepted_behaviors, observed) == 1
    assert silent_drop_count(task.accepted_behaviors, task.accepted_behaviors) == 0
    print("fixture=self-test status=ok silent_drop_metric=accepted_behavior_absence")
    print("evaluation=status=not-run reason=real-model-runs-unavailable")


def plan() -> None:
    print("evaluation=status=not-run reason=real-model-runs-unavailable")
    print("arms=A:minimizer-alone B:minimizer-plus-holytail")
    print("metric=accepted_behaviors_silently_dropped")
    for task in TASKS:
        print(f"task={task.name} accepted_behaviors={len(task.accepted_behaviors)}")
    print("report=per-task-result,variance,caveats(model,prompt,task-corpus,host)")
    print("per_task_results=status=not-run variance=status=not-run")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    self_test() if args.self_test else plan()
