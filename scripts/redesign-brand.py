"""One-time UI brand migration; never opens application databases."""
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'frontend/src'
path = root / 'design-system/tokens.css'
css = path.read_text(encoding='utf-8')
colours = {
 '#12283f':'#163b35', '#2b4056':'#354e47', '#536579':'#5c6b63', '#d5dde5':'#dce2d8',
 '#eaf0f5':'#e9eee5', '#f4f7fa':'#f7f8f2', '#205a9c':'#176350', '#edf4fc':'#eaf4ed',
 '#80500b':'#805318', '#fff5df':'#fff3dd', '#2265bb':'#247a66',
 '#e1eaf3':'#354e47', '#2c4c6e':'#155543',
}
for before, after in colours.items(): css = css.replace(before, after)
css = css.replace('--rail: var(--ink-950);', '--rail: #f0f2e9;')
css = css.replace('--rail-width: 224px;', '--rail-width: 240px;')
css = css.replace('--font-ui: "Segoe UI", "Helvetica Neue", Arial, sans-serif;', '--font-ui: "Manrope", "Segoe UI", sans-serif;\n  --brand-accent: #b86b28;\n  --action-hover: #104b3d;\n  --control-border: #91a398;\n  --focus-surface: #123b3b;\n  --focus-text: #f4f7ee;\n  --focus-muted: #c2d6ca;')
path.write_text(css, encoding='utf-8')
path = root / 'design-system/workspace.css'
css = path.read_text(encoding='utf-8')
for before, after in {**colours, '#184a83':'#104b3d', '#97a9ba':'#91a398', '#cce0f5':'#d6e9da',
 '#203d58':'#e1e8dc', '#c0d0df':'#5c6b63', '#bdcede':'#5c6b63', '#6f8ba5':'#91a398',
 '#3a5269':'#d4ddcf', '#e8eef4':'#ecefe5', '#40536a':'#52634f', '#6e8093':'#647765',
 '#f8fafc':'#fafbf6', '#cbdff3':'#ccddce', '#9bafc2':'#9bac9b', '#647587':'#637263'}.items():
    css = css.replace(before, after)
css = css.replace('font-weight: 650;', 'font-weight: 700;')
# The chosen identity changes the existing shell rules, rather than layering a second theme.
css = css.replace('  background: var(--rail);\n  color: var(--rail-text);', '  background: var(--rail);\n  border-right: 1px solid var(--border);\n  color: var(--rail-text);')
css = css.replace('  color: #fff;\n  font-size: 1.125rem;\n  font-weight: 700;', '  color: var(--text);\n  font-size: 1.125rem;\n  font-weight: 700;')
css = css.replace('  padding: 30px 16px 20px;', '  padding: 32px 18px 20px;')
css = css.replace('  margin-top: 36px;', '  margin-top: 44px;')
css = css.replace('  font-size: 1.75rem;\n  letter-spacing: -0.025em;', '  font-size: 1.875rem;\n  letter-spacing: -0.03em;')
path.write_text(css, encoding='utf-8')

(root / 'features/workspace/WorkQueue.tsx').write_text('''import { useState } from 'react';
import type { CaseRecord, Session } from '../../api';
import { PageHeading, EmptyState, Icon } from '../../shared/ui';
import { ResourceState, useResource } from '../../ui';
import { dateLabel, mayCreate } from '../../presentation';
import { LiveTable } from '../cases/CaseList';
import { FocusCase } from './FocusCase';
import { InstitutionConnections } from './InstitutionConnections';

type Queue = 'open' | 'overdue' | 'mine';
type Workspace = { as_of: string; queue: Queue; counts: Record<Queue | 'total', number>; matching: number; limit: number; items: CaseRecord[] };

export function WorkQueue({ session }: { session: Session }) {
  const [queue, setQueue] = useState<Queue>('open');
  const [view, setView] = useState<'cases' | 'institutions'>('cases');
  const resource = useResource<Workspace>('/api/workspace?queue=' + queue);
  const data = resource.data;
  return <>
    <PageHeading title="Your workspace" action={mayCreate(session) ? <a className="button primary" href="#/cases/new">New complaint <Icon name="arrow" size={16}/></a> : undefined}>
      Every complaint has an owner. Every team has a next step.
    </PageHeading>
    <div className="workspace-viewbar"><div className="workspace-view-switch" aria-label="Workspace view"><button aria-pressed={view === 'cases'} onClick={() => setView('cases')}><Icon name="cases" size={18}/>Case queue</button><button aria-pressed={view === 'institutions'} onClick={() => setView('institutions')}><Icon name="coordination" size={18}/>Shared plans</button></div><span className="workspace-date">{data ? dateLabel(data.as_of) + ' · demo date' : 'Persistent synthetic workspace'}</span></div>
    {view === 'institutions' ? <InstitutionConnections/> : <div className="desk-layout">
      <section className="queue-workspace" aria-label="Complaint work queue">
        <div className="queue-toolbar"><div className="queue-tabs" aria-label="Show complaints">{([['open','All open'],['overdue','Overdue'],['mine','Assigned to me']] as const).map(([key,label]) => <button key={key} aria-pressed={queue === key} onClick={() => setQueue(key)}>{label}{data && <span className="count">{data.counts[key]}</span>}</button>)}</div><button className="text-button" onClick={resource.reload}>Refresh</button></div>
        <ResourceState {...resource}/>
        {data && !resource.loading && <>
          {data.items.length ? <>
            <FocusCase record={data.items[0]} asOf={data.as_of}/>
            {data.items.length > 1 && <><div className="queue-rest-heading"><h2>Also in your queue</h2><span>{data.items.length - 1} shown</span></div><LiveTable records={data.items.slice(1)} asOf={data.as_of}/></>}
          </> : <EmptyState title={queue === 'overdue' ? 'No overdue complaints' : 'No complaints in this queue'}>Try another view or browse all complaints, including closed records.</EmptyState>}
          <div className="queue-footer"><span>Showing {data.items.length} of {data.matching} matching complaints</span><a href="#/cases">All {data.counts.total} records <Icon name="arrow" size={16}/></a></div>
        </>}
      </section>
      <aside className="desk-context" aria-label="Shared work and review guidance">
        <InstitutionConnections compact onExpand={() => setView('institutions')}/>
        <section className="desk-review-note"><Icon name="check" size={20}/><h2>You make the decision.</h2><p>Suggested connections are a starting point. Review the evidence before recording a relationship.</p><a href="#/coordination">Open evidence reviews <Icon name="arrow" size={15}/></a></section>
      </aside>
    </div>}
  </>;
}
''', encoding='utf-8')
print('Updated live brand tokens, existing shell theme and work queue composition.')
