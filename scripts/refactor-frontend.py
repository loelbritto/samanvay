"""Separate runtime shell, preview fixtures and live primitives without changing records."""
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'frontend/src'
source = (root / 'components.tsx').read_text(encoding='utf-8')
start, end = source.index('export function Icon('), source.index('export function Badge(')
(root / 'shared/Icon.tsx').write_text("import type { ReactNode } from 'react';\n\n" + source[start:end], encoding='utf-8')
(root / 'components.tsx').write_text(source[:start] + "import { Icon } from './shared/Icon';\nexport { Icon } from './shared/Icon';\n" + source[end:], encoding='utf-8')
for name in ['LiveScreens', 'WorkflowScreens', 'CoordinationScreens', 'MatchingScreens', 'OperationsScreens']:
    path = root / f'screens/{name}.tsx'
    source = path.read_text(encoding='utf-8').replace("from '../components'", "from '../shared/ui'")
    source = source.replace('<p className="eyebrow">{words(n.kind)}</p><h2>{n.title}</h2>', '<h2>{n.title}</h2><p className="small muted">{words(n.kind)}</p>')
    if name == 'LiveScreens':
        start, end = source.index('export function LiveOverview('), source.index('export function LiveCases(')
        source = source[:start] + source[end:]
        source = source.replace('attentionCases, ', '')
        source = source.replace('Every update stays with this complaint. Its owner is responsible for the next step.', '{id} · Every update stays with this complaint.')
    path.write_text(source, encoding='utf-8')
path = root / 'ui.tsx'
source = path.read_text(encoding='utf-8')
source = source.replace("import { useEffect, useState } from 'react';\n", '').replace("import { api } from './api';\n", '')
start, end = source.index('export function useResource'), source.index('export function ResourceState')
source = source[:start] + "import { useResource } from './shared/useResource';\nexport { useResource } from './shared/useResource';\n\n" + source[end:]
path.write_text(source, encoding='utf-8')
path = root / 'main.tsx'
path.write_text(path.read_text(encoding='utf-8').replace("import './styles.css';\n", ''), encoding='utf-8')
path = root / 'PreviewApp.tsx'
path.write_text("import './styles.css';\n" + path.read_text(encoding='utf-8'), encoding='utf-8')
(root / 'LiveApp.tsx').write_text('''import { useEffect, useState } from 'react';
import { Login } from './app/Login';
import { WorkspaceShell } from './app/WorkspaceShell';
import { RouteView } from './app/RouteView';
import { parseRoute } from './app/navigation';
import { useSession } from './app/useSession';
import { Notice } from './shared/ui';
import './design-system/workspace.css';

export default function LiveApp() {
  const auth = useSession();
  const [hash, setHash] = useState(location.hash);
  const route = parseRoute(hash);
  useEffect(() => {
    const changed = () => setHash(location.hash);
    window.addEventListener('hashchange', changed);
    return () => window.removeEventListener('hashchange', changed);
  }, []);
  useEffect(() => {
    document.title = route.label + ' · Samanvay demo';
    const frame = requestAnimationFrame(() => document.getElementById('page-title')?.focus());
    window.scrollTo(0, 0);
    return () => cancelAnimationFrame(frame);
  }, [hash, route.label, auth.session]);
  return <div className="samanvay-app">{auth.loading ? <div className="login-layout"><p role="status">Opening Samanvay…</p></div> : !auth.session ?
    <Login error={auth.error} onLogin={auth.login} onRetry={auth.retry}/> :
    <WorkspaceShell session={auth.session} route={hash} section={route.section} label={route.label} onLogout={auth.logout}>
      {auth.error && <Notice tone="amber">{auth.error}</Notice>}<RouteView route={route} session={auth.session}/>
    </WorkspaceShell>}</div>;
}
''', encoding='utf-8')
(root / 'App.tsx').write_text('''import { lazy, Suspense } from 'react';
const LiveApp = lazy(() => import('./LiveApp'));
const PreviewApp = lazy(() => import('./PreviewApp'));

export default function App() {
  return <Suspense fallback={<p role="status">Opening Samanvay…</p>}>
    {new URLSearchParams(location.search).get('preview') === '1' ? <PreviewApp/> : <LiveApp/>}
  </Suspense>;
}
''', encoding='utf-8')
print('Separated preview styles and fixtures from live runtime; extracted shell, resource hook and shared icons.')
