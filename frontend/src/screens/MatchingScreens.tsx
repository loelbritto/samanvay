import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api";
import type { CaseRecord, Session } from "../api";
import type { Pair } from "./CoordinationScreens";
export function MatchingRetrieval({
  cases,
  session,
  onResults,
}: {
  cases: CaseRecord[];
  session: Session;
  onResults: (pairs: Pair[]) => void;
}) {
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  async function run(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const c = cases.find((c) => c.id === f.get("source"));
    if (!c) return;
    setError("");
    setBusy(true);
    try {
      const result = await api<{
        items: { rank_score: number; review: Pair }[];
        candidate_count: number;
        method: string;
      }>(`/api/cases/${c.id}/matching`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": session.csrf_token,
        },
        body: JSON.stringify({
          expected_version: c.version,
          method: "baseline",
        }),
      });
      onResults(result.items.map((i) => i.review));
      setStatus(
        `${result.items.length} suggestions from ${result.candidate_count} permitted candidates (up to 50). Review each comparison before deciding.`,
      );
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel padded spacing-top">
      <h2>Find potentially connected complaints</h2>
      <p>
        Choose a complaint to look for a possible connection. Closed complaints
        may also be compared.
      </p>
      <form onSubmit={run} className="intake-form">
        <label htmlFor="matching-source">Complaint to compare</label>
        <select id="matching-source" name="source" required>
          <option value="">Choose case with evidence delegation</option>
          {cases
            .filter((c) => c.can_review_pair)
            .map((c) => (
              <option key={c.id} value={c.id}>
                {c.subject} · {c.id}
              </option>
            ))}
        </select>
        <button
          className="primary"
          disabled={busy || !cases.some((c) => c.can_review_pair)}
        >
          {busy ? "Finding suggestions…" : "Find suggestions"}
        </button>
      </form>
      {error && (
        <p role="alert" className="validation-errors">
          {error}
        </p>
      )}
      {status && (
        <p role="status" className="notice blue spacing-top">
          {status}
        </p>
      )}
      <p className="small muted">
        {!cases.some((c) => c.can_review_pair) &&
          "No pair-evidence delegation is available. Ask the authorised coordinator to review. "}
        Rule-based suggestions only; no semantic AI service is connected.
        Choices are limited to 200 recent cases.
      </p>
    </section>
  );
}
