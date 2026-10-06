from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_runner import PACKAGE, invoke, write_standard_effort, write_text


def register_inputs(project: Path, directory: Path) -> None:
    invoke(
        "checkpoint", "write", "--project", str(project), "--effort", directory.name,
        "--expected-revision", "0", "--input", f"contract=specs/{directory.name}/spec.md",
        "--input", f"plan=specs/{directory.name}/plan.md",
    )


def ticket_meta(directory: Path, name: str = "TK-001-demo.md") -> str:
    return (directory / "tickets" / name).read_text(encoding="utf-8")


class TicketGateTests(unittest.TestCase):
    def update(self, project: Path, *arguments: str, code: int = 0) -> dict:
        return invoke("ticket", "update", "--project", str(project), "--effort", "001-demo",
                      "--ticket", "TK-001", *arguments, expected_code=code)[1]

    def passed_evidence(self, project: Path) -> None:
        write_text(project / "src" / "demo.py", "def public_function():\n    return 7")
        invoke("evidence", "add", "--project", str(project), "--effort", "001-demo", "--ticket", "TK-001",
               "--acceptance-refs", "AC-001", "--procedure", "python -m unittest", "--result", "passed",
               "--executed", "--path", "src")

    def test_draft_cannot_jump_to_delivery_states(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            path = directory / "tickets" / "TK-001-demo.md"
            path.write_text(path.read_text(encoding="utf-8").replace("status: ready", "status: draft"), encoding="utf-8")
            self.passed_evidence(project)
            result = self.update(project, "--status", "verified", code=2)
            self.assertEqual(result["error"], "ticket_transition")

    def test_terminal_status_cannot_reopen_silently(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            write_standard_effort(project)
            self.update(project, "--status", "cancelled")
            self.assertEqual(self.update(project, "--status", "in_progress", code=2)["error"], "ticket_transition")

    def test_verified_records_passed_verification_in_the_same_call(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            self.passed_evidence(project)
            result = self.update(project, "--status", "verified")
            self.assertEqual(result["verification_status"], "passed")
            self.assertIn("verification_status: passed", ticket_meta(directory))

    def test_done_requires_review_and_never_writes_an_invalid_ticket(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            self.passed_evidence(project)
            before = ticket_meta(directory)
            result = self.update(project, "--status", "done", code=2)
            self.assertEqual(result["error"], "ticket_gate")
            self.assertIn("review", result["message"])
            self.assertEqual(before, ticket_meta(directory))
            result = self.update(project, "--status", "done", "--review", "passed")
            self.assertEqual(result["to"], "done")
            self.assertEqual(result["verification_status"], "passed")
            self.assertIn("review_status: passed", ticket_meta(directory))
            _, validation = invoke("validate", "--project", str(project), "--effort", "001-demo")
            self.assertTrue(validation["ok"], validation)

    def test_validate_rejects_done_without_review(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            path = directory / "tickets" / "TK-001-demo.md"
            path.write_text(path.read_text(encoding="utf-8").replace("status: ready", "status: done")
                            .replace("verification_status: not_run", "verification_status: passed"), encoding="utf-8")
            _, validation = invoke("validate", "--project", str(project), "--effort", "001-demo", expected_code=1)
            self.assertTrue(any("review_status=passed" in error for error in validation["errors"]), validation)


class EvidenceRunTests(unittest.TestCase):
    def run_evidence(self, project: Path, command: str, *extra: str, code: int = 0) -> dict:
        return invoke("evidence", "run", "--project", str(project), "--effort", "001-demo",
                      "--ticket", "TK-001", "--acceptance-refs", "AC-001", "--command", command,
                      "--path", "src", *extra, expected_code=code)[1]

    def test_passing_command_records_runner_evidence_and_advances_ticket(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            write_text(project / "src" / "demo.py", "VALUE = 7")
            command = f'"{sys.executable}" -c "print(7)"'
            result = self.run_evidence(project, command)
            self.assertEqual(result["result"], "passed")
            self.assertEqual(result["ticket_status"], "verified")
            self.assertNotIn("output_tail", result)
            record = json.loads((directory / "evidence" / "EV-001.json").read_text(encoding="utf-8"))
            self.assertEqual(record["executor"], "runner")
            self.assertEqual(record["exit_code"], 0)
            self.assertEqual(record["execution_status"], "executed")
            self.assertIn("verification_status: passed", ticket_meta(directory))

    def test_failing_command_is_recorded_as_failed_with_short_output(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            write_text(project / "src" / "demo.py", "VALUE = 7")
            command = f'"{sys.executable}" -c "import sys; print(\'boom\'); sys.exit(3)"'
            result = self.run_evidence(project, command, code=1)
            self.assertEqual(result["result"], "failed")
            self.assertEqual(result["exit_code"], 3)
            self.assertIn("boom", result["output_tail"])
            self.assertIn("status: ready", ticket_meta(directory))
            self.assertIn("verification_status: failed", ticket_meta(directory))

    def test_compact_effort_records_without_ticket(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            invoke("init", "--project", str(project), "--mode", "compact")
            invoke("scaffold", "--project", str(project), "--effort", "002-small", "--mode", "compact")
            write_text(project / "src" / "demo.py", "VALUE = 7")
            _, result = invoke("evidence", "run", "--project", str(project), "--effort", "002-small",
                               "--acceptance-refs", "AC-001", "--command", f'"{sys.executable}" -c "pass"',
                               "--path", "src")
            self.assertEqual(result["result"], "passed")
            self.assertIsNone(result["ticket"])


class NextTests(unittest.TestCase):
    def test_next_registers_inputs_and_returns_a_small_ready_package(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            write_standard_effort(project, second_ticket=True)
            _, preview = invoke("next", "--project", str(project), "--effort", "001-demo")
            self.assertFalse(preview["ticket"]["ready"])
            self.assertTrue(preview["untracked_inputs"])
            completed = subprocess.run(
                [sys.executable, str(PACKAGE / "scripts" / "hybrid.py"), "next", "--project", str(project),
                 "--effort", "001-demo", "--write", "--json"],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(completed.returncode, 0, completed.stdout)
            result = json.loads(completed.stdout)
            self.assertEqual(result["stage"], "tickets")
            self.assertEqual(result["ticket"]["id"], "TK-001")
            self.assertTrue(result["ticket"]["ready"], result)
            self.assertEqual(result["queue"], ["TK-002"])
            self.assertEqual(result["untracked_inputs"], {})
            self.assertLess(len(completed.stdout), 2400, "next must stay a small package")

    def test_next_reports_stale_evidence_and_invalidates_with_write(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            register_inputs(project, directory)
            write_text(project / "src" / "demo.py", "VALUE = 7")
            invoke("evidence", "add", "--project", str(project), "--effort", "001-demo", "--ticket", "TK-001",
                   "--acceptance-refs", "AC-001", "--procedure", "python -m unittest", "--result", "passed",
                   "--executed", "--path", "src")
            write_text(project / "src" / "demo.py", "VALUE = 8")
            _, result = invoke("next", "--project", str(project), "--effort", "001-demo", "--write")
            self.assertEqual(result["stale_evidence"], ["EV-001"])
            record = json.loads((directory / "evidence" / "EV-001.json").read_text(encoding="utf-8"))
            self.assertEqual(record["result"], "stale")

    def test_next_on_compact_effort_points_to_change(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            invoke("init", "--project", str(project), "--mode", "compact")
            invoke("scaffold", "--project", str(project), "--effort", "002-small", "--mode", "compact")
            _, result = invoke("next", "--project", str(project), "--effort", "002-small", "--write")
            self.assertEqual(result["contract"], "specs/002-small/change.md")
            self.assertIsNone(result["ticket"])


MINIMAL_TICKET = """
---
schema: hybrid/ticket
schema_version: "1.0"
id: TK-001
effort: 001-demo
type: delivery
status: ready
ticket_revision: 1
requires: []
requirement_refs: [FR-001]
acceptance_refs: [AC-001]
spec_revision: 1
plan_revision: 1
owned_areas: [src, tests]
verification_status: not_run
---
# TK-001 — Demo
## Objetivo e limites
Deliver AC-001. Não inclui AC-002.
## Leitura em ordem
1. `src/demo.py` → `public_function`.
## Exemplos de aceite
**AC-001**: valid input returns 7.
## Validação
`python -m unittest`
"""


class MinimalTicketTests(unittest.TestCase):
    def test_optional_sections_can_be_omitted(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            write_text(directory / "tickets" / "TK-001-demo.md", MINIMAL_TICKET)
            register_inputs(project, directory)
            _, result = invoke("next", "--project", str(project), "--effort", "001-demo")
            self.assertTrue(result["ticket"]["ready"], result)

    def test_core_sections_remain_required(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            write_text(directory / "tickets" / "TK-001-demo.md", MINIMAL_TICKET.replace("## Validação", "## Notas"))
            _, result = invoke("validate", "--project", str(project), "--effort", "001-demo", expected_code=1)
            self.assertTrue(any("Validação" in error for error in result["errors"]), result)


class SessionLimitTests(unittest.TestCase):
    def test_limits_renew_by_absolute_context_not_window_percentage(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            write_standard_effort(project)
            _, result = invoke("session", "--project", str(project), "--effort", "001-demo", "--write")
            self.assertEqual(result["limits"]["renew_context_tokens"], 100000)
            self.assertNotIn("context_used_percent", result["limits"])
            self.assertNotIn("60%", result["goal_objective"] + result["continuation_prompt"])
            written = (project / ".hybrid" / "continuations" / "001-demo.md").read_text(encoding="utf-8")
            self.assertNotIn("60%", written)


class InstallTargetTests(unittest.TestCase):
    def test_existing_claude_skill_root_is_detected(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            (project / ".claude" / "skills").mkdir(parents=True)
            _, result = invoke("install", "--project", str(project))
            self.assertEqual(result["skill_root"], ".claude/skills")
            self.assertTrue((project / ".claude" / "skills" / "hybrid-start" / "SKILL.md").exists())
            installed = subprocess.run(
                [sys.executable, str(project / ".hybrid" / "hybrid.py"), "package-validate", "--json"],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(installed.returncode, 0, installed.stdout)

    def test_every_skill_disables_implicit_invocation_for_codex(self):
        for skill in sorted((PACKAGE / "skills").glob("hybrid-*")):
            policy = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.assertIn("allow_implicit_invocation: false", policy, skill.name)


if __name__ == "__main__":
    unittest.main()
