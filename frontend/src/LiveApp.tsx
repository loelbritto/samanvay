import { useEffect, useState } from "react";
import { Login } from "./app/Login";
import { WorkspaceShell } from "./app/WorkspaceShell";
import { RouteView } from "./app/RouteView";
import { parseRoute } from "./app/navigation";
import { useSession } from "./app/useSession";
import { Notice } from "./shared/ui";
import "./design-system/workspace.css";
import "@fontsource/manrope/latin-400.css";
import "@fontsource/manrope/latin-500.css";
import "@fontsource/manrope/latin-600.css";
import "@fontsource/manrope/latin-700.css";
import "./design-system/desk.css";

export default function LiveApp() {
  const auth = useSession();
  const [hash, setHash] = useState(location.hash);
  const route = parseRoute(hash);
  useEffect(() => {
    const changed = () => setHash(location.hash);
    window.addEventListener("hashchange", changed);
    return () => window.removeEventListener("hashchange", changed);
  }, []);
  useEffect(() => {
    document.title = route.label + " · Samanvay demo";
    const frame = requestAnimationFrame(() =>
      document.getElementById("page-title")?.focus(),
    );
    window.scrollTo(0, 0);
    return () => cancelAnimationFrame(frame);
  }, [hash, route.label, auth.session]);
  return (
    <div className="samanvay-app">
      {auth.loading ? (
        <div className="login-layout">
          <p role="status">Opening Samanvay…</p>
        </div>
      ) : !auth.session ? (
        <Login error={auth.error} onLogin={auth.login} onRetry={auth.retry} />
      ) : (
        <WorkspaceShell
          session={auth.session}
          route={hash}
          section={route.section}
          label={route.label}
          onLogout={auth.logout}
        >
          {auth.error && <Notice tone="amber">{auth.error}</Notice>}
          <RouteView route={route} session={auth.session} />
        </WorkspaceShell>
      )}
    </div>
  );
}
