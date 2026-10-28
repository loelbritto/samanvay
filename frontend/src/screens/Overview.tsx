import { Badge, CaseTable, Icon, PageHeading } from '../components';
import { cases, institutions, referenceDate } from '../fixtures';

export default function Overview() {
  const pune = cases.filter(item => item.institutionId === 'DEMO-INST-017');
  const bureauCount = new Set(pune.map(item => item.bureau)).size;
  return <>
    <PageHeading eyebrow="Officer workspace" title="Overview" action={<a className="button secondary" href="#/cases/new"><Icon name="cases" size={17} /> Preview case intake</a>}>See what needs attention, who owns it, and the next step.</PageHeading>
    <div className="section-heading"><h2>Needs attention <span className="count">2</span></h2><span className="muted small">Illustrative queue · as of {referenceDate}</span></div>
    <section className="attention-list" aria-label="Illustrative attention queue">
      <article className="attention-item"><span className="attention-symbol"><Icon name="coordination" size={24} /></span><div className="attention-copy"><div className="inline"><Badge tone="amber">Coordination required</Badge><span className="small muted">{pune.length} cases · {bureauCount} bureaus</span></div><h3>One institution. Parallel bureau activity.</h3><p>Demo Suryavan Institute, Pune <span className="mono">DEMO-INST-017</span></p><p className="small">Case owners: Demo Ananya Rao (PGRC) and Demo Kabir Sen (RB).<br />Coordination lead: <strong>not yet assigned</strong> · proposed review by 29 Oct.</p></div><a className="button primary" href="#/institutions/DEMO-INST-017">Open institution <Icon name="arrow" size={16} /></a></article>
      <article className="attention-item"><span className="attention-symbol neutral"><Icon name="clock" size={24} /></span><div className="attention-copy"><div className="inline"><Badge tone="amber">Due 28 Oct · illustrative</Badge><span className="mono small">PGRC-019</span></div><h3>Salary statement needs follow-up</h3><p>Demo Suryavan Institute, Pune · faculty grievance</p><p className="small">Owner: Demo Ananya Rao · next: review the requested salary statement.</p></div><a className="button secondary" href="#/cases/PGRC-019">Review case <Icon name="arrow" size={16} /></a></article>
    </section>
    <div className="section-heading spacing-top"><h2>Workload at a glance</h2><span className="muted small">Computed from {cases.length} fictional fixtures</span></div>
    <section className="stats" aria-label="Illustrative workload counts">
      {[{label:'Case records',value:cases.length,href:'#/cases',note:`Across ${institutions.length} fictional institutions`},{label:'Pending',value:cases.length,href:'#/cases',note:'All non-disposed fixture cases'},{label:'Under review',value:cases.filter(c=>c.lifecycle==='Under review').length,href:'#/cases?lifecycle=Under%20review',note:'A subset of pending cases'},{label:'Shared institution',value:1,href:'#/coordination',note:'Illustrative coordination item'}].map(stat=><a href={stat.href} className="stat-card" key={stat.label}><span>{stat.label}<Icon name="arrow" size={16} /></span><strong>{stat.value}</strong><small>{stat.note}</small></a>)}
    </section>
    <section className="panel spacing-top"><div className="panel-heading"><div><h2>Current cases</h2><p className="muted small">Original records remain separate across bureaus.</p></div><a className="text-link" href="#/cases">Browse all cases <Icon name="arrow" size={16} /></a></div><CaseTable records={cases} /></section>
    <div className="footnote"><Icon name="info" size={16} />Counts and deadlines describe this synthetic snapshot. No database or scheduling service is connected.</div>
  </>;
}
