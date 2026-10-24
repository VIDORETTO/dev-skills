#!/usr/bin/env python3
"""Basic offline package validator (stdlib only).

Checks the Agent Skills identity and local file references; not a substitute
for `skills-ref validate` when available.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED = [
    'README.md',
    'references/grill-me.md', 'references/decision-engine.md',
    'references/tool-routing.md', 'references/evidence-and-tests.md',
    'references/quality-gates.md', 'references/safety-and-rights.md',
    'references/agent-roles.md', 'references/sources.md',
    'scripts/triage.py', 'scripts/compare_jsonl.py',
    'assets/templates/decision-record.md', 'examples/01-migracao-com-fonte.md',
]


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skill = root / 'SKILL.md'
    if not skill.is_file():
        return ['Missing SKILL.md']
    contents = skill.read_text(encoding='utf-8')
    match = re.match(r'\A---\r?\n(.*?)\r?\n---\r?\n', contents, flags=re.DOTALL)
    if not match:
        return ['Missing YAML frontmatter (--- block)']
    front = match.group(1)
    name_match = re.search(r'^name:\s*([\w-]+)\s*$', front, flags=re.MULTILINE)
    if not name_match:
        errors.append('Missing frontmatter name')
    else:
        name = name_match.group(1)
        if len(name) > 64 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            errors.append(f'Invalid Agent Skills name: {name}')
        if root.name != name:
            errors.append(f'Folder ({root.name}) must equal skill name ({name})')
    if not re.search(r'^description:\s*(?:>|\||\S)', front, flags=re.MULTILINE):
        errors.append('Missing frontmatter description')
    for filename in REQUIRED:
        if not (root / filename).is_file():
            errors.append(f'Missing packaged file: {filename}')
    for reference in set(re.findall(r'(?:references|assets/templates|examples|scripts)/[a-zA-Z0-9_./-]+(?:\.md|\.csv|\.py)', contents)):
        if not (root / reference).is_file():
            errors.append(f'Broken relative reference in SKILL.md: {reference}')
    if len(contents.splitlines()) >= 500:
        errors.append('SKILL.md >= 500 lines; split details into references')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, nargs='?', default=Path.cwd())
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for problem in errors:
            print('ERROR:', problem, file=sys.stderr)
        return 1
    print(f'OK: {args.root.resolve()} contains a valid basic Agent Skills package')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
