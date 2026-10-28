"""One-time relocation of existing case UI into explicit feature boundaries."""
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'frontend/src'
source = (root / 'screens/LiveScreens.tsx').read_text(encoding='utf-8')
def part(start, end=None):
    return source[source.index(start):source.index(end) if end else len(source)]
files = {
 'features/cases/CaseList.tsx': ("import type { CaseRecord } from '../../api';\nimport { Badge, Icon } from '../../shared/ui';\nimport { dateLabel as date, person, words as titleState } from '../../presentation';\n", part('export function LiveTable(', 'export function LiveCases(')),
 'features/cases/CasesPage.tsx': ("import { useState } from 'react';\nimport type { CaseRecord, Session } from '../../api';\nimport { PageHeading, EmptyState } from '../../shared/ui';\nimport { CaseFilters, ResourceState, useResource, filterParams, initialFilters } from '../../ui';\nimport { mayCreate } from '../../presentation';\nimport { LiveTable } from './CaseList';\n", part('export function LiveCases(', 'export function LiveIntake(')),
 'features/cases/IntakePage.tsx': ("import { useState } from 'react';\nimport type { FormEvent } from 'react';\nimport { api } from '../../api';\nimport type { CaseRecord, Institution, Session } from '../../api';\nimport { PageHeading, Notice } from '../../shared/ui';\nimport { ResourceState, useResource } from '../../ui';\n", part('export function LiveIntake(', 'export function LiveDetail(')),
 'features/cases/CaseDetailPage.tsx': ("import { useState } from 'react';\nimport type { FormEvent } from 'react';\nimport { api } from '../../api';\nimport type { CaseRecord, Session } from '../../api';\nimport { Badge, PageHeading, Notice } from '../../shared/ui';\nimport { ResourceState, Disclosure, useResource } from '../../ui';\nimport { dateLabel as date, person, words as titleState } from '../../presentation';\nimport { WorkflowPanel } from '../../screens/WorkflowScreens';\n", part('export function LiveDetail(', 'export function LiveInstitutions(')),
 'features/institutions/InstitutionsPage.tsx': ("import type { CaseRecord, Institution } from '../../api';\nimport { Badge, PageHeading, Notice, EmptyState, Icon } from '../../shared/ui';\nimport { ResourceState, useResource } from '../../ui';\nimport { LiveTable } from '../cases/CaseList';\n", part('export function LiveInstitutions(', 'export function Unavailable(')),
 'app/NotFound.tsx': ("import { PageHeading } from '../shared/ui';\n", part('export function Unavailable(')),
}
for name, (imports, body) in files.items():
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(imports + '\n' + body, encoding='utf-8')
(root / 'screens/LiveScreens.tsx').write_text('''// Compatibility exports for the feature-organised application.
export { LiveTable } from '../features/cases/CaseList';
export { LiveCases } from '../features/cases/CasesPage';
export { LiveIntake } from '../features/cases/IntakePage';
export { LiveDetail } from '../features/cases/CaseDetailPage';
export { LiveInstitutions } from '../features/institutions/InstitutionsPage';
export { Unavailable } from '../app/NotFound';
''', encoding='utf-8')
path = root / 'features/workspace/WorkQueue.tsx'
path.write_text(path.read_text(encoding='utf-8').replace("from '../../screens/LiveScreens'", "from '../cases/CaseList'"), encoding='utf-8')
path = root / 'screens/WorkflowScreens.tsx'
path.write_text(path.read_text(encoding='utf-8').replace('<p className="eyebrow">Move the case forward</p>', ''), encoding='utf-8')
path = root / 'screens/CoordinationScreens.tsx'
text = path.read_text(encoding='utf-8')
text = text.replace('<p className="eyebrow">{finalDecision(selected)?\'Recorded review\':\'Suggestion · review required\'}</p><h2 id="review-title" tabIndex={-1}>{words(selected.proposed_label)}</h2>', '<h2 id="review-title" tabIndex={-1}>{words(selected.proposed_label)}</h2><p className="badge amber">{finalDecision(selected)?\'Recorded review\':\'Suggestion · review required\'}</p>')
text = text.replace('<p className="eyebrow">Complaint {index+1}</p><a href={\'#/cases/\'+s.id+\'/timeline\'}>{s.id}</a><h3>{s.subject}</h3>', '<h3>{s.subject}</h3><p className="small muted">Complaint {index+1} · <a href={\'#/cases/\'+s.id+\'/timeline\'}>{s.id}</a></p>')
path.write_text(text, encoding='utf-8')
print('Split case list, intake, detail and institution pages into feature modules.')
