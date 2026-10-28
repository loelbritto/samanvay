import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api";
import { MatchingRetrieval } from "./MatchingScreens";
import type { CaseRecord, Institution, Session } from "../api";
import { Badge, EmptyState, Notice, PageHeading } from "../shared/ui";
import { Disclosure, Fields, useResource } from "../ui";
import { dateLabel, person, words } from "../presentation";
type Group = {
  id: string;
  institution_id: string;
  institution: string;
  label: string;
  condition_active: boolean;
  state: string;
  due_at: string | null;
  version: number;
  lead: string | null;
  lead_id: string | null;
  lead_bureau: string | null;
  next_action: string;
  can_review: boolean;
  cases: {
    id: string;
    owner: string;
    bureau: string;
    lifecycle: string;
    historical_participation: boolean;
  }[];
  reviews: {
    action: string;
    reason: string;
    at: string;
    actor: string;
    version: number;
  }[];
};
export type Pair = {
  id: string;
  left: string;
  right: string;
  left_version: number;
  right_version: number;
  fingerprint: string;
  method: string;
  proposed_label: string;
  evidence: Record<string, unknown>;
  previous_id: string | null;
  version: number;
  stale: boolean;
  workflow_versions_changed?: boolean;
  decision_applies_to_unchanged_evidence?: boolean;
  decisions: {
    action: string;
    label: string | null;
    reason: string;
    actor: string;
  }[];
  sources: {
    id: string;
    version: number;
    subject: string;
    description: string;
    category: string;
    institution_id: string;
    complainant_token: string;
  }[];
};

const transitions: Record<string, string[]> = {
  REVIEW_REQUIRED: ["IN_REVIEW", "DEFER"],
  IN_REVIEW: ["PLANNED", "DEFER"],
  PLANNED: ["IN_REVIEW", "RESOLVED", "DEFER"],
  RESOLVED: ["IN_REVIEW", "DEFER"],
};
const finalDecision = (p: Pair) =>
  p.decisions.some((d) => d.action !== "DEFER");
