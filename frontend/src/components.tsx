import { useId } from 'react';
import type { ReactNode } from 'react';
import { dateLabel, institutionLabel } from './fixtures';
import type { Case } from './fixtures';

import { Icon } from './shared/Icon';
export { Icon } from './shared/Icon';
export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: string }) { return <span className={`badge ${tone}`}>{children}</span>; }
export function PageHeading({ eyebrow, title, children, action }: { eyebrow: string; title: string; children: ReactNode; action?: ReactNode }) {
  return <header className="page-heading"><div><p className="eyebrow">{eyebrow}</p><h1 tabIndex={-1} id="page-title">{title}</h1><p className="subtitle">{children}</p></div>{action}</header>;
}
export function Notice({ children, tone = 'blue' }: { children: ReactNode; tone?: string }) { return <div className={`notice ${tone}`}><Icon name="info" /><div>{children}</div></div>; }
export function Pending({ children = 'Requires an authenticated backend and a database transaction.' }: { children?: ReactNode }) { return <p className="pending-note"><Icon name="info" size={16} />{children}</p>; }
export function CaseTable({ records, caption = 'Illustrative case records' }: { records: readonly Case[]; caption?: string }) {
  const hintId = useId();
  return <><p className="table-hint" id={hintId}>Scroll the table horizontally to see owners, deadlines and next actions. Keyboard: focus the table, then use the arrow keys.</p><div className="table-scroll" role="region" aria-label={caption} aria-describedby={hintId} tabIndex={0} onKeyDown={event=>{if(event.target!==event.currentTarget||event.altKey||event.ctrlKey||event.metaKey)return;const region=event.currentTarget;if(event.key==='ArrowRight'||event.key==='ArrowLeft'){event.preventDefault();region.scrollLeft+=event.key==='ArrowRight'?80:-80;}else if(event.key==='Home'||event.key==='End'){event.preventDefault();region.scrollLeft=event.key==='Home'?0:region.scrollWidth;}}}><table><caption>{caption} · fictional fixtures, no database</caption><thead><tr><th scope="col">Case / institution</th><th scope="col">Issue</th><th scope="col">Accountable owner</th><th scope="col">Lifecycle / due date</th><th scope="col">Next action</th></tr></thead><tbody>{records.map(record => <tr key={record.id}>
    <td><a className="case-id" href={`#/cases/${record.id}`}>{record.id}</a><span className="cell-sub">{institutionLabel(record.institutionId)}</span><span className="mono cell-sub">{record.institutionId}</span></td>
    <td>{record.subject}<span className="cell-sub">{record.category}</span></td><td>{record.owner}<span className="cell-sub">{record.bureau}</span></td><td><Badge tone={record.lifecycle === 'Awaiting information' ? 'amber' : 'blue'}>{record.lifecycle}</Badge><span className="cell-sub">{dateLabel(record.due)}</span></td><td><span className="next-action">{record.nextAction}</span><a className="text-link" href={`#/cases/${record.id}/timeline`}>View timeline <Icon name="arrow" size={14} /></a></td>
  </tr>)}</tbody></table></div></>;
}
export function EmptyState({ title, children, action }: { title: string; children: ReactNode; action?: ReactNode }) { return <div className="empty-state"><span className="empty-icon"><Icon name="cases" size={28} /></span><h2>{title}</h2><p>{children}</p>{action}</div>; }
