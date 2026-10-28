import assert from 'node:assert/strict';
import test from 'node:test';
import { actionFields, attentionCases, availableActions, dateLabel, mayCreate, words } from '../src/presentation.ts';
import type { CaseRecord, Session } from '../src/api.ts';

const session = { user: { id: 'officer', memberships: [{ role: 'RB_OFFICER', bureau: 'RB', region: null }] } } as Session;
const base = { id: 'DEMO-CASE-1', owner: { id: 'officer', name: 'Fictional officer', bureau: 'RB' }, lifecycle: 'RECEIVED', can_read_narrative: true, can_assign: false, capabilities: {} } as CaseRecord;

test('an officer sees tasks appropriate to the current state', () => {
  assert.deepEqual(availableActions(base, session), ['REVIEW', 'AMEND', 'NEXT_ACTION']);
  assert.deepEqual(availableActions({ ...base, lifecycle: 'UNDER_REVIEW' }, session), ['REQUEST_INFORMATION', 'AMEND', 'NEXT_ACTION']);
  assert.deepEqual(availableActions({ ...base, lifecycle: 'AWAITING_INFORMATION' }, session), ['REVIEW', 'INFORMATION', 'AMEND', 'NEXT_ACTION']);
});
test('metadata-only supervision does not expose narrative commands', () => {
  const record = { ...base, owner: { ...base.owner, id: 'other' }, can_assign: true, can_read_narrative: false, capabilities: { DEADLINE: true } };
  assert.deepEqual(availableActions(record, session), ['DEADLINE']);
});
test('viewing another officer case does not grant actions', () => {
  assert.deepEqual(availableActions({ ...base, owner: { ...base.owner, id: 'other' } }, session), []);
});
test('pending transfer suppresses closure and closed cases expose reopening only when delegated', () => {
  const privileged = { ...base, capabilities: { DISPOSE: true, REOPEN: true, DEADLINE: true, ESCALATE: true } };
  assert.equal(availableActions({ ...privileged, pending_transfer: 'transfer-1' }, session).includes('DISPOSE'), false);
  assert.equal(availableActions(privileged, session).includes('DISPOSE'), true);
  assert.deepEqual(availableActions({ ...privileged, lifecycle: 'DISPOSED' }, session), ['AMEND', 'REOPEN']);
  assert.deepEqual(availableActions({ ...privileged, lifecycle: 'DISPOSED', capabilities: {} }, session), ['AMEND']);
});
test('requesting information includes both the question and the next step', () => {
  assert.deepEqual(actionFields('REQUEST_INFORMATION'), { text: true, textMinimum: 5, next: true, due: false });
});
test('closure requires a resolution and no irrelevant deadline or next-step fields', () => {
  assert.deepEqual(actionFields('DISPOSE'), { text: true, textMinimum: 10, next: false, due: false });
  assert.equal(actionFields('AMEND').text, true);
  assert.equal(actionFields('INFORMATION').text, true);
});
test('deadline and reopening forms request different inputs', () => {
  assert.deepEqual(actionFields('DEADLINE'), { text: false, textMinimum: 10, next: false, due: true });
  assert.equal(actionFields('REOPEN').next, true);
  assert.equal(actionFields('REOPEN').due, false);
});
test('attention uses the supplied demo date, retains input, excludes closed cases, orders by deadline', () => {
  const records = [
    { ...base, id: 'none', due_at: null },
    { ...base, id: 'future', due_at: '2035-02-04T00:00:00Z' },
    { ...base, id: 'closed', due_at: '2035-01-01T00:00:00Z', lifecycle: 'DISPOSED' },
    { ...base, id: 'late', due_at: '2035-02-01T00:00:00Z' },
  ];
  assert.deepEqual(attentionCases(records, '2035-02-03T00:00:00Z').map(c => c.id), ['late', 'future', 'none']);
  assert.deepEqual(records.map(c => c.id), ['none', 'future', 'closed', 'late']);
});
test('intake availability respects account role, not broad administration', () => {
  assert.equal(mayCreate(session), true);
  for (const role of ['COORDINATOR', 'SYSTEM_ADMIN', 'SENIOR_MANAGEMENT', 'BUREAU_SUPERVISOR']) {
    assert.equal(mayCreate({ ...session, user: { ...session.user, memberships: [{ role, bureau: null, region: null }] } }), false);
  }
});
test('India dates preserve date-only inputs and cross-midnight timestamps', () => {
  assert.equal(dateLabel('2026-10-28'), '28 Oct 2026');
  assert.equal(dateLabel('2026-10-27T20:00:00Z'), '28 Oct 2026');
  assert.equal(dateLabel(null), 'No due date');
  assert.equal(words('facts.receipt_reference'), 'Receipt reference');
});
