// All records, people, events and deadlines in this file are fictional, illustrative fixtures.
// No workflow state is persisted or changed by the Stage 1 preview.
export type Case = {
  id: string; institutionId: string; bureau: 'PGRC' | 'RB'; owner: string;
  subject: string; description: string; category: string;
  lifecycle: 'Under review' | 'Awaiting information' | 'Assigned';
  received: string; due: string; nextAction: string;
  student: string; receipt: string; incident: string; amount?: string;
};
export const institutions = [
  { id: 'DEMO-INST-017', name: 'Demo Suryavan Institute', city: 'Pune', alias: 'DSI Pune', address: 'Fictional campus, Pune, Maharashtra' },
  { id: 'DEMO-INST-044', name: 'Demo Suryavan Institute', city: 'Nagpur', alias: 'DSI Nagpur', address: 'Fictional campus, Nagpur, Maharashtra' },
] as const;
export const cases: readonly Case[] = [
  { id: 'PGRC-014', institutionId: 'DEMO-INST-017', bureau: 'PGRC', owner: 'Demo Ananya Rao', subject: 'Admission fee refund pending', description: 'My admission cancellation was included in refund batch DEMO-BATCH-07 on 16 October. The ₹42,000 refund against receipt R-882 has not arrived.', category: 'Fee refund', lifecycle: 'Under review', received: '2026-10-20', due: '2026-10-29', nextAction: 'Compare the refund evidence with RB-023', student: 'DEMO-STU-042', receipt: 'R-882', incident: 'DEMO-BATCH-07 · 16 Oct 2026', amount: '₹42,000' },
  { id: 'RB-023', institutionId: 'DEMO-INST-017', bureau: 'RB', owner: 'Demo Kabir Sen', subject: 'Refund not received after cancellation', description: 'DSI Pune has not paid my ₹42,000 cancellation refund. My receipt is R-883 and the institute referred to DEMO-BATCH-07 dated 16 October.', category: 'Fee refund', lifecycle: 'Under review', received: '2026-10-22', due: '2026-10-30', nextAction: 'Review related incident; retain separate handling', student: 'DEMO-STU-057', receipt: 'R-883', incident: 'DEMO-BATCH-07 · 16 Oct 2026', amount: '₹42,000' },
  { id: 'PGRC-019', institutionId: 'DEMO-INST-017', bureau: 'PGRC', owner: 'Demo Ananya Rao', subject: 'Faculty salary clarification', description: 'A fictional faculty member requests a salary statement for September. This concerns a separate issue and period from the student refund cases.', category: 'Faculty grievance', lifecycle: 'Awaiting information', received: '2026-10-23', due: '2026-10-28', nextAction: 'Review the requested salary statement', student: 'DEMO-FAC-008', receipt: 'Not applicable', incident: 'September 2026 salary period' },
  { id: 'RB-031', institutionId: 'DEMO-INST-044', bureau: 'RB', owner: 'Demo Meera Das', subject: 'Laboratory equipment clarification', description: 'A fictional laboratory equipment query at the Nagpur campus. This is a different institution from the similarly named Pune campus.', category: 'Infrastructure', lifecycle: 'Assigned', received: '2026-10-25', due: '2026-11-02', nextAction: 'Begin review of the submitted equipment list', student: 'DEMO-STAFF-011', receipt: 'Not applicable', incident: 'October 2026 equipment review' },
];
export const findInstitution = (id: string) => institutions.find(item => item.id === id);
export const institutionLabel = (id: string) => { const item = findInstitution(id); return item ? `${item.name}, ${item.city}` : 'Unknown institution'; };
export const dateLabel = (date: string) => new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'Asia/Kolkata' }).format(new Date(`${date}T00:00:00+05:30`));
export const referenceDate = '27 Oct 2026';
