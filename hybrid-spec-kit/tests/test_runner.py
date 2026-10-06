from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
RUNNER = PACKAGE / "scripts" / "hybrid.py"


def invoke(*arguments: str, expected_code: int = 0) -> tuple[int, dict]:
    completed = subprocess.run(
        [sys.executable, str(RUNNER), *arguments, "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != expected_code:
        raise AssertionError(
            f"unexpected exit code {completed.returncode} != {expected_code}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    try:
        return completed.returncode, json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"runner did not emit JSON: {completed.stdout}\n{completed.stderr}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_standard_effort(project: Path, effort: str = "001-demo", second_ticket: bool = False) -> Path:
    invoke("init", "--project", str(project), "--mode", "standard")
    invoke("scaffold", "--project", str(project), "--effort", effort, "--title", "Demo")
    directory = project / "specs" / effort
    write_text(
        directory / "spec.md",
        f"""
        ---
        schema: hybrid/spec
        schema_version: "1.0"
        effort_id: {effort}
        revision: 1
        status: accepted
        profile: standard
        ---
        # Specification: Demo
        ## Scope
        Included and excluded behavior.
        ## Requirements
        - **FR-001** — return the requested result.
        - **FR-002** — reject the invalid result.
        ## Acceptance scenarios
        - **AC-001** — Given valid input, when called, then return 7.
        - **AC-002** — Given invalid input, when called, then return an error and preserve state.
        """,
    )
    write_text(
        directory / "plan.md",
        f"""
        ---
        schema: hybrid/plan
        schema_version: "1.0"
        effort_id: {effort}
        revision: 1
        spec_revision: 1
        status: ready
        ---
        # Plan: Demo
        ## Summary
        Use the existing public interface.
        ## Modules, interfaces, consumers, and seams
        Module and seam are recorded.
        ## Verification strategy
        AC-001 and AC-002 use independent literal outcomes.
        """,
    )
    write_text(directory / "tickets" / "TK-001-demo.md", ticket_text(effort, "TK-001", [], ["FR-001"], ["AC-001"]))
    if second_ticket:
        write_text(directory / "tickets" / "TK-002-invalid.md", ticket_text(effort, "TK-002", ["TK-001"], ["FR-002"], ["AC-002"]))
    return directory


def ticket_text(effort: str, ticket_id: str, requires: list[str], requirements: list[str], acceptances: list[str]) -> str:
    req = ", ".join(requirements)
    ac = ", ".join(acceptances)
    blockers = ", ".join(requires) if requires else "nenhum"
    requires_yaml = "[]" if not requires else "[" + ", ".join(requires) + "]"
    return f"""
    ---
    schema: hybrid/ticket
    schema_version: "1.0"
    id: {ticket_id}
    effort: {effort}
    type: delivery
    status: ready
    ticket_revision: 1
    requires: {requires_yaml}
    requirement_refs: [{req}]
    acceptance_refs: [{ac}]
    spec_revision: 1
    plan_revision: 1
    owned_areas: [src, tests]
    verification_status: not_run
    ---
    # {ticket_id} — Demo slice
    ## Objetivo e limites
    Deliver {ac}. Não inclui unrelated work.
    ## Leitura em ordem
    1. `src/demo.py` → `public_function` — existing behavior.
    ## Decisões já resolvidas
    Use the public interface and a literal oracle.
    ## Mapa de alterações
    Existing `src/demo.py`; new `tests/test_demo.py`.
    ## Contrato técnico
    Inputs are valid values; outputs are observable; errors preserve state.
    ## Exemplos de aceite
    **{acceptances[0]}**: valid input produces the literal expected result.
    ## Dependências e sequência de execução
    Depende de: {blockers}.
    - [ ] {ticket_id}.1 Write the behavior case and observe red.
    - [ ] {ticket_id}.2 Implement the minimum and observe green.
    ## Validação
    Comando/procedimento exato: `python -m unittest`.
    ## Condição de retorno à planejadora
    Return if the interface or contract differs.
    ## Relatório de saída
    Report changed symbols, acceptance, evidence, limits, and next action.
    """


class RunnerTests(unittest.TestCase):
    def test_package_structure_is_valid(self) -> None:
        _, result = invoke("package-validate")
        self.assertTrue(result["ok"])
        self.assertEqual(result["skill_count"], 10)
        self.assertGreaterEqual(result["schema_count"], 6)

    def test_checked_in_examples_are_runnable_project_layouts(self) -> None:
        standard = PACKAGE / "examples" / "standard" / "reserva-estoque"
        compact = PACKAGE / "examples" / "compact" / "limite-desconto"
        _, standard_result = invoke("validate", "--project", str(standard), "--effort", "014-reserva-estoque")
        _, compact_result = invoke("validate", "--project", str(compact), "--effort", "002-limite-desconto")
        self.assertTrue(standard_result["ok"], standard_result)
        self.assertTrue(compact_result["ok"], compact_result)

    def test_standard_and_compact_scaffolds_validate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-test-") as raw:
            project = Path(raw)
            write_standard_effort(project)
            state = json.loads((project / "specs" / "001-demo" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["baseline"]["kind"], "inventory")
            self.assertTrue(state["baseline"]["ref"])
            _, start = invoke("start", "--project", str(project), "--effort", "001-demo")
            self.assertEqual(start["untracked_inputs"], {"plan": "specs/001-demo/plan.md"})
            _, standard = invoke("validate", "--project", str(project), "--effort", "001-demo")
            self.assertTrue(standard["ok"], standard)

            compact = project / "compact-project"
            invoke("init", "--project", str(compact), "--mode", "compact")
            invoke("scaffold", "--project", str(compact), "--effort", "002-small", "--mode", "compact")
            _, compact_result = invoke("validate", "--project", str(compact), "--effort", "002-small")
            self.assertTrue(compact_result["ok"], compact_result)

    def test_validate_detects_missing_persisted_config_keys(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-config-") as raw:
            project = Path(raw)
            (project / ".hybrid").mkdir()
            (project / ".hybrid" / "config.json").write_text(
                json.dumps({"schema_version": "1.0", "mode": "standard"}),
                encoding="utf-8",
            )
            _, result = invoke("validate", "--project", str(project), "--require-config", expected_code=1)
            self.assertIn("config missing roadmap_path", result["errors"])

    def test_start_reports_git_baseline_and_preserves_existing_changes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-git-") as raw:
            project = Path(raw)
            subprocess.run(["git", "-C", str(project), "init"], check=True, capture_output=True, text=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name", "Hybrid Test"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email", "hybrid@example.invalid"], check=True)
            write_text(project / "README.md", "original")
            subprocess.run(["git", "-C", str(project), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-m", "baseline"], check=True, capture_output=True, text=True)
            invoke("init", "--project", str(project), "--mode", "standard")
            invoke("scaffold", "--project", str(project), "--effort", "001-legacy", "--title", "Legacy")
            readme = project / "README.md"
            readme.write_text("original\nlocal edit\n", encoding="utf-8")
            write_text(project / "notes.md", "user file")
            _, start = invoke("start", "--project", str(project), "--effort", "001-legacy")
            self.assertEqual(start["state"]["baseline"]["kind"], "git")
            self.assertEqual(start["git_baseline"], start["state"]["baseline"]["ref"])
            self.assertTrue(any("README.md" in change for change in start["working_changes"]))
            self.assertTrue(any("notes.md" in change for change in start["working_changes"]))
            self.assertEqual(readme.read_text(encoding="utf-8"), "original\nlocal edit\n")

    def test_graph_detects_cycle_and_reports_frontier(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-test-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project, second_ticket=True)
            _, graph = invoke("graph", "--project", str(project), "--effort", directory.name)
            self.assertEqual(graph["frontier"], ["TK-001"])
            self.assertEqual(graph["order"], ["TK-001", "TK-002"])
            self.assertEqual(graph["owned_area_overlaps"][0]["tickets"], ["TK-001", "TK-002"])

            second = directory / "tickets" / "TK-002-invalid.md"
            second.write_text(second.read_text(encoding="utf-8").replace("requires: [TK-001]", "requires: [TK-002]"), encoding="utf-8")
            _, cycle = invoke("graph", "--project", str(project), "--effort", directory.name, expected_code=1)
            self.assertFalse(cycle["ok"])
            self.assertTrue(any("cycle" in error for error in cycle["errors"]))

    def test_generated_views_are_idempotent_and_guard_user_edits(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-test-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            write_text(
                project / "roadmap.md",
                """
                | Candidate | Outcome/hypothesis | Depends on | Priority | State | Promoted effort |
                | --- | --- | --- | --- | --- | --- |
                | CAND-004 | Improve reporting | — | P1 | candidate | — |
                """,
            )
            invoke("render", "--project", str(project), "--effort", directory.name, "--view", "all")
            todo = directory / "todo.md"
            backlog = project / "backlog.md"
            self.assertIn("`CAND-004`", backlog.read_text(encoding="utf-8"))
            self.assertNotIn("CAND-004", todo.read_text(encoding="utf-8"))
            first_hash = hashlib.sha256(todo.read_bytes()).hexdigest()
            _, second_render = invoke("render", "--project", str(project), "--effort", directory.name, "--view", "all")
            self.assertEqual(second_render["changed"], [])
            self.assertEqual(first_hash, hashlib.sha256(todo.read_bytes()).hexdigest())
            todo.write_text(todo.read_text(encoding="utf-8") + "\nmanual note\n", encoding="utf-8")
            _, conflict = invoke("render", "--project", str(project), "--effort", directory.name, "--view", "todo", expected_code=2)
            self.assertEqual(conflict["error"], "write_conflict")

    def test_compact_keeps_tasks_in_change_and_supports_inline_evidence_record(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-compact-") as raw:
            project = Path(raw)
            invoke("init", "--project", str(project), "--mode", "compact")
            invoke("scaffold", "--project", str(project), "--effort", "002-small", "--mode", "compact")
            directory = project / "specs" / "002-small"
            change = directory / "change.md"
            change.write_text(
                change.read_text(encoding="utf-8").replace(
                    "- **FR-001** — [comportamento aceito]",
                    "- **FR-001** — o total não fica negativo",
                ).replace(
                    "- **AC-001** — Dado [estado], quando [ação], então [resultado literal independente].",
                    "- **AC-001** — Dado 1000 e desconto 1200, então o resultado é 0.",
                ),
                encoding="utf-8",
            )
            _, compact_validate = invoke("validate", "--project", str(project), "--effort", directory.name)
            self.assertTrue(compact_validate["ok"], compact_validate)
            _, render_error = invoke("render", "--project", str(project), "--effort", directory.name, "--view", "todo", expected_code=2)
            self.assertEqual(render_error["error"], "compact_projection")
            self.assertFalse((directory / "todo.md").exists())
            _, evidence = invoke(
                "evidence", "add", "--project", str(project), "--effort", directory.name,
                "--acceptance-refs", "AC-001", "--procedure", "python -m unittest",
                "--result", "not_run", "--limitations", "ambiente não disponível",
            )
            self.assertIsNone(evidence.get("ticket"))
            stored = json.loads((directory / "evidence" / "EV-001.json").read_text(encoding="utf-8"))
            self.assertIsNone(stored["ticket"])

    def test_contract_revision_invalidates_dependent_evidence_and_ticket(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-contract-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            write_text(project / "src" / "demo.py", "def public_function():\n    return 7")
            _, evidence = invoke(
                "evidence", "add", "--project", str(project), "--effort", directory.name,
                "--ticket", "TK-001", "--acceptance-refs", "AC-001", "--procedure", "python -m unittest",
                "--result", "passed", "--executed", "--path", "src", "--observations", "7",
            )
            invoke(
                "ticket", "update", "--project", str(project), "--effort", directory.name,
                "--ticket", "TK-001", "--status", "done", "--verification-status", "passed", "--review", "passed",
            )
            contract = directory / "spec.md"
            contract.write_text(
                contract.read_text(encoding="utf-8").replace("revision: 1", "revision: 2").replace(
                    "return 7", "return 8"),
                encoding="utf-8",
            )
            _, gate = invoke(
                "ticket", "update", "--project", str(project), "--effort", directory.name,
                "--ticket", "TK-001", "--status", "done", "--verification-status", "passed",
                expected_code=2,
            )
            self.assertEqual(gate["error"], "ticket_gate")
            _, invalidated = invoke("invalidate", "--project", str(project), "--effort", directory.name, "--write")
            self.assertEqual(invalidated["stale_evidence"], [evidence["evidence"]])
            self.assertEqual(invalidated["updated_tickets"], ["TK-001"])
            stored_ticket = next((directory / "tickets").glob("TK-001*.md")).read_text(encoding="utf-8")
            self.assertIn("status: in_progress", stored_ticket)
            _, invalidated_again = invoke("invalidate", "--project", str(project), "--effort", directory.name)
            self.assertEqual(invalidated_again["stale_evidence"], [])

    def test_checkpoint_uses_atomic_revision_guard(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-test-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            invoke(
                "checkpoint", "write", "--project", str(project), "--effort", directory.name,
                "--expected-revision", "0", "--phase", "implementation", "--next-action", "run AC-001",
                "--input", "plan=specs/001-demo/plan.md",
            )
            _, conflict = invoke("checkpoint", "write", "--project", str(project), "--effort", directory.name, "--expected-revision", "0", "--next-action", "stale writer", expected_code=2)
            self.assertEqual(conflict["error"], "checkpoint_conflict")
            state = json.loads((directory / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["revision"], 1)
            self.assertEqual(state["next_action"], "run AC-001")
            self.assertEqual(state["inputs"]["plan"]["revision"], 1)

    def test_evidence_fingerprint_becomes_stale_after_code_change(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-test-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            _, missing_path = invoke(
                "evidence", "add", "--project", str(project), "--effort", directory.name,
                "--ticket", "TK-001", "--acceptance-refs", "AC-001", "--procedure", "python -m unittest",
                "--result", "passed", "--executed", expected_code=2,
            )
            self.assertEqual(missing_path["error"], "evidence_input")
            code = project / "src" / "demo.py"
            write_text(code, "def public_function():\n    return 7")
            _, evidence = invoke(
                "evidence", "add", "--project", str(project), "--effort", directory.name,
                "--ticket", "TK-001", "--acceptance-refs", "AC-001", "--procedure", "python -m unittest",
                "--result", "passed", "--executed", "--path", "src", "--observations", "7",
            )
            self.assertEqual(evidence["result"], "passed")
            code.write_text(code.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")
            _, invalidated = invoke("invalidate", "--project", str(project), "--effort", directory.name, "--write")
            self.assertEqual(invalidated["stale_evidence"], [evidence["evidence"]])
            stored = json.loads((directory / "evidence" / f"{evidence['evidence']}.json").read_text(encoding="utf-8"))
            self.assertEqual(stored["result"], "stale")
            state = json.loads((directory / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["revision"], 1)
            self.assertEqual(state["last_invalidation"]["evidence"], [evidence["evidence"]])

    def test_finding_add_is_deduplicated(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-test-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            arguments = (
                "finding", "add", "--project", str(project), "--effort", directory.name,
                "--origin", "convergence", "--source-ref", "AC-001", "--gap-type", "missing-evidence",
                "--area", "src", "--severity", "blocker", "--summary", "AC-001 lacks evidence",
            )
            _, first = invoke(*arguments)
            _, second = invoke(*arguments)
            self.assertTrue(first["created"])
            self.assertTrue(second["deduplicated"])
            self.assertEqual(len(list((directory / "findings").glob("FD-*.json"))), 1)

    def test_consistency_finds_acceptance_without_ticket(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-test-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            _, result = invoke("check", "--project", str(project), "--effort", directory.name, "--mode", "consistency")
            self.assertTrue(any(item["gap_type"] == "acceptance_without_ticket" for item in result["findings"]))

    def test_convergence_finds_acceptance_without_current_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-convergence-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            _, result = invoke("check", "--project", str(project), "--effort", directory.name, "--mode", "convergence")
            missing = {item["source_ref"] for item in result["findings"] if item["gap_type"] == "acceptance_without_current_pass"}
            self.assertEqual(missing, {"AC-001", "AC-002"})

    def test_ready_ticket_can_be_passed_as_execution_package(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-test-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            invoke(
                "checkpoint", "write", "--project", str(project), "--effort", directory.name,
                "--expected-revision", "0", "--input", "contract=specs/001-demo/spec.md",
                "--input", "plan=specs/001-demo/plan.md",
            )
            _, result = invoke("package", "--project", str(project), "--effort", directory.name, "--ticket", "TK-001")
            self.assertTrue(result["package"]["ready"], result)
            self.assertEqual(result["package"]["objective_and_limits"]["acceptance_refs"], ["AC-001"])
            self.assertIn("TK-001.1", result["package"]["sequence"])
            self.assertIn("Return", result["package"]["return_condition"])

    def test_execution_package_requires_accepted_contract_and_ready_plan(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-package-gate-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            invoke(
                "checkpoint", "write", "--project", str(project), "--effort", directory.name,
                "--expected-revision", "0", "--input", "contract=specs/001-demo/spec.md",
                "--input", "plan=specs/001-demo/plan.md",
            )
            plan = directory / "plan.md"
            plan.write_text(plan.read_text(encoding="utf-8").replace("status: ready", "status: draft"), encoding="utf-8")
            _, result = invoke(
                "package", "--project", str(project), "--effort", directory.name,
                "--ticket", "TK-001", expected_code=1,
            )
            self.assertFalse(result["package"]["ready"])
            self.assertIn("plan.md must have status=ready before a ticket is ready", result["package"]["errors"])

    def test_done_and_todo_require_current_passed_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-test-") as raw:
            project = Path(raw)
            directory = write_standard_effort(project)
            write_text(project / "src" / "demo.py", "def public_function():\n    return 7")
            invoke(
                "evidence", "add", "--project", str(project), "--effort", directory.name,
                "--ticket", "TK-001", "--acceptance-refs", "AC-001", "--procedure", "python -m unittest",
                "--result", "passed", "--executed", "--path", "src", "--observations", "7",
            )
            invoke(
                "ticket", "update", "--project", str(project), "--effort", directory.name,
                "--ticket", "TK-001", "--status", "done", "--verification-status", "passed", "--review", "passed",
            )
            invoke("render", "--project", str(project), "--effort", directory.name, "--view", "todo")
            self.assertIn("## [x] TK-001", (directory / "todo.md").read_text(encoding="utf-8"))
            invoke("render", "--project", str(project), "--effort", directory.name, "--view", "backlog")
            backlog = (project / "backlog.md").read_text(encoding="utf-8")
            self.assertIn("`001-demo`", backlog)
            self.assertIn("`active`", backlog)
            self.assertIn("`1/1`", backlog)

    def test_install_copies_native_skills_and_shared_resources(self) -> None:
        with tempfile.TemporaryDirectory(prefix="hybrid-install-") as raw:
            project = Path(raw)
            _, result = invoke("install", "--project", str(project))
            self.assertEqual(result["skill_root"], ".agents/skills")
            self.assertTrue((project / ".agents" / "skills" / "hybrid-start" / "SKILL.md").exists())
            self.assertTrue((project / ".agents" / "shared" / "references" / "vocabulary.md").exists())
            self.assertTrue((project / ".hybrid" / "hybrid.py").exists())
            installed_check = subprocess.run(
                [sys.executable, str(project / ".hybrid" / "hybrid.py"), "package-validate", "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(installed_check.returncode, 0, installed_check.stderr)
            self.assertTrue(json.loads(installed_check.stdout)["ok"])
            installed = project / ".agents" / "skills" / "hybrid-start" / "SKILL.md"
            installed.write_text(installed.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
            _, conflict = invoke("install", "--project", str(project), expected_code=2)
            self.assertEqual(conflict["error"], "install_conflict")
            outside = project.parent / "hybrid-install-outside"
            _, unsafe = invoke(
                "install", "--project", str(project), "--skill-root", str(outside), expected_code=2,
            )
            self.assertEqual(unsafe["error"], "unsafe_path")

    def test_evaluation_manifest_has_all_cases_and_explicit_tracker_state(self) -> None:
        cases = json.loads((PACKAGE / "examples" / "evaluation" / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual([case["id"] for case in cases], [f"E{number:02d}" for number in range(1, 32)])
        tracker_case = next(case for case in cases if case["id"] == "E20")
        self.assertEqual(tracker_case["deterministic"], "not_applicable")
        self.assertEqual(tracker_case["behavioral"], "not_applicable")
        for case in cases:
            self.assertIn("expected", case)
            self.assertIn("procedure", case)
            self.assertIn("behavioral", case)


if __name__ == "__main__":
    unittest.main()
