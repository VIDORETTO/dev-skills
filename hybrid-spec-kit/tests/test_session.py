from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from test_runner import invoke, ticket_text, write_standard_effort, write_text


class SessionTests(unittest.TestCase):
    def fixture(self, project: Path, count: int = 1) -> Path:
        directory = write_standard_effort(project)
        for index in range(2, count + 1):
            write_text(directory / 'tickets' / f'TK-{index:03d}.md',
                       ticket_text(directory.name, f'TK-{index:03d}', [], ['FR-001'], ['AC-001']))
        return directory

    def session(self, project: Path, *arguments: str, code: int = 0) -> dict:
        return invoke('session', '--project', str(project), '--effort', '001-demo',
                      *arguments, expected_code=code)[1]

    def change_state(self, directory: Path, **changes) -> None:
        path = directory / 'state.json'
        state = json.loads(path.read_text())
        state.update(changes)
        path.write_text(json.dumps(state))

    def test_selects_at_most_three_without_mutating_canonical_files(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = self.fixture(project, 5)
            before = {path: path.read_bytes() for path in project.rglob('*') if path.is_file()}
            result = self.session(project)
            self.assertEqual([item['id'] for item in result['selected_tickets']], ['TK-001', 'TK-002', 'TK-003'])
            self.assertFalse(result['readiness_checked'])
            self.assertEqual(result['limits']['planned_compactions'], 0)
            self.assertEqual(before, {path: path.read_bytes() for path in project.rglob('*') if path.is_file()})

    def test_resumes_only_active_work_even_with_other_related_ready_tickets(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = self.fixture(project, 4)
            path = directory / 'tickets/TK-003.md'
            path.write_text(path.read_text().replace('status: ready', 'status: in_progress'))
            self.change_state(directory, active_ticket='TK-003')
            result = self.session(project)
            self.assertEqual([item['id'] for item in result['selected_tickets']], ['TK-003'])

    def test_chain_is_conditional_and_blocked_predecessors_are_never_bypassed(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = write_standard_effort(project, second_ticket=True)
            result = self.session(project)
            self.assertEqual(result['selected_tickets'][1]['requires_selected_done'], ['TK-001'])
            path = directory / 'tickets/TK-001-demo.md'
            path.write_text(path.read_text().replace('status: ready', 'status: blocked'))
            result = self.session(project)
            self.assertEqual(result['selected_tickets'], [])
            self.assertEqual(result['stage'], 'route_checkpoint')

    def test_does_not_mix_unrelated_delivery_areas_or_acceptances(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = self.fixture(project, 2)
            path = directory / 'tickets/TK-002.md'
            path.write_text(path.read_text().replace('acceptance_refs: [AC-001]', 'acceptance_refs: [AC-002]')
                            .replace('owned_areas: [src, tests]', 'owned_areas: [other, other_tests]'))
            self.assertEqual(len(self.session(project)['selected_tickets']), 1)

    def test_requires_accepted_contract_ready_plan_and_active_checkpoint(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = self.fixture(project)
            plan = directory / 'plan.md'
            original = plan.read_text()
            plan.write_text(original.replace('status: ready', 'status: draft'))
            self.assertEqual(self.session(project)['selected_tickets'], [])
            plan.write_text(original)
            spec = directory / 'spec.md'
            original = spec.read_text()
            spec.write_text(original.replace('status: accepted', 'status: draft'))
            self.assertEqual(self.session(project)['selected_tickets'], [])
            spec.write_text(original)
            self.change_state(directory, status='waiting_input')
            result = self.session(project)
            self.assertEqual(result['stage'], 'resolve_checkpoint')
            self.assertEqual(result['selected_tickets'], [])

    def test_done_tickets_route_to_delivery_gates_not_project_completion(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = self.fixture(project)
            path = directory / 'tickets/TK-001-demo.md'
            path.write_text(path.read_text().replace('status: ready', 'status: done'))
            result = self.session(project)
            self.assertEqual(result['stage'], 'delivery_gates')
            self.assertIn('gates finais', result['continuation_prompt'])
            self.assertEqual(json.loads((directory / 'state.json').read_text())['status'], 'active')

    def test_contradictory_completion_routes_to_reconciliation(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = self.fixture(project)
            self.change_state(directory, status='complete')
            self.assertEqual(self.session(project)['stage'], 'reconcile_completion')

    def test_handoff_is_guarded_and_preserves_user_edits_and_state(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = self.fixture(project)
            state_before = (directory / 'state.json').read_bytes()
            result = self.session(project, '--write')
            output = project / result['written']
            self.assertIn(result['continuation_prompt'], output.read_text())
            output.write_text('user handoff notes\n')
            result = self.session(project, '--write', code=2)
            self.assertEqual(result['error'], 'write_conflict')
            self.assertEqual(output.read_text(), 'user handoff notes\n')
            self.assertEqual((directory / 'state.json').read_bytes(), state_before)

    def test_invalid_graph_cannot_generate_handoff(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = self.fixture(project)
            path = directory / 'tickets/TK-001-demo.md'
            path.write_text(path.read_text().replace('requires: []', 'requires: [TK-999]'))
            self.assertEqual(self.session(project, '--write', code=2)['error'], 'invalid_graph')
            self.assertFalse((project / '.hybrid/continuations/001-demo.md').exists())

    def test_small_batch_and_time_override_are_explicit(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            self.fixture(project, 4)
            result = self.session(project, '--max-tickets', '1', '--minutes', '15')
            self.assertEqual(len(result['selected_tickets']), 1)
            self.assertEqual(result['limits']['soft_minutes'], 15)

    def test_ticket_growth_baseline_survives_handoff_and_warns_without_dropping_work(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            directory = self.fixture(project, 2)
            self.session(project, '--write')
            write_text(directory / 'tickets/TK-003.md', ticket_text(directory.name, 'TK-003', [], ['FR-001'], ['AC-001']))
            result = self.session(project, '--write')
            self.assertEqual(result['ticket_growth']['baseline_count'], 2)
            self.assertEqual(result['ticket_growth']['growth_percent'], 50.0)
            self.assertTrue(result['ticket_growth']['requires_reconciliation'])
            self.assertEqual(result['total_tickets'], 3)
            self.assertEqual(self.session(project, '--baseline-tickets', '3', code=2)['error'], 'ticket_baseline_conflict')

    def test_migration_can_record_known_original_ticket_count(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            self.fixture(project, 5)
            result = self.session(project, '--baseline-tickets', '2', '--write')
            self.assertEqual(result['ticket_growth']['baseline_count'], 2)
            self.assertEqual(self.session(project)['ticket_growth']['baseline_count'], 2)

    def test_compact_has_no_ticket_inflation_and_draft_is_not_executable(self):
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            invoke('init', '--project', str(project), '--mode', 'compact')
            invoke('scaffold', '--project', str(project), '--effort', '001-demo', '--mode', 'compact')
            path = project / 'specs/001-demo/change.md'
            self.assertNotEqual(self.session(project)['stage'], 'compact')
            path.write_text(path.read_text().replace('status: draft', 'status: accepted'))
            result = self.session(project)
            self.assertEqual(result['stage'], 'compact')
            self.assertEqual(result['total_tickets'], 0)


if __name__ == '__main__':
    unittest.main()
