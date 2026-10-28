"""Regression contracts for the architecture pass, using disposable databases only."""
import ast
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path
import pytest
from sqlalchemy import select
from app.application.case_actions import execute_case_action
from app.domain.case_actions import ActionCommand, CaseState, RuleViolation, decide_action
from app.models import CaseRecord, now
from app.case_views import deadline_date
from conftest import signin


def state(**changes):
    return replace(CaseState('UNDER_REVIEW', now() - timedelta(days=30), 2, 0), **changes)


@pytest.mark.parametrize('action,case,arguments', [
    ('REVIEW', state(lifecycle='AWAITING_INFORMATION'), {}),
    ('REQUEST_INFORMATION', state(lifecycle='DISPOSED'), {'text': 'Receipt required', 'next_action': 'Wait'}),
    ('INFORMATION', state(), {'text': 'Information supplied'}),
    ('NEXT_ACTION', state(lifecycle='DISPOSED'), {'next_action': 'Review'}),
    ('DEADLINE', state(), {'due_at': now().replace(tzinfo=None)}),
    ('DEADLINE', state(), {'due_at': now() - timedelta(days=60)}),
    ('DISPOSE', state(pending_transfer=True), {'text': 'Detailed resolution'}),
    ('DISPOSE', state(evidence_authorised=False), {'text': 'Detailed resolution'}),
    ('REOPEN', state(), {'next_action': 'Review appeal'}),
    ('ESCALATE', state(lifecycle='DISPOSED'), {}),
    ('UNKNOWN', state(), {}),
])
def test_invalid_transition_never_reaches_repository_commit(action, case, arguments):
    class Repository:
        def snapshot(self, command): return case
        def commit(self, command, decision): pytest.fail('An invalid action reached persistence')
    with pytest.raises(RuleViolation):
        execute_case_action(Repository(), ActionCommand(action, 1, 'Synthetic test', **arguments))


def test_amendment_changes_current_narrative_without_original_identity_or_ownership():
    decision = decide_action(state(), ActionCommand('AMEND', 1, 'Synthetic correction', text='Corrected current description', facts={'receipt_reference': 'DEMO-2'}))
    assert decision.changes == {'description': 'Corrected current description', 'facts': {'receipt_reference': 'DEMO-2'}}
    assert not decision.record_resolution


def test_domain_and_application_do_not_import_http_or_sql():
    root = Path(__file__).parents[1] / 'app'
    for directory in ['domain', 'application']:
        for file in (root / directory).glob('*.py'):
            for node in ast.walk(ast.parse(file.read_text())):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names = [node.module or ''] if isinstance(node, ast.ImportFrom) else [name.name for name in node.names]
                    assert not any(part in name.split('.') for name in names for part in ['fastapi', 'sqlalchemy', 'models', 'infrastructure', 'api', 'workflows']), file


def test_workspace_includes_old_urgent_case_beyond_twenty_newest(system, client):
    signin(client)
    with system.state.sessions() as db:
        case = db.scalar(select(CaseRecord).where(CaseRecord.public_id == 'RB-023'))
        case.due_at = now() - timedelta(days=100)
        case.created_at = now() - timedelta(days=200)
        for index in range(26):
            values = {column.name: getattr(case, column.name) for column in CaseRecord.__table__.columns if column.name not in {'id', 'public_id'}}
            values.update(public_id=f'DEMO-QUEUE-{index}', due_at=now()+timedelta(days=index+1), created_at=now())
            db.add(CaseRecord(**values))
        db.commit()
    recent = client.get('/api/overview').json()['cases']
    assert 'RB-023' not in [case['id'] for case in recent]
    response = client.get('/api/workspace')
    assert response.status_code == 200
    data = response.json()
    assert data['items'][0]['id'] == 'RB-023'
    assert data['matching'] > 20 and len(data['items']) == 12
    assert all(case['lifecycle'] != 'DISPOSED' for case in data['items'])


@pytest.mark.parametrize('role', ['rb', 'coordinator', 'management', 'admin'])
def test_workspace_obeys_scope_and_queue_filters(client, role):
    signin(client, role + '@demo.test')
    cases = client.get('/api/cases').json()
    visible = {case['id']: case for case in cases['items']}
    session = client.get('/api/auth/session').json()
    for queue in ['open', 'overdue', 'mine']:
        response = client.get('/api/workspace?queue=' + queue)
        assert response.status_code == 200
        data = response.json()
        assert data['counts']['total'] == cases['total']
        for case in data['items']:
            assert case['id'] in visible and case['lifecycle'] != 'DISPOSED'
            assert case['subject'] == visible[case['id']]['subject']
            if queue == 'mine': assert case['owner']['id'] == session['user']['id']
            if queue == 'overdue': assert case['due_at'] < data['as_of']
    assert client.get('/api/workspace?queue=anything').status_code == 422


def test_workspace_requires_session(client):
    assert client.get('/api/workspace').status_code == 401


def test_deadline_projection_preserves_date_only_and_explicit_daytime_values():
    assert deadline_date(datetime.fromisoformat('2026-10-29T00:00:00+05:30')) == '2026-10-28'
    assert deadline_date(datetime.fromisoformat('2026-10-29T15:30:00+05:30')) == '2026-10-29'
    assert deadline_date(datetime.fromisoformat('2026-10-29T00:30:00+00:00')) == '2026-10-29'
    assert deadline_date(None) is None
