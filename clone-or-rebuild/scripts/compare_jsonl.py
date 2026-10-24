#!/usr/bin/env python3
"""Compare JSON lines deterministically without executing a target.

Each line is a complete JSON value. Order is significant both in JSONL and
arrays. JSON object key order is ignored. Exact numbers by default; optional
absolute tolerance for float/int values. Avoid feeding secrets or personal data.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any


def differences(a: Any, b: Any, tolerance: float = 0.0, path: str = "$") -> list[str]:
    if isinstance(a, bool) or isinstance(b, bool):
        return [] if type(a) is type(b) and a == b else [f"{path}: {a!r} != {b!r}"]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tolerance:
            return []
        return [f"{path}: {a!r} != {b!r} (tol={tolerance})"]
    if type(a) is not type(b):
        return [f"{path}: types differ ({type(a).__name__} vs {type(b).__name__})"]
    if isinstance(a, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            field = f"{path}.{key}"
            if key not in a:
                result.append(f"{field}: extra key in candidate")
            elif key not in b:
                result.append(f"{field}: missing key in candidate")
            else:
                result.extend(differences(a[key], b[key], tolerance, field))
        return result
    if isinstance(a, list):
        result = []
        if len(a) != len(b):
            result.append(f"{path}: array lengths differ ({len(a)} vs {len(b)})")
        for i, (x, y) in enumerate(zip(a, b)):
            result.extend(differences(x, y, tolerance, f"{path}[{i}]"))
        return result
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


def compare_files(reference: Path, candidate: Path, tolerance: float = 0., max_diffs: int = 20) -> dict:
    errors = []
    lines = 0
    matches = 0
    with reference.open(encoding="utf-8") as first, candidate.open(encoding="utf-8") as second:
        for line_num, (left, right) in enumerate(itertools.zip_longest(first, second), 1):
            lines += 1
            if left is None or right is None:
                errors.append(f"line {line_num}: {'missing' if right is None else 'extra'} candidate line")
                continue
            try:
                a = json.loads(left)
                b = json.loads(right)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_num}: {exc}") from exc
            diff = differences(a, b, tolerance)
            if not diff:
                matches += 1
            else:
                errors.extend([f"line {line_num}: {issue}" for issue in diff])
    return {"passed": not errors, "matching_lines": matches, "total_lines": lines,
            "difference_count": len(errors), "differences": errors[:max_diffs],
            "truncated": len(errors) > max_diffs}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=0.0)
    parser.add_argument("--max-diffs", type=int, default=20)
    args = parser.parse_args()
    if args.tolerance < 0 or not math.isfinite(args.tolerance):
        parser.error("--tolerance must be a finite non-negative number")
    if args.max_diffs < 1:
        parser.error("--max-diffs must be >= 1")
    try:
        report = compare_files(args.reference, args.candidate, args.tolerance, args.max_diffs)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
