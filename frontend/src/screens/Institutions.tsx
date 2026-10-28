import { Badge, CaseTable, EmptyState, Icon, Notice, PageHeading } from '../components';
import { cases, findInstitution, institutions } from '../fixtures';

export function InstitutionList() {
  return <><PageHeading eyebrow="Institution directory" title="Institutions">A shared name does not establish a shared identity.</PageHeading><Notice>Both institutions below are fictional. Their cities and identifiers deliberately differ.</Notice><div className="institution-grid spacing-top">{institutions.map(item=>{const count=cases.filter(c=>c.institutionId===item.id).length;return <article className="panel institution-card" key={item.id}><span className="institution-icon"><Icon name="institutions" size={30} /></span><Badge>Fictional institution</Badge><h2>{item.name}, {item.city}</h2><p className="mono">{item.id}</p><p className="muted">{item.address}</p><p>{count} illustrative case {count===1?'record':'records'}</p><a className="button secondary" href={`#/institutions/${item.id}`}>Open {item.city} institution <Icon name="arrow" size={16}/></a></article>;})}</div></>;
}
export function InstitutionProfile({ id }: { id:string }) {
  const institution = findInstitution(id);
  if (!institution) return <EmptyState title="Institution not found">This identifier is not part of the synthetic preview. <a href="#/institutions">Return to the directory</a>.</EmptyState>;
  const records = cases.filter(c=>c.institutionId===id);
  const bureauCount = new Set(records.map(c=>c.bureau)).size;
  const multiBureau = bureauCount > 1;
  return <>
    <a className="back-link" href="#/institutions">← Institution directory</a>
    <PageHeading eyebrow="Fictional institution profile" title={`${institution.name}, ${institution.city}`}>Institution identity · <span className="mono">{institution.id}</span></PageHeading>
    <div className="profile-facts"><div><span>Location</span><strong>{institution.city}, Maharashtra</strong></div><div><span>Illustrative alias</span><strong>{institution.alias}</strong></div><div><span>Identity status</span><strong>Selected fixture identity</strong></div><div><span>Case activity</span><strong>{records.length} {records.length===1?'record':'records'} · {bureauCount} {bureauCount===1?'bureau':'bureaus'}</strong></div></div>
    <Notice>Alias provenance and authorized identity confirmation need a backend. The similarly named {institution.city === 'Pune' ? 'Nagpur' : 'Pune'} institution has a different identifier. <a href={`#/institutions/${institution.city === 'Pune' ? 'DEMO-INST-044' : 'DEMO-INST-017'}`}>Inspect the other institution</a>.</Notice>
    {multiBureau ? <section className="coordination-callout spacing-top"><div><Badge tone="amber">Shared institution — coordination required</Badge><h2>Review the connection. Keep each case accountable.</h2><p>PGRC and RB have active fixture cases here, including an independent faculty grievance. Complaint similarity is not required for institutional coordination.</p><p className="small"><strong>Case owners:</strong> Demo Ananya Rao / Demo Kabir Sen &nbsp; <strong>Coordination lead:</strong> unassigned</p></div><a className="button primary" href="#/coordination/compare">Compare evidence <Icon name="arrow" size={16}/></a></section> : <Notice>This institution has cases in one bureau in this snapshot. It does not meet the proposed cross-bureau coordination condition.</Notice>}
    <section className="panel spacing-top"><div className="panel-heading"><div><h2>Cases at this institution</h2><p className="small muted">Fictional original records · independent ownership</p></div></div><CaseTable records={records} /></section>
    <section className="panel padded spacing-top"><div className="section-heading"><h2>Institution activity</h2><Badge>Illustrative timeline</Badge></div><ol className="timeline compact">{records.map(c=><li key={c.id}><span className="timeline-dot"/><div><p className="small muted">{c.received} · {c.bureau}</p><h3>{c.id} · {c.subject}</h3><p>Accountable owner: {c.owner}</p><a className="text-link" href={`#/cases/${c.id}/timeline`}>View case timeline <Icon name="arrow" size={14}/></a></div></li>)}</ol></section>
  </>;
}
