import type { CaseRecord, Session } from './api';

const labels: Record<string, string> = {
  RECEIVED: 'Received', ASSIGNED: 'Assigned', UNDER_REVIEW: 'In review',
  AWAITING_INFORMATION: 'Waiting for information', DISPOSED: 'Closed',
  REVIEW: 'Start / resume review', REQUEST_INFORMATION: 'Request information',
  INFORMATION: 'Add requested information', AMEND: 'Correct complaint details',
  NEXT_ACTION: 'Update next step', DEADLINE: 'Change due date', ESCALATE: 'Escalate case',
  DISPOSE: 'Close with a resolution', REOPEN: 'Reopen case',
  REVIEW_REQUIRED: 'Needs a shared plan', IN_REVIEW: 'In review', PLANNED: 'Plan agreed', RESOLVED: 'Coordination complete',
  DEFER: 'Review later', CONFIRM: 'Record a relationship', REJECT: 'Reject suggestion',
  UNKNOWN: 'Not enough evidence', RELATED: 'Related complaints',
  DUPLICATE: 'Same complaint submitted again', INDEPENDENT: 'Separate matters',
  PENDING: 'Awaiting acceptance', ACCEPTED: 'Accepted', REJECTED: 'Rejected',
  CANCELLED: 'Cancelled', EXPIRED: 'Expired', NONE: 'None',
  RB: 'Regulation Bureau', PGRC: 'Public Grievance Redressal Cell',
  'DEMO-WEST': 'Western region (demo)',
  RB_OFFICER: 'Regulation officer', PGRC_OFFICER: 'Grievance officer',
  REGIONAL_OFFICER: 'Regional officer', BUREAU_SUPERVISOR: 'Bureau supervisor',
  COORDINATOR: 'Institution coordinator', SENIOR_MANAGEMENT: 'Management', SYSTEM_ADMIN: 'Administrator',
  institution_id: 'Institution', complainant_token: 'Complainant reference',
  incident_reference: 'Incident reference', receipt_reference: 'Receipt reference',
  incident_date: 'Incident date', amount: 'Amount', remedy: 'Requested outcome',
};
export const words = (value: string) => labels[value.replace(/^facts\./, '')] ?? value.replace(/^facts\./, '').replaceAll('_', ' ').toLowerCase().replace(/^./, c => c.toUpperCase());
export const person = (name: string) => name.replace(/^Demo /, '');
export const dateLabel = (value?: string | null, time = false) => value ? new Intl.DateTimeFormat('en-IN', {
  day: 'numeric', month: 'short', year: 'numeric', timeZone: 'Asia/Kolkata',
  ...(time ? { hour: 'numeric', minute: '2-digit' } as const : {}),
}).format(new Date(value.length === 10 ? value + 'T00:00:00+05:30' : value)) : 'No due date';
export const mayCreate = (session: Session) => session.user.memberships.some(m => ['RB_OFFICER', 'PGRC_OFFICER', 'REGIONAL_OFFICER'].includes(m.role));

// Presentation choices narrow controls; the server remains the authority for each mutation.
export function availableActions(c: CaseRecord, session: Session): string[] {
  const active = c.lifecycle !== 'DISPOSED';
  const actions: string[] = [];
  if ((c.owner.id === session.user.id || c.can_assign) && c.can_read_narrative) {
    if (['RECEIVED', 'ASSIGNED', 'AWAITING_INFORMATION'].includes(c.lifecycle)) actions.push('REVIEW');
    if (c.lifecycle === 'UNDER_REVIEW') actions.push('REQUEST_INFORMATION');
    if (c.lifecycle === 'AWAITING_INFORMATION') actions.push('INFORMATION');
    actions.push('AMEND');
    if (active) actions.push('NEXT_ACTION');
  }
  for (const key of ['DEADLINE', 'ESCALATE', 'DISPOSE', 'REOPEN']) {
    if (!c.capabilities?.[key]) continue;
    if (key === 'REOPEN' ? !active : active && (key !== 'DISPOSE' || !c.pending_transfer)) actions.push(key);
  }
  return actions;
}
export const actionFields = (action: string) => ({
  text: ['REQUEST_INFORMATION', 'INFORMATION', 'AMEND', 'DISPOSE'].includes(action),
  textMinimum: action === 'REQUEST_INFORMATION' ? 5 : 10,
  next: ['REQUEST_INFORMATION', 'NEXT_ACTION', 'REOPEN'].includes(action),
  due: action === 'DEADLINE',
});
export function attentionCases(cases: CaseRecord[], asOf: string) {
  const due = (c: CaseRecord) => c.due_at ? new Date(c.due_at).getTime() : Infinity;
  return cases.filter(c => c.lifecycle !== 'DISPOSED').slice().sort((a, b) => {
    const lateA = due(a) < new Date(asOf).getTime(), lateB = due(b) < new Date(asOf).getTime();
    return Number(lateB) - Number(lateA) || due(a) - due(b) || a.id.localeCompare(b.id);
  });
}