export function LiveCoordination({
  session,
  institutionId,
  initialView = "plans",
}: {
  session: Session;
  institutionId?: string;
  initialView?: "plans" | "reviews";
}) {
  const [groups, setGroups] = useState<Group[]>([]),
    [pairs, setPairs] = useState<Pair[]>([]),
    [cases, setCases] = useState<CaseRecord[]>([]),
    [targets, setTargets] = useState<
      { id: string; name: string; bureau: string }[]
    >([]);
  const [view, setView] = useState<"plans" | "reviews">(initialView),
    [groupId, setGroupId] = useState(""),
    [pairId, setPairId] = useState(""),
    [showCompleted, setShowCompleted] = useState(false);
  const [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [loading, setLoading] = useState(true),
    [busy, setBusy] = useState(false),
    [decision, setDecision] = useState("CONFIRM");
  const headers = {
    "Content-Type": "application/json",
    "X-CSRF-Token": session.csrf_token,
  };
  function load() {
    setLoading(true);
    setError("");
    Promise.all([
      api<Group[]>("/api/coordination"),
      api<Pair[]>("/api/relationships"),
      api<{ items: CaseRecord[] }>("/api/cases?limit=200"),
      api<typeof targets>("/api/workflow-targets"),
    ])
      .then(([g, p, c, t]) => {
        setGroups(g);
        setPairs(p);
        setCases(c.items);
        setTargets(t);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }
  useEffect(load, []);
  const shownPairs = pairs.filter((p) => showCompleted || !finalDecision(p));
  const group = groupId
      ? groups.find((g) => g.id === groupId)
      : institutionId
        ? groups.find((g) => g.institution_id === institutionId)
        : groups[0],
    selected = shownPairs.find((p) => p.id === pairId) ?? shownPairs[0];
  const focusDetail = () =>
    requestAnimationFrame(() =>
      document.getElementById("review-title")?.focus(),
    );
  async function source(left: string, right: string) {
    if (left === right) {
      setError("Choose two different complaints to compare.");
      return;
    }
    setError("");
    setMessage("");
    setBusy(true);
    try {
      const row = await api<Pair>("/api/relationships/source-review", {
        method: "POST",
        headers,
        body: JSON.stringify({ left, right }),
      });
      setPairId(row.id);
      setView("reviews");
      setShowCompleted(true);
      setMessage("Comparison opened. Review both complaints before deciding.");
      load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function decide(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!selected) return;
    const f = new FormData(e.currentTarget);
    setError("");
    setMessage("");
    setBusy(true);
    try {
      await api("/api/relationships/" + selected.id + "/decision", {
        method: "POST",
        headers,
        body: JSON.stringify({
          action: decision,
          label: decision === "CONFIRM" ? f.get("label") : null,
          expected_version: selected.version,
          left_version: selected.left_version,
          right_version: selected.right_version,
          fingerprint: selected.fingerprint,
          reason: f.get("reason"),
        }),
      });
      setShowCompleted(true);
      setMessage(
        "Review saved. Both complaint records and owners are preserved.",
      );
      load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function plan(e: FormEvent<HTMLFormElement>, g: Group) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setError("");
    setMessage("");
    setBusy(true);
    try {
      await api("/api/coordination/" + g.id + "/review", {
        method: "POST",
        headers,
        body: JSON.stringify({
          state: f.get("state"),
          expected_version: g.version,
          reason: f.get("reason"),
          next_action: f.get("next"),
          lead_id: f.get("lead") || null,
          due_at: g.due_at,
        }),
      });
      setMessage(
        "Coordination update saved. Individual case owners are unchanged.",
      );
      load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading eyebrow="Work across bureaus" title="Coordination">
        Agree a shared institution plan. Review connections between complaints
        separately.
      </PageHeading>
      <div className="view-switch" aria-label="Coordination view">
        <button
          aria-pressed={view === "plans"}
          onClick={() => setView("plans")}
        >
          Institution plans
        </button>
        <button
          aria-pressed={view === "reviews"}
          onClick={() => setView("reviews")}
        >
          Compare complaints
        </button>
      </div>
      {error && (
        <div role="alert" className="validation-errors">
          <p>{error}</p>
          <button onClick={load}>Reload latest records</button>
        </div>
      )}
      {message && (
        <p role="status" className="notice blue">
          {message}
        </p>
      )}
      {loading ? (
        <p className="loading-state" role="status">
          Loading coordination work…
        </p>
      ) : view === "plans" ? (
        <>
          {group ? (
            <div className="review-layout">
              <aside className="review-queue" aria-label="Choose institution">
                {groups.map((g) => (
                  <button
                    className="queue-item"
                    key={g.id}
                    aria-pressed={group.id === g.id}
                    onClick={() => {
                      setGroupId(g.id);
                      focusDetail();
                    }}
                  >
                    <strong>{g.institution}</strong>
                    <small>
                      {words(g.state)} ·{" "}
                      {g.lead ? person(g.lead) : "Needs a coordinator"}
                    </small>
                  </button>
                ))}
              </aside>
              <section
                className="panel padded review-detail"
                key={group.id + "-" + group.version}
              >
                <Badge tone={group.state === "RESOLVED" ? "neutral" : "amber"}>
                  {words(group.state)}
                </Badge>
                <h2 id="review-title" tabIndex={-1} className="spacing-top">
                  {group.institution}
                </h2>
                <p className="muted">
                  {group.condition_active
                    ? "Active complaints span more than one bureau. Agree the shared next step."
                    : "Cross-bureau activity is no longer active. The previous plan and case history are retained."}
                </p>
                <div className="responsibility">
                  <div>
                    <span className="field-caption">Coordination lead</span>
                    <strong>
                      {group.lead ? person(group.lead) : "Not yet assigned"}
                    </strong>
                    <small>
                      {group.lead_bureau
                        ? words(group.lead_bureau)
                        : "Assign a lead when agreeing the plan"}
                    </small>
                  </div>
                  <div>
                    <span className="field-caption">Shared next step</span>
                    <p>
                      {group.next_action ||
                        "Agree a next step with the participating bureaus."}
                    </p>
                  </div>
                </div>
                <h3>Each complaint keeps its own owner</h3>
                <ul className="participant-list">
                  {group.cases.map((c) => (
                    <li key={c.id}>
                      <div>
                        <a href={"#/cases/" + c.id}>{c.id}</a>
                        <small>
                          {words(c.lifecycle)}
                          {c.historical_participation
                            ? " · previously at this institution"
                            : ""}
                        </small>
                      </div>
                      <div>
                        <strong>{person(c.owner)}</strong>
                        <small>{words(c.bureau)}</small>
                      </div>
                    </li>
                  ))}
                </ul>
                {group.can_review && (
                  <Disclosure
                    title={
                      group.state === "REVIEW_REQUIRED"
                        ? "Start a coordination review"
                        : "Update coordination plan"
                    }
                  >
                    <form
                      className="intake-form"
                      onSubmit={(e) => plan(e, group)}
                    >
                      <label htmlFor="plan-state">Next stage</label>
                      <select id="plan-state" name="state">
                        {(transitions[group.state] ?? []).map((s) => (
                          <option key={s} value={s}>
                            {s === "IN_REVIEW"
                              ? "Review the shared plan"
                              : s === "PLANNED"
                                ? "Agree a plan"
                                : s === "RESOLVED"
                                  ? "Complete coordination"
                                  : words(s)}
                          </option>
                        ))}
                      </select>
                      <label htmlFor="plan-lead">
                        Who coordinates the institution?
                      </label>
                      <select
                        id="plan-lead"
                        name="lead"
                        defaultValue={group.lead_id ?? ""}
                      >
                        <option value="">Keep current / choose a lead</option>
                        {targets.map((t) => (
                          <option key={t.id} value={t.id}>
                            {person(t.name)} · {words(t.bureau)}
                          </option>
                        ))}
                      </select>
                      <p className="small muted">
                        A named lead is required to agree a plan. This does not
                        change any complaint owner.
                      </p>
                      <label htmlFor="plan-next">Shared next step *</label>
                      <input
                        id="plan-next"
                        name="next"
                        required
                        minLength={3}
                        maxLength={500}
                        defaultValue={group.next_action}
                      />
                      <label htmlFor="plan-reason">
                        Reason for this update *
                      </label>
                      <textarea
                        id="plan-reason"
                        name="reason"
                        required
                        minLength={5}
                        maxLength={2000}
                      />
                      <button className="primary" disabled={busy}>
                        Save coordination update
                      </button>
                    </form>
                  </Disclosure>
                )}
                <Disclosure title="Previous coordination updates">
                  {group.reviews.map((r, i) => (
                    <article className="history-record" key={i}>
                      <h3>{words(r.action)}</h3>
                      <p>{r.reason}</p>
                      <small>
                        {person(r.actor)} · {dateLabel(r.at, true)} IST
                      </small>
                    </article>
                  ))}
                </Disclosure>
                <a
                  className="text-link spacing-top"
                  href={"#/institutions/" + group.institution_id}
                >
                  View institution and activity →
                </a>
              </section>
            </div>
          ) : (
            <EmptyState title="No shared plans available">
              Only institutions whose participating cases are within your access
              are shown. Your case owner can help with coordination.
            </EmptyState>
          )}
        </>
      ) : (
        <>
          <p className="section-note">
            Suggestions need an authorised review. Similar names alone do not
            make complaints duplicates. No review merges or removes a complaint.
          </p>
          <Disclosure title="Start a new comparison" className="panel padded">
            <MatchingRetrieval
              cases={cases}
              session={session}
              onResults={(rows) => {
                setPairs((old) => [
                  ...rows,
                  ...old.filter((p) => !rows.some((r) => r.id === p.id)),
                ]);
                setPairId(rows[0]?.id ?? "");
                setShowCompleted(true);
              }}
            />
            <Disclosure title="Choose two specific complaints">
              <p className="small muted">
                Choices are limited to the 200 most recent cases you may view;
                evidence-review permission is also required.
              </p>
              <form
                className="intake-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  const f = new FormData(e.currentTarget);
                  void source(String(f.get("left")), String(f.get("right")));
                }}
              >
                <div className="two-column">
                  {["left", "right"].map((side) => (
                    <div key={side}>
                      <label htmlFor={"pair-" + side}>
                        {side === "left"
                          ? "First complaint"
                          : "Second complaint"}
                      </label>
                      <select id={"pair-" + side} name={side} required>
                        <option value="">Choose complaint</option>
                        {cases
                          .filter((c) => c.can_review_pair)
                          .map((c) => (
                            <option key={c.id} value={c.id}>
                              {c.subject} · {c.id}
                            </option>
                          ))}
                      </select>
                    </div>
                  ))}
                </div>
                <button
                  className="secondary"
                  disabled={busy || !cases.some((c) => c.can_review_pair)}
                >
                  Open comparison
                </button>
              </form>
            </Disclosure>
          </Disclosure>
          <label className="checkbox-row spacing-top">
            <input
              type="checkbox"
              checked={showCompleted}
              onChange={(e) => setShowCompleted(e.target.checked)}
            />
            Include completed reviews
          </label>
          {selected ? (
            <div className="review-layout spacing-top">
              <aside className="review-queue" aria-label="Choose comparison">
                {shownPairs.map((p) => (
                  <button
                    className="queue-item"
                    key={p.id}
                    aria-pressed={selected.id === p.id}
                    onClick={() => {
                      setPairId(p.id);
                      setDecision("CONFIRM");
                      focusDetail();
                    }}
                  >
                    <strong>{p.sources[0]?.subject ?? p.left}</strong>
                    <small>
                      {p.left} / {p.right}
                    </small>
                    <small>
                      {p.stale
                        ? "Evidence changed"
                        : finalDecision(p)
                          ? "Reviewed"
                          : "Awaiting review"}
                    </small>
                  </button>
                ))}
              </aside>
              <section
                className="panel padded review-detail"
                key={selected.id + "-" + selected.version}
              >
                <h2 id="review-title" tabIndex={-1}>
                  {words(selected.proposed_label)}
                </h2>
                <p className="badge amber">
                  {finalDecision(selected)
                    ? "Recorded review"
                    : "Suggestion · review required"}
                </p>
                <p>
                  Proposed by{" "}
                  {selected.method === "HUMAN_SOURCE_REVIEW"
                    ? "a manual source comparison"
                    : "rule-based checks"}
                  . Read the evidence before deciding.
                </p>
                {selected.stale && (
                  <Notice tone="amber">
                    The source records changed. Earlier decisions remain saved.
                    <button
                      disabled={busy}
                      className="secondary"
                      onClick={() => void source(selected.left, selected.right)}
                    >
                      Open current comparison
                    </button>
                  </Notice>
                )}
                {selected.workflow_versions_changed &&
                  selected.decision_applies_to_unchanged_evidence && (
                    <p className="small muted">
                      Case activity changed, but the evidence is unchanged. The
                      recorded final decision still applies.
                    </p>
                  )}
                <div className="evidence-columns">
                  {selected.sources.map((s, index) => (
                    <article className="source-card" key={s.id}>
                      <h3>{s.subject}</h3>
                      <p className="small muted">
                        Complaint {index + 1} ·{" "}
                        <a href={"#/cases/" + s.id + "/timeline"}>{s.id}</a>
                      </p>
                      <blockquote className="preserve-text">
                        {s.description}
                      </blockquote>
                      <dl className="readable-fields">
                        <div>
                          <dt>Institution</dt>
                          <dd>{s.institution_id}</dd>
                        </div>
                        <div>
                          <dt>Category</dt>
                          <dd>{s.category}</dd>
                        </div>
                        <div>
                          <dt>Complainant</dt>
                          <dd>{s.complainant_token}</dd>
                        </div>
                      </dl>
                    </article>
                  ))}
                </div>
                <Evidence evidence={selected.evidence} />
                {selected.decisions.map((d, i) => (
                  <article className="history-record" key={i}>
                    <Badge>
                      {d.action === "CONFIRM"
                        ? words(d.label ?? "UNKNOWN")
                        : words(d.action)}
                    </Badge>
                    <p className="spacing-top">{d.reason}</p>
                    <small>Reviewed by {person(d.actor)}</small>
                  </article>
                ))}
                {!finalDecision(selected) && !selected.stale && (
                  <div className="review-decision">
                    <h3>Your review</h3>
                    <form onSubmit={decide} className="intake-form">
                      <label htmlFor="pair-decision">Decision</label>
                      <select
                        id="pair-decision"
                        value={decision}
                        onChange={(e) => setDecision(e.target.value)}
                      >
                        <option value="CONFIRM">Record a relationship</option>
                        <option value="REJECT">Reject this suggestion</option>
                        <option value="DEFER">Review later</option>
                      </select>
                      {decision === "CONFIRM" && (
                        <>
                          <label htmlFor="pair-label">
                            How are these complaints connected?
                          </label>
                          <select
                            id="pair-label"
                            name="label"
                            required
                            defaultValue=""
                          >
                            <option value="" disabled>
                              Choose after reviewing the evidence
                            </option>
                            {[
                              "UNKNOWN",
                              "DUPLICATE",
                              "RELATED",
                              "INDEPENDENT",
                            ].map((l) => (
                              <option key={l} value={l}>
                                {words(l)}
                              </option>
                            ))}
                          </select>
                          <p className="small muted">
                            Different people or receipts from the same incident
                            can be related. “Same complaint” requires evidence
                            of the same complainant and request.
                          </p>
                        </>
                      )}
                      <label htmlFor="pair-reason">
                        Explain the evidence behind your decision *
                      </label>
                      <textarea
                        id="pair-reason"
                        name="reason"
                        required
                        minLength={5}
                        maxLength={2000}
                      />
                      <button className="primary" disabled={busy}>
                        {busy ? "Saving…" : "Save review"}
                      </button>
                    </form>
                  </div>
                )}
                {finalDecision(selected) && (
                  <p className="notice blue spacing-top">
                    This final review is preserved. New material evidence
                    requires a new linked review.
                  </p>
                )}
                <Disclosure title="Review method & reference details">
                  <Fields
                    values={{
                      method: selected.method,
                      review_reference: selected.id,
                      previous_review: selected.previous_id,
                      score_meaning:
                        selected.evidence.score_meaning ??
                        "No probability estimate",
                      source_versions:
                        selected.left_version + " / " + selected.right_version,
                    }}
                  />
                  <p className="small muted">
                    No semantic AI or LLM service is connected. Any automated
                    output is a suggestion. Human review is required.
                  </p>
                </Disclosure>
              </section>
            </div>
          ) : (
            <EmptyState title="No comparisons in this view">
              Start a comparison, or include completed reviews to inspect a
              previous decision.
            </EmptyState>
          )}
        </>
      )}
    </>
  );
}
function Evidence({ evidence }: { evidence: Record<string, unknown> }) {
  return (
    <>
      {[
        ["supporting", "Evidence listed in support"],
        ["conflicting", "Differences to review"],
        ["missing", "What is missing"],
      ].map(([key, title]) => (
        <section className="evidence-section" key={key}>
          <h3>{title}</h3>
          {Array.isArray(evidence[key]) &&
          (evidence[key] as unknown[]).length ? (
            <ul>
              {(evidence[key] as unknown[]).map((item, index) => {
                if (typeof item === "string")
                  return <li key={index}>{item.replaceAll("_", " ")}</li>;
                const citation = item as {
                  case_id?: string;
                  field?: string;
                  value?: unknown;
                  excerpt?: string;
                };
                return (
                  <li key={index}>
                    <strong>{words(citation.field ?? "Evidence")}:</strong>{" "}
                    {String(citation.excerpt ?? citation.value ?? "")}{" "}
                    {citation.case_id && (
                      <a href={"#/cases/" + citation.case_id + "/timeline"}>
                        ({citation.case_id})
                      </a>
                    )}
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="small muted">
              None recorded. This does not establish that the complaints match.
            </p>
          )}
        </section>
      ))}
    </>
  );
}
export function IdentityTools({
  session,
  institutionId,
}: {
  session: Session;
  institutionId?: string;
}) {
  const [result, setResult] = useState<{
    status: string;
    selected_candidate: string | null;
    candidates: {
      id: string;
      city: string;
      basis: string;
      city_conflict: boolean;
    }[];
  } | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const institutions = useResource<Institution[]>("/api/institutions");
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [events, setEvents] = useState<
    {
      case_id: string;
      type: string;
      at: string;
      reason: string;
      owner: string;
      bureau: string;
    }[]
  >([]);
  useEffect(() => {
    api<{ items: CaseRecord[] }>("/api/cases")
      .then((r) => setCases(r.items))
      .catch((e) => setError(e.message));
    if (institutionId)
      api<{ events: typeof events }>(
        `/api/institutions/${institutionId}/timeline`,
      )
        .then((r) => setEvents(r.events))
        .catch((e) => setError(e.message));
  }, [institutionId]);
  async function lookup(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setResult(null);
    setError("");
    try {
      setResult(
        await api(
          "/api/identity/lookup?" +
            new URLSearchParams({
              q: String(f.get("q")),
              city: String(f.get("city")),
            }),
        ),
      );
      setError("");
    } catch (err) {
      setError((err as Error).message);
    }
  }
  async function confirm(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const c = cases.find((c) => c.id === f.get("case"));
    if (!c) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await api(`/api/cases/${c.id}/identity`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": session.csrf_token,
        },
        body: JSON.stringify({
          institution_id: f.get("institution"),
          expected_version: c.version,
          reason: f.get("reason"),
          provenance: f.get("provenance"),
          alias: f.get("alias") || "",
          acknowledge_conflict: f.get("ack") === "on",
        }),
      });
      setMessage(
        "Institution decision saved. The original name and previous decisions are retained.",
      );
      window.dispatchEvent(new Event("case-records-changed"));
      if (institutionId) {
        const timeline = await api<{ events: typeof events }>(
          "/api/institutions/" + institutionId + "/timeline",
        );
        setEvents(timeline.events);
      }
      const current = await api<{ items: CaseRecord[] }>("/api/cases");
      setCases(current.items);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Disclosure
        title="Check or correct an institution name"
        className="panel padded spacing-top"
      >
        <p>
          Use this when a submitted name is unclear or a case is linked to the
          wrong institution.
        </p>
        <form onSubmit={lookup} className="intake-form">
          <label htmlFor="identity-query">Institution name or reference</label>
          <input id="identity-query" name="q" required maxLength={500} />
          <label htmlFor="identity-city">City (optional)</label>
          <input id="identity-city" name="city" maxLength={100} />
          <button className="secondary">Find institution</button>
        </form>
        {result && (
          <div role="status" className="spacing-top">
            <strong>{words(result.status)}</strong>
            {result.candidates.map((c) => (
              <p key={c.id}>
                {institutions.data?.find((i) => i.id === c.id)?.name ?? c.id} ·{" "}
                {c.city} · {words(c.basis)}
                {c.city_conflict ? " · location conflict" : ""}
              </p>
            ))}
          </div>
        )}
        {error && (
          <p role="status" className="notice amber">
            {error}
          </p>
        )}
        {message && (
          <p role="status" className="notice blue">
            {message}
          </p>
        )}
        <details className="spacing-top">
          <summary>Correct a case’s institution</summary>
          <p>
            Your account needs permission to correct the institution. If the
            original city conflicts, explain the evidence and acknowledge the
            conflict. Choices show up to 200 recent cases.
          </p>
          <form onSubmit={confirm} className="intake-form">
            <label htmlFor="identity-case">Case to review</label>
            <select id="identity-case" name="case" required>
              <option value="">Select source</option>
              {cases
                .filter((c) => c.can_read_narrative)
                .map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.subject} · {c.id}
                  </option>
                ))}
            </select>
            <label htmlFor="identity-target">Correct institution *</label>
            <select
              id="identity-target"
              name="institution"
              required
              defaultValue={institutionId ?? ""}
            >
              <option value="">Choose institution and city</option>
              {institutions.data?.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.name}, {i.city} · {i.id}
                </option>
              ))}
            </select>
            <label htmlFor="identity-reason">Identity decision reason *</label>
            <textarea
              id="identity-reason"
              name="reason"
              required
              minLength={5}
              maxLength={1000}
            />
            <label htmlFor="identity-provenance">
              Where does the evidence come from? *
            </label>
            <input
              id="identity-provenance"
              name="provenance"
              required
              minLength={5}
              maxLength={1000}
            />
            <label htmlFor="identity-alias">Confirmed alias (optional)</label>
            <input id="identity-alias" name="alias" maxLength={180} />
            <label className="checkbox-row">
              <input type="checkbox" name="ack" />I reviewed and explained any
              conflicting original location
            </label>
            <button className="primary" disabled={busy}>
              {busy ? "Saving…" : "Save institution correction"}
            </button>
          </form>
        </details>
      </Disclosure>
      {institutionId && (
        <Disclosure
          title="Institution activity history"
          className="panel padded spacing-top"
        >
          <p>
            Only your permitted case activity is shown. Case owners and
            coordination leads remain separate.
          </p>
          <ol className="timeline">
            {[...events]
              .sort((a, b) => a.at.localeCompare(b.at))
              .map((e, i) => (
                <li key={i}>
                  <div>
                    <a href={`#/cases/${e.case_id}/timeline`}>{e.case_id}</a>
                    <h3>{words(e.type)}</h3>
                    <p>{e.reason}</p>
                    <p className="small muted">
                      {new Date(e.at).toLocaleString()} · current owner{" "}
                      {e.owner} ({e.bureau})
                    </p>
                  </div>
                </li>
              ))}
          </ol>
        </Disclosure>
      )}
    </>
  );
}
