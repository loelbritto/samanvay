"""Save current brand-pass evidence and status without modifying business state."""
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/evidence/brand-redesign-20261028'
before = json.loads((OUT/'before.json').read_text(encoding='utf-8'))
after = json.loads((OUT/'after.json').read_text(encoding='utf-8'))
preservation = json.loads((OUT/'preservation-result.json').read_text(encoding='utf-8'))
backend_unchanged = {k:v for k,v in before['sources'].items() if k.startswith('backend/')} == {k:v for k,v in after['sources'].items() if k.startswith('backend/')}
contrast = json.loads((OUT/'contrast.json').read_text(encoding='utf-8'))
assert preservation['records_and_private_bytes_unchanged'] and backend_unchanged and contrast['passed']
test_log = (OUT/'frontend-tests.txt').read_text(encoding='utf-8-sig')
build_log = (OUT/'build.txt').read_text(encoding='utf-8-sig')
assert re.search(r'\bpass 18\b', test_log) and re.search(r'\bfail 0\b', test_log)
assert 'built in' in build_log
assets = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'frontend/public/brand').rglob('*') if p.is_file()}
verification = {'records_and_private_bytes_unchanged': True, 'backend_source_unchanged': backend_unchanged,
 'frontend_tests': {'passed':18,'failed':0,'evidence':'frontend-tests.txt'},
 'static_colour_pairs_passed':len(contrast['pairs']), 'build_evidence':'build.txt',
 'browser': {'verified':False,'reason':'Previously observed saved origin policy remains unresolved; no workaround or unchanged-state retry.'},
 'source_review':'No outstanding P1/P2 after institution-selection and focus fixes; not visual acceptance.',
 'logo_validation':json.loads((ROOT/'frontend/public/brand/asset-validation.json').read_text(encoding='utf-8'))}
(OUT/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
additional = ['frontend/package.json','frontend/package-lock.json','frontend/index.html',
 'frontend/tests/connections.test.ts','frontend/tests/queue-model.test.ts',
 'scripts/redesign-brand.py','scripts/check-redesign-contrast.py','scripts/finalize-brand-evidence.py',
 'DESIGN.md','.impeccable/design.json','.impeccable/surface-brief.md',
 'docs/BRAND_IDENTITY_20261028.md','docs/BRAND_REDESIGN_20261028.md',
 'PROJECT_STATE.md','README.md','PLAN.md','docs/ACCEPTANCE.md','docs/MODULE_GUIDE.md']
(OUT/'changed-files.json').write_text(json.dumps({'source_comparison':preservation,'additional_changed_files':additional,'brand_assets_sha256':assets},indent=2),encoding='utf-8')
summary = '''**Current: 28 October 2026 identity and workspace revision.** Custom two-part S logo, six vector concepts, outlined Manrope wordmarks, self-hosted type, warm ivory/teal interface, earliest-due case focus and an interactive view of saved shared institution plans are implemented. Compact/full selection and focus handling were corrected in source review. Build and 18 frontend tests passed; 20 static colour pairs passed. Existing complaint/domain records and private bytes are unchanged, as are backend source hashes. No backend regression rerun or browser result is claimed for this frontend-only pass.'''
gate = '''**Browser acceptance is OPEN.** Saved origin policy remains unresolved; current desktop/mobile/supporting-screen rendering, keyboard flow and actual 200% zoom remain unverified. Next: restore effective tool access, capture and review the live screens, then rehearse mutations in a separate synthetic context. Previous browser results are historical. The prototype remains synthetic, with no official integration or SIH judging claim.'''
def replace_intro(file, marker, heading, link):
    path=ROOT/file
    text=path.read_text(encoding='utf-8')
    path.write_text(heading+'\n\n'+summary+'\n\n'+gate+'\n\n'+link+'\n\n'+text[text.index(marker):],encoding='utf-8')
replace_intro('PROJECT_STATE.md','Release `samanvay-local-20261027`','# Project state','[Current changes and evidence](docs/BRAND_REDESIGN_20261028.md) · [Architecture revision](docs/ARCHITECTURE_REDESIGN_20261028.md) · [Design system](DESIGN.md).')
replace_intro('README.md','Student prototype for institution','# Samanvay','[Current report](docs/BRAND_REDESIGN_20261028.md) · [Logo concepts and assets](docs/BRAND_IDENTITY_20261028.md).')
replace_intro('PLAN.md','Stages1–9 local technical gates passed','# Execution status','See docs/BRAND_REDESIGN_20261028.md. The plan below describes the historical release.')
replace_intro('docs/ACCEPTANCE.md','All fourteen scenarios below','# Acceptance gates and evidence','[Current report](BRAND_REDESIGN_20261028.md).')
path=ROOT/'docs/MODULE_GUIDE.md'
text=path.read_text(encoding='utf-8')
addition='''Current brand pass: `shared/Brand.tsx` owns the custom mark; `design-system/desk.css` owns task-focus and brand components; `features/workspace/InstitutionConnections.tsx` and `connection-model.ts` present authorised saved institution plans without changing ownership. `FocusCase.tsx` uses the supplied context clock. `app/WorkspaceBoundary.tsx` provides load/render recovery. Logo exports and concept gallery are in `frontend/public/brand/`. See [current report](BRAND_REDESIGN_20261028.md).'''
if addition not in text:
    path.write_text(text.replace('# Module and data-flow guide\n','# Module and data-flow guide\n\n'+addition+'\n',1),encoding='utf-8')
print(json.dumps({'records_preserved':True,'backend_unchanged':backend_unchanged,'static_pairs':len(contrast['pairs']),'brand_files':len(assets),'source_changes':len(preservation['changed_sources'])},indent=2))
