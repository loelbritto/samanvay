import { Component } from "react";
import type { ReactNode } from "react";

/** A failed module load must leave a recovery control, not an empty workspace. */
export class WorkspaceBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <main
        role="alert"
        style={{
          maxWidth: "32rem",
          margin: "12vh auto",
          padding: "1.5rem",
          fontFamily: "var(--font-ui, sans-serif)",
          lineHeight: 1.6,
        }}
      >
        <h1 style={{ fontSize: "1.5rem" }}>
          The workspace could not be loaded
        </h1>
        <p>
          Reload to reconnect to your saved complaints. Unsaved changes have not
          been confirmed.
        </p>
        <button
          type="button"
          style={{ minHeight: 44, padding: "10px 16px", cursor: "pointer" }}
          onClick={() => location.reload()}
        >
          Reload workspace
        </button>
        <p style={{ fontSize: ".875rem" }}>
          Samanvay · synthetic student prototype
        </p>
      </main>
    );
  }
}
