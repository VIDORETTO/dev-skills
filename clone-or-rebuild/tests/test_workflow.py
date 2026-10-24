"""Unittests for the portable, offline tool helpers."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / 'scripts' / name
    spec = importlib.util.spec_from_file_location(name.removesuffix('.py'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


triage = load_script('triage.py')
compare = load_script('compare_jsonl.py')
validator = load_script('validate_skill.py')


class TriageTests(unittest.TestCase):
    def test_no_authorization_stops_even_with_complete_source(self):
        result = triage.recommend('complete', 'repo', 'yes', 'no')
        self.assertEqual(result['route'], 'STOP')

    def test_unknown_authorization_plan_only(self):
        self.assertEqual(triage.recommend('none', 'native', 'yes', 'unknown')['route'], 'PLAN_ONLY')

    def test_reuse_beats_unnecessary_re(self):
        self.assertEqual(triage.recommend('none', 'files', 'yes', 'yes', oss='yes')['route'], 'REUSE')

    def test_complete_source_routes_source_first(self):
        self.assertEqual(triage.recommend('complete', 'electron', 'yes', 'yes')['route'], 'SOURCE_FIRST')

    def test_no_source_native_starts_with_oracle(self):
        self.assertEqual(triage.recommend('none', 'native', 'yes', 'yes')['route'], 'BLACK_BOX_THEN_FOCUSED_RE')

    def test_visual_web_uses_browser_tools(self):
        result = triage.recommend('none', 'web', 'yes', 'yes', goal='visual')
        self.assertEqual(result['route'], 'VISUAL_BLACK_BOX')
        self.assertIn('Playwright', result['initial_tools'])


class ComparatorTests(unittest.TestCase):
    def test_structural_comparison(self):
        self.assertEqual(compare.differences({'a': [1, 2]}, {'a': [1, 2.0]}), [])
        self.assertEqual(len(compare.differences({'a': [1]}, {'a': [2]})), 1)

    def test_bools_are_not_numbers(self):
        self.assertNotEqual(compare.differences(True, 1), [])

    def test_tolerance(self):
        self.assertEqual(compare.differences({'x': 0.3}, {'x': 0.30001}, tolerance=.001), [])
        self.assertNotEqual(compare.differences({'x': 0.3}, {'x': 0.30001}, tolerance=.000001), [])

    def test_jsonl_comparison_and_missing_lines(self):
        with tempfile.TemporaryDirectory() as temp:
            p, q = Path(temp)/'ref.jsonl', Path(temp)/'test.jsonl'
            p.write_text('{"x":1}\n{"y":2}\n', encoding='utf-8')
            q.write_text('{"x":1}\n', encoding='utf-8')
            result = compare.compare_files(p, q)
            self.assertEqual(result['matching_lines'], 1)
            self.assertEqual(result['total_lines'], 2)
            self.assertFalse(result['passed'])

    def test_identical_jsonl_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            p, q = Path(temp)/'ref.jsonl', Path(temp)/'test.jsonl'
            p.write_text('{"x":1,"y":true}\n', encoding='utf-8')
            q.write_text('{"y":true,"x":1}\n', encoding='utf-8')
            self.assertTrue(compare.compare_files(p, q)['passed'])


class ValidatorTests(unittest.TestCase):
    def test_complete_package(self):
        self.assertEqual(validator.validate(ROOT), [])

    def test_invalid_package(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertTrue(validator.validate(Path(temp)))


if __name__ == '__main__':
    unittest.main()
