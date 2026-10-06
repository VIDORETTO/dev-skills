from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
BENCH = PACKAGE / "scripts" / "bench_ab.py"

FAKE_CLAUDE = r'''
import json, os, sys
prompt = sys.argv[sys.argv.index("-p") + 1]
hybrid = prompt.startswith("/hybrid-start")
open("solved.txt", "w").write("ok")
print(json.dumps({"type": "result", "is_error": False, "num_turns": 11 if hybrid else 10,
                  "duration_ms": 1100 if hybrid else 1000, "total_cost_usd": 0.105 if hybrid else 0.1,
                  "usage": {"input_tokens": 10, "output_tokens": 5, "cache_read_input_tokens": 100,
                            "cache_creation_input_tokens": 20}}))
'''


class BenchTests(unittest.TestCase):
    def test_runs_both_arms_and_reports_overhead_per_success(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = root / "fake_claude.py"
            fake.write_text(FAKE_CLAUDE, encoding="utf-8")
            template = root / "template"
            (template / "src").mkdir(parents=True)
            (template / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
            tasks = root / "tasks.json"
            tasks.write_text(json.dumps([{"id": "t1", "repo": str(template), "prompt": "fix it",
                                          "check": f'"{sys.executable}" -c "import pathlib,sys; sys.exit(0 if pathlib.Path(\'solved.txt\').exists() else 1)"'}]),
                             encoding="utf-8")
            out = root / "out"
            completed = subprocess.run(
                [sys.executable, str(BENCH), "--tasks", str(tasks), "--runs", "2", "--out", str(out),
                 "--claude-bin", f"{sys.executable} {fake}"],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["arms"]["baseline"]["runs"], 2)
            self.assertEqual(summary["arms"]["hybrid"]["pass_rate"], 1.0)
            self.assertAlmostEqual(summary["overhead"]["cost_per_success_pct"], 5.0, places=1)
            self.assertAlmostEqual(summary["overhead"]["duration_pct"], 10.0, places=1)
            self.assertEqual(len((out / "runs.jsonl").read_text(encoding="utf-8").splitlines()), 4)
            installed = list(out.glob("work/t1-hybrid-*/.claude/skills/hybrid-start/SKILL.md"))
            self.assertTrue(installed)
            self.assertFalse(list(out.glob("work/t1-baseline-*/.claude/skills")))


if __name__ == "__main__":
    unittest.main()
