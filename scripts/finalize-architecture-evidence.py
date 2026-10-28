"""Reconcile this revision's observed checks and documentation, never application data."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/evidence/architecture-redesign-20261028'


def intro(name, marker, replacement):
    path = ROOT / name
    source = path.read_text(encoding='utf-8')
    path.write_text(replacement.rstrip() + '\n\n' + source[source.index(marker):], encoding='utf-8')


current = '''The live app now has a token-based officer workspace, a scoped queue over all authorised cases, separate session/shell/routes and feature pages, plus pure case-action decisions and a transactional repository adapter. Build passed (50 modules), 13 frontend tests passed, 91 full backend tests passed, and 24 overlapping follow-up checks passed after fixing daytime deadline projection. One Starlette/httpx deprecation warning remains. All 16 selected static colour pairs passed. Existing complaint/domain records and private bytes are unchanged. The API restarted in the same eight-case context; listeners are on 5174/8001.'''
gate = '''**Browser acceptance remains OPEN.** Automatic review still denies the origin after renewed user approval and a reported permission change. Current desktop/mobile/supporting-screen/keyboard/actual 200% zoom and UI write-rehearsal results are not claimed. Independent finish reviewer: **recapture**. This revision is not ready to close the visual acceptance gate. The 27 October browser evidence and the earlier 28 October interface report are historical.'''
intro('PROJECT_STATE.md', 'Release `samanvay-local-20261027`', '# Project state\n\n**Current: 28 October 2026 architecture and interface revision.**\n\n' + current + '\n\n' + gate + '\n\nSee [current report](docs/ARCHITECTURE_REDESIGN_20261028.md), [product context](PRODUCT.md), [design system](DESIGN.md) and [earlier report](docs/REDESIGN_20261028.md).')
intro('README.md', 'Student prototype for institution', '# Samanvay\n\n**28 October architecture and UI update:** ' + current + '\n\n' + gate + '\n\n[Implementation, commands and next phase](docs/ARCHITECTURE_REDESIGN_20261028.md) · [Design system](DESIGN.md).')
intro('PLAN.md', 'Stages1–9 local technical gates passed', '# Execution status\n\n' + current + '\n\n' + gate + '\n\nNext: restore effective browser permission, capture current desktop/mobile layouts, verify supporting screens and keyboard/200% flows, then rehearse writes in a separate synthetic context. See docs/ARCHITECTURE_REDESIGN_20261028.md. The plan below describes the historical release.')
intro('docs/ACCEPTANCE.md', 'All fourteen scenarios below', '# Acceptance gates and evidence\n\n**Current architecture/interface revision, 28 October 2026:** ' + current + '\n\n' + gate + '\n\nSee [current report](ARCHITECTURE_REDESIGN_20261028.md).')
intro('docs/MODULE_GUIDE.md', 'Release samanvay-local-20261027.', '''# Module and data-flow guide

Current architecture: [28 October report](ARCHITECTURE_REDESIGN_20261028.md). Live session/navigation/shell are in `frontend/src/app/`; case and institution pages are in `features/`; primitives/resource hooks are in `shared/`; `design-system/` owns live tokens/CSS. `screens/LiveScreens.tsx` is a compatibility export file. The static preview loads independently.

`backend/app/domain/case_actions.py` owns pure decisions; `application/case_actions.py` owns the use case and repository port; `infrastructure/case_actions.py` owns SQL persistence. `case_views.py` projects authorised responses; `workspace.py` selects the queue before display pagination. Existing transfer/coordination/reporting services remain in place. The table and browser observations below describe the earlier release.''')
intro('docs/BACKEND_GAPS.md', 'The persistent workspace implements', '''# Current limitations after local Stages 1–9

28 October architecture update: case actions now have separate domain, application and SQL adapter boundaries; the queue covers the full authorised population before limiting display. Transfer, identity, scheduling, matching and reporting retain their existing service modules. This is an incremental modular-monolith refactor, not a completed production architecture migration. Current browser acceptance is OPEN because saved origin policy still blocks inspection. The historical browser checks below do not validate the new interface. See [current report](ARCHITECTURE_REDESIGN_20261028.md).''')

preservation = json.loads((OUT / 'preservation-result.json').read_text())
extras = ['PRODUCT.md', 'DESIGN.md', '.impeccable/design.json', '.impeccable/surface-brief.md',
          'PROJECT_STATE.md', 'PLAN.md', 'README.md', 'frontend/package.json',
          'frontend/tests/api.test.ts', 'frontend/tests/navigation.test.ts', 'backend/tests/test_architecture.py',
          'scripts/check-redesign-contrast.py', 'scripts/check-redesign-preservation.py',
          'scripts/refactor-architecture.py', 'scripts/refactor-frontend.py', 'scripts/split-feature-pages.py',
          'scripts/finalize-architecture-evidence.py', 'docs/ARCHITECTURE_REDESIGN_20261028.md',
          'docs/ACCEPTANCE.md', 'docs/BACKEND_GAPS.md', 'docs/MODULE_GUIDE.md']
(OUT / 'changed-files.json').write_text(json.dumps({
    'source_hash_comparison': preservation, 'additional_changed_files': extras,
    'evidence_directory': OUT.relative_to(ROOT).as_posix(),
    'note': 'Repository had no tracked initial source commit; source changes are compared with this revision\'s before.json, not inferred from git status.'
}, indent=2), encoding='utf-8')
for filename in ['backend-tests.xml', 'deadline-followup.xml']:
    suite = ET.parse(OUT / filename).getroot().find('testsuite')
    assert suite is not None and suite.get('failures') == '0' and suite.get('errors') == '0', filename
assert preservation['records_and_private_bytes_unchanged']
assert json.loads((OUT / 'contrast.json').read_text())['passed']
json.loads((ROOT / '.impeccable/design.json').read_text(encoding='utf-8'))
print('Reconciled project state, module/acceptance/limitations documents, and changed-file manifest from observed evidence.')
