"""Automated second rehearsal and actual private snapshot recovery; never delete contexts."""
from datetime import datetime, timezone
import faulthandler
import csv
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from fastapi.testclient import TestClient
from app.api import create_app
from app.coordination import process_domain_one
from app.demo import backup, context_settings, new_context, rehearsal_grants, restore, storage_audit
from app.scheduling import deliver_one, run_scheduler


def signin(client, name):
    response = client.post('/api/auth/login', json={'username': name+'@demo.test', 'password': 'DemoOnly-Stage2!'})
    assert response.status_code == 200, response.text
    return {'X-CSRF-Token': response.json()['csrf_token']}


def snapshot(settings):
    with sqlite3.connect('file:'+(settings.data_dir/'samanvay.sqlite3').as_posix()+'?mode=ro', uri=True) as db:
        return {table: db.execute('SELECT * FROM '+table+' ORDER BY id').fetchall() for table in
                ['cases', 'original_submissions', 'attachments', 'assignment_history', 'workflow_events',
                 'relationship_suggestions', 'relationship_decisions', 'coordination_groups', 'coordination_reviews']}


def main():
    faulthandler.dump_traceback_later(45)
    proof = json.loads((ROOT/'docs/evidence/stage9/ui-rehearsal.json').read_text(encoding='utf-8'))
    source = context_settings(proof['context_id'])
    original = snapshot(source)
    print('Source snapshot read', flush=True)
    archive = backup(source)
    recovered = restore(archive['backup_id'], 'final-recovery-'+uuid.uuid4().hex)
    restored = context_settings(recovered['context_id'])
    assert snapshot(restored) == original
    assert storage_audit(source)['passed'] and storage_audit(restored)['passed']
    print('Backup restored; original rows and private files verified', flush=True)

    run = new_context('repeat-rehearsal-'+uuid.uuid4().hex)
    settings = context_settings(run['context_id'])
    app = create_app(settings)
    created = []
    for index, account in enumerate(['pgrc', 'rb', 'pgrc']):
        print('Creating synthetic repeat record '+str(index), flush=True)
        with TestClient(app) as client:
            headers = signin(client, account)
            payload = {'institution_id': 'DEMO-INST-017', 'original_institution_text': 'DSI Pune — synthetic repeat',
                       'received_date': '2026-10-27', 'expected_disposal_date': '2026-10-30',
                       'subject': 'Synthetic independent faculty wage statement' if index == 2 else 'Synthetic cancellation refund request',
                       'description': 'Synthetic faculty salary statement request' if index == 2 else 'Synthetic admission cancellation refund remains pending',
                       'category': 'Faculty grievance' if index == 2 else 'Fee refund', 'next_action': 'Review synthetic evidence',
                       'complainant_token': 'DEMO-REPEAT-'+str(index), 'synthetic': True,
                       'facts': {'incident_reference': 'INC-REPEAT-FAC' if index == 2 else 'INC-REPEAT-1',
                                 'incident_date': '2026-10-24', 'receipt_reference': 'R-REPEAT-'+str(index),
                                 'remedy': 'salary statement' if index == 2 else 'refund'}}
            response = client.post('/api/cases', headers={**headers, 'Idempotency-Key': uuid.uuid4().hex},
                                   data={'payload': json.dumps(payload)},
                                   files=[('files', ('repeat.txt', b'SYNTHETIC repeat rehearsal evidence only', 'text/plain'))])
            assert response.status_code == 201, response.text
            created.append(response.json())
    print('Three repeat records committed', flush=True)
    while process_domain_one(app.state.sessions) is not None:
        pass
    rehearsal_grants(settings, app.state.sessions, 'Explicit synthetic automated second rehearsal')
    with TestClient(app) as client:
        headers = signin(client, 'coordinator')
        for left, label in [(created[0], 'RELATED'), (created[2], 'INDEPENDENT')]:
            result = client.post('/api/cases/'+created[1]['id']+'/matching', headers=headers,
                                 json={'expected_version': 1, 'method': 'baseline'})
            assert result.status_code == 200, result.text
            row = next(r['review'] for r in result.json()['items'] if {r['review']['left'], r['review']['right']} == {left['id'], created[1]['id']})
            assert row['proposed_label'] == label
            decision = client.post('/api/relationships/'+row['id']+'/decision', headers=headers, json={
                'action': 'CONFIRM', 'label': label, 'expected_version': row['version'], 'left_version': row['left_version'],
                'right_version': row['right_version'], 'fingerprint': row['fingerprint'],
                'reason': 'Synthetic automated exercise of authorised review controls; not independent human annotation'})
            assert decision.status_code == 200, decision.text
        group = client.get('/api/coordination').json()[0]
        lead = next(o['id'] for o in client.get('/api/workflow-targets').json() if o['name'] == 'Demo Meera Das')
        for state in ['IN_REVIEW', 'PLANNED']:
            response = client.post('/api/coordination/'+group['id']+'/review', headers=headers, json={
                'state': state, 'expected_version': group['version'], 'lead_id': lead,
                'next_action': 'Coordinate separate responses; preserve individual case owners', 'reason': 'Synthetic automated second rehearsal plan'})
            assert response.status_code == 200, response.text
            group = response.json()
        assert client.get('/api/identity/lookup', params={'q': 'Demo Suryavan Institute'}).json()['status'] == 'AMBIGUOUS'
    with TestClient(app) as client:
        headers = signin(client, 'admin')
        clock = client.get('/api/settings').json()
        response = client.post('/api/demo/clock', headers=headers, json={'advance_seconds': 432000,
            'expected_version': clock['clock_version'], 'reason': 'Synthetic second rehearsal isolated clock'})
        assert response.status_code == 200, response.text
    run_scheduler(app.state.sessions)
    while deliver_one(app.state.sessions) is not None:
        pass
    with TestClient(app) as client:
        headers = signin(client, 'coordinator')
        notice = next(n for n in client.get('/api/notifications').json() if n['kind'] == 'OVERDUE')
        assert client.post('/api/notifications/'+notice['id']+'/acknowledge', headers=headers).status_code == 200
        cookie = dict(client.cookies)
        before = client.get('/api/coordination').json()
    app.state.engine.dispose()
    restarted = create_app(settings)
    with TestClient(restarted) as client:
        client.cookies.update(cookie)
        assert client.get('/api/coordination').json() == before
        assert client.get('/api/reports').json()['total'] == 7
    with TestClient(restarted) as client:
        signin(client, 'management')
        report = client.get('/api/reports').json()
        export = client.get('/api/reports/csv')
        rows = list(csv.DictReader(io.StringIO(export.content.decode('utf-8-sig'))))
        assert report['total'] == len(rows) == 6 and all(r['subject'] == 'Restricted narrative' for r in rows)
        assert client.get(created[0]['attachments'][0]['download_url']).status_code == 404
    restarted.state.engine.dispose()
    assert snapshot(source) == original
    result = {'passed': True, 'observed_at_utc': datetime.now(timezone.utc).isoformat(),
              'repeat_method': 'FastAPI TestClient plus new application/engine instance; actual service restart is separately evidenced',
              'human_review': 'Automated exercise of fictional authorised controls, not a human study',
              'repeat_context': run['context_id'], 'repeat_case_count': 7, 'created_case_ids': [c['id'] for c in created],
              'metadata_csv_count': 6, 'source_context': source.context_id, 'source_case_count': len(original['cases']),
              'backup_id': archive['backup_id'], 'restored_context': recovered['context_id'],
              'all_source_records_unchanged': True, 'restored_rows_originals_history_identical': True,
              'restored_private_files_verified': True, 'files_or_complaints_deleted': 0}
    (ROOT/'docs/evidence/stage9/repeat-recovery.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))
    faulthandler.cancel_dump_traceback_later()


if __name__ == '__main__':
    main()
