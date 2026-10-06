#!/usr/bin/env python3
"""A/B benchmark: the same tasks with and without the hybrid skills.

Each task copies a template project twice: `baseline` runs the prompt as-is,
`hybrid` installs the kit under `.claude/skills` and prefixes `/hybrid-start`.
Both run `claude -p ... --output-format json`; the task's `check` command
decides success.  The summary compares medians and cost per successful task.

tasks.json: [{"id": "...", "repo": "path/to/template", "prompt": "...", "check": "shell cmd"}]

This spends real model usage; start with --runs 1 on one task.
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / "hybrid.py"
ARMS = ("baseline", "hybrid")


def run_arm(task: dict, arm: str, index: int, args: argparse.Namespace) -> dict:
    work = args.out / "work" / f"{task['id']}-{arm}-{index}"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(task["repo"], work)
    prompt = task["prompt"]
    if arm == "hybrid":
        subprocess.run([sys.executable, str(RUNNER), "install", "--project", str(work),
                        "--skill-root", ".claude/skills", "--json"], check=True, capture_output=True)
        prompt = f"/hybrid-start {prompt}"
    command = [*shlex.split(args.claude_bin), "-p", prompt, "--output-format", "json", *shlex.split(args.claude_args)]
    completed = subprocess.run(command, cwd=work, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=args.timeout)
    try:
        result = json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        result = {"is_error": True, "raw": completed.stdout[-500:] + completed.stderr[-500:]}
    check = subprocess.run(task["check"], shell=True, cwd=work, capture_output=True, timeout=args.timeout)
    usage = result.get("usage", {})
    return {
        "task": task["id"], "arm": arm, "run": index, "passed": check.returncode == 0 and not result.get("is_error"),
        "num_turns": result.get("num_turns"), "duration_ms": result.get("duration_ms"),
        "cost_usd": result.get("total_cost_usd"),
        "tokens": sum(int(usage.get(key, 0) or 0) for key in
                      ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")),
    }


def median(values: list) -> float | None:
    values = [value for value in values if isinstance(value, (int, float))]
    return statistics.median(values) if values else None


def pct(new: float | None, base: float | None) -> float | None:
    return round(100 * (new / base - 1), 2) if new is not None and base else None


def summarize(rows: list[dict]) -> dict:
    arms = {}
    for arm in ARMS:
        selected = [row for row in rows if row["arm"] == arm]
        successes = sum(row["passed"] for row in selected)
        total_cost = sum(row["cost_usd"] or 0 for row in selected)
        arms[arm] = {
            "runs": len(selected), "pass_rate": round(successes / len(selected), 3) if selected else 0,
            "median_turns": median([row["num_turns"] for row in selected]),
            "median_duration_ms": median([row["duration_ms"] for row in selected]),
            "median_tokens": median([row["tokens"] for row in selected]),
            "cost_per_success_usd": round(total_cost / successes, 6) if successes else None,
        }
    base, hybrid = arms["baseline"], arms["hybrid"]
    return {"arms": arms, "overhead": {
        "turns_pct": pct(hybrid["median_turns"], base["median_turns"]),
        "duration_pct": pct(hybrid["median_duration_ms"], base["median_duration_ms"]),
        "tokens_pct": pct(hybrid["median_tokens"], base["median_tokens"]),
        "cost_per_success_pct": pct(hybrid["cost_per_success_usd"], base["cost_per_success_usd"]),
    }}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--out", type=Path, default=Path("bench-out"))
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--claude-args", default="", help='e.g. "--model claude-sonnet-5-5 --permission-mode acceptEdits"')
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    tasks = json.loads(args.tasks.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    with (args.out / "runs.jsonl").open("w", encoding="utf-8") as log:
        for task in tasks:
            for index in range(args.runs):
                for arm in ARMS:  # interleave arms so drift affects both equally
                    row = run_arm(task, arm, index, args)
                    rows.append(row)
                    log.write(json.dumps(row) + "\n")
                    log.flush()
    summary = summarize(rows)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["overhead"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
