import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api";
import type { Session } from "../api";
import { Icon } from "../shared/ui";
import { Brand } from "../shared/Brand";

export function Login({
  error,
  onLogin,
  onRetry,
}: {
  error: string;
  onLogin: (session: Session) => void;
  onRetry: () => void;
}) {
  const [busy, setBusy] = useState(false),
    [message, setMessage] = useState("");
  const [username, setUsername] = useState(""),
    [password, setPassword] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      onLogin(
        await api<Session>("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        }),
      );
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="login-layout">
      <section className="login-story">
        <a className="brand" href="#/overview">
          <Brand />
        </a>
        <h2>
          Separate complaints.
          <br />
          <em>One shared plan.</em>
        </h2>
        <p>
          See the people, evidence and next steps behind every case. Bring teams
          together without losing individual responsibility.
        </p>
        <div
          className="login-connection-example"
          aria-label="Illustration of separate case ownership and shared institution coordination"
        >
          <div className="example-cases">
            <div>
              <Icon name="cases" />
              <strong>Complaint A</strong>
              <span>Its own case officer</span>
            </div>
            <div>
              <Icon name="cases" />
              <strong>Complaint B</strong>
              <span>Its own case officer</span>
            </div>
          </div>
          <div className="example-branches" aria-hidden="true" />
          <div className="example-plan">
            <Icon name="coordination" size={22} />
            <div>
              <strong>A shared institution plan</strong>
              <span>Separate coordination lead</span>
            </div>
            <Icon name="check" size={18} />
          </div>
          <p>Illustration · complaints remain separate records</p>
        </div>
        <div className="login-principles">
          <span>
            <Icon name="check" size={16} /> Original records retained
          </span>
          <span>
            <Icon name="check" size={16} /> Authorised human review
          </span>
        </div>
      </section>
      <section className="login-panel panel padded">
        <h1 id="page-title" tabIndex={-1}>
          Sign in to your workspace
        </h1>
        <p>Review complaints and keep the next step clear.</p>
        {(error || message) && (
          <div className="validation-errors" role="alert">
            <p>{message || error}</p>
            <button onClick={onRetry}>Retry connection</button>
          </div>
        )}
        <form className="login-form" onSubmit={submit}>
          <label htmlFor="login-username">Email</label>
          <input
            id="login-username"
            type="email"
            autoComplete="username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button className="primary" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <details className="demo-credentials">
          <summary>Try a fictional demo account</summary>
          <p>
            Choose a role, then sign in. Your role controls the records and
            actions available.
          </p>
          <div className="demo-account-grid">
            {[
              ["rb", "Case officer"],
              ["coordinator", "Coordinator"],
              ["management", "Management"],
              ["supervisor", "Supervisor"],
              ["pgrc", "Grievance officer"],
              ["admin", "Administrator"],
            ].map(([id, label]) => (
              <button
                type="button"
                key={id}
                onClick={() => {
                  setUsername(id + "@demo.test");
                  setPassword("DemoOnly-Stage2!");
                }}
              >
                {label}
              </button>
            ))}
          </div>
          <p className="small">
            Administrator access does not include complaint access.
          </p>
        </details>
      </section>
      <p className="login-disclaimer">
        <strong>Student prototype · fictional data</strong>
        <br />
        No official AICTE connection. No real complaints or personal
        information.
      </p>
    </div>
  );
}
