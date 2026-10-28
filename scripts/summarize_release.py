"""Verify existing release evidence, reconcile requirement status and hash the actual build."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from capture_requirements import GATES

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence/stage9'


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))


def main():
    suite=ET.parse(ROOT/'docs/evidence/stage9-final-tests.xml').getroot().find('testsuite')
    follow=ET.parse(ROOT/'docs/evidence/stage9-print-tests.xml').getroot().find('testsuite')
    assert int(suite.attrib['tests'])==72 and int(suite.attrib['failures'])==int(suite.attrib['errors'])==0
    assert int(follow.attrib['tests'])==7 and int(follow.attrib['failures'])==int(follow.attrib['errors'])==0
    checkpoint=read('docs/evidence/stage2/results.json')
    assert checkpoint['stage1_ready'] and checkpoint['stage2_ready']
    restarted=read('docs/evidence/stage9/after-restart.json')
    repeat=read('docs/evidence/stage9/repeat-recovery.json')
    clean=read('docs/evidence/stage9/clean-dependencies.json')
    browser=read('docs/evidence/stage9/browser-final.json')
    assert restarted['passed'] and restarted['matches_before_restart'] and restarted['case_count']==8
    assert repeat['passed'] and repeat['all_source_records_unchanged'] and repeat['restored_private_files_verified']
    assert clean['passed'] and browser['passed']
    before=read('docs/evidence/stage9/service-processes-before.json')
    after=read('docs/evidence/stage9/service-processes-after.json')
    # Before capture includes command provenance; after records listeners of the new owned services.
    def pid_for(rows,port):
        return next(r.get('process_id',r.get('pid',r.get('OwningProcess'))) for r in rows if int(r.get('port',r.get('LocalPort',0)))==port)
    assert all(pid_for(before,p)!=pid_for(after,p) for p in [8001,5174])
    latest=read('docs/evidence/stage8/latest.json');evaluation=read(latest['summary'])
    assert evaluation['classification']['n']==168 and evaluation['identity_matching']['n']==98
    for file,digest in evaluation['source_sha256'].items():
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest
    summary={'release':'samanvay-local-20261027','observed_at_utc':datetime.now(timezone.utc).isoformat(),
        'technical_gates_passed':True,'stages':{str(i):'bounded local technical gate passed' for i in range(1,10)},
        'full_backend_tests':72,'print_followup_tests':7,'dependency_warning':'Starlette TestClient/httpx deprecation',
        'actual_api_ui_restart':True,'browser_case_count':8,'original_context_case_count':5,'management_csv_count':7,
        'automated_second_rehearsal':True,'actual_backup_restore':True,'records_deleted':0,
        'fresh_dependencies_verified':True,'browser_observations':len(browser['checks']),
        'native_200_percent_evidence':'docs/evidence/stage1-zoom/results.json',
        'evaluation_summary':latest['summary'],'live_semantic_service':False,'selected_method':'baseline',
        'independent_human_review_performed':False,'three_minute_timed_run_verified':False,'official_scope_verified':False,
        'remaining_limits':'PROJECT_STATE.md; docs/BACKEND_GAPS.md; docs/evidence/stage9/human-feedback.json'}
    (E/'release-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')

    mapping=read('docs/requirement-map.json');progress={}
    partial={1:'Official identifier/year/text remain unverified.',16:'Separately cited original brief is missing; two supplied sources are completely inventoried.',
             17:'Official round/template not supplied; outline provisional.',22:'Agent technical inspection passed; first-time human comprehension is not measured.',
             67:'Frozen split audit passed; independent difficult-label review is unperformed.',
             69:'All fourteen bounded technical scenarios exercised; semantic evidence uses validated baseline/disabled-adapter tests, not a live semantic model. Formal exhaustive usability is not established.',
             74:'Observable browser and automated rehearsal passed; approximately three-minute narration is a target, not measured runtime.',
             76:'Q&A prepared; unfamiliar teammate comprehension requested but user delegated choices, so human study is unperformed.'}
    for item in mapping['requirements']:
        stage=max(item['stages']);line=item['line']
        evidence='docs/ACCEPTANCE.md; docs/PHASES_3_TO_9.md; docs/evidence/stage9/release-summary.json'
        if stage==0:evidence='PLAN.md; DECISIONS.md; docs/source-snapshot.json; source-coverage audit'
        progress[item['id']]={'status':'partially_verified' if line in partial else 'specified' if stage==0 else f'verified_stage{stage}',
            'implementation_location':'; '.join(dict.fromkeys(GATES[s][1] for s in item['stages'])),
            'evidence':evidence+('; '+partial[line] if line in partial else '; Local technical scope only. External/human/production limits: PROJECT_STATE.md.')}
    for item in mapping['guide_sections']:
        progress[item['id']]={'status':'reference_mapped','implementation_location':'; '.join(dict.fromkeys(GATES[s][1] for s in item['stages'])),
            'evidence':'Exact source paragraphs retained in docs/source-snapshot.json; implemented proposals/evidence: docs/ACCEPTANCE.md, MODULE_GUIDE.md, DEMO_RUNBOOK.md; official/human/production limits in PROJECT_STATE.md. Reference mapping is not a claim that contextual prose is a completed mandatory feature.'}
    (ROOT/'docs/requirement-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    files=[]
    for base in ['backend/app','backend/migrations','backend/tests','frontend/src','evaluation','scripts']:
        for p in (ROOT/base).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc'}:files.append(p)
    files += [ROOT/p for p in ['.env.example','.gitignore','backend/requirements.in','backend/requirements.lock',
        'backend/alembic.ini','frontend/package.json','frontend/package-lock.json','frontend/tsconfig.json','frontend/vite.config.ts','frontend/index.html']]
    files += [p for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()]
    captures=[p for p in E.iterdir() if p.suffix=='.png']
    manifest={'release':summary['release'],'capture_date':'2026-10-27','timezone':'Asia/Kolkata','git_commit':None,
        'source_build_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},
        'actual_capture_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(captures)},
        'private_data_included':False,'capture_notice':'Actual synthetic build. Some business dates are Nov1 due to isolated clock; host capture date is Oct27.'}
    (E/'release-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))


if __name__=='__main__':main()
