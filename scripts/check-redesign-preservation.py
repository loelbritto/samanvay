"""Read-only comparison of synthetic records and source files across a UI redesign."""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/evidence' / (sys.argv[2] if len(sys.argv) > 2 else 'redesign-20261028')
if OUT.resolve().parent != (ROOT / 'docs/evidence').resolve():
    raise SystemExit('Evidence run must be a single directory name')
TABLES = ['cases', 'original_submissions', 'assignment_history', 'workflow_events',
          'case_actions', 'resolutions', 'transfers', 'identity_decisions',
          'coordination_groups', 'coordination_reviews', 'relationship_suggestions',
          'relationship_decisions']

def digest(value):
    return hashlib.sha256(value).hexdigest()

def capture():
    contexts = {}
    for directory in [ROOT / '.local-data', ROOT / '.demo-contexts/demo-5f5a439bfd2ea5ede367507b']:
        connection = sqlite3.connect((directory / 'samanvay.sqlite3').as_uri() + '?mode=ro', uri=True)
        connection.execute('BEGIN')
        tables = {}
        for table in TABLES:
            rows = sorted(connection.execute('SELECT * FROM ' + table).fetchall(), key=repr)
            tables[table] = {'count': len(rows), 'sha256': digest(json.dumps(rows, default=str).encode())}
        connection.close()
        files = {p.relative_to(directory).as_posix(): digest(p.read_bytes())
                 for p in (directory / 'private-evidence').rglob('*') if p.is_file()}
        contexts[directory.relative_to(ROOT).as_posix()] = {'tables': tables, 'evidence': files}
    sources = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
               for folder in ['frontend/src', 'backend/app'] for p in (ROOT / folder).rglob('*')
               if p.is_file() and '__pycache__' not in p.parts}
    return {'contexts': contexts, 'sources': sources}

OUT.mkdir(parents=True, exist_ok=True)
phase = sys.argv[1]
snapshot = capture()
target = OUT / (phase + '.json')
if phase == 'before' and target.exists():
    raise SystemExit('Baseline already exists; preserving it')
target.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')
if phase == 'after':
    before = json.loads((OUT / 'before.json').read_text())
    result = {'records_and_private_bytes_unchanged': before['contexts'] == snapshot['contexts'],
              'changed_sources': [p for p, h in snapshot['sources'].items() if before['sources'].get(p) != h],
              'removed_sources': sorted(set(before['sources']) - set(snapshot['sources']))}
    (OUT / 'preservation-result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    if not result['records_and_private_bytes_unchanged']:
        raise SystemExit(1)
else:
    print('Captured read-only baseline for two synthetic contexts and source hashes.')
