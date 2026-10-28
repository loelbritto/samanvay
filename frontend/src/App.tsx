import { lazy, Suspense } from "react";
import { WorkspaceBoundary } from "./app/WorkspaceBoundary";
const LiveApp = lazy(() => import("./LiveApp"));
const PreviewApp = lazy(() => import("./PreviewApp"));

export default function App() {
  return (
    <WorkspaceBoundary>
      <Suspense fallback={<p role="status">Opening Samanvay…</p>}>
        {new URLSearchParams(location.search).get("preview") === "1" ? (
          <PreviewApp />
        ) : (
          <LiveApp />
        )}
      </Suspense>
    </WorkspaceBoundary>
  );
}
