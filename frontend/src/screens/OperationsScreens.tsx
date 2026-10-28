import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api";
import type { Institution, Session } from "../api";
import { EmptyState, Notice, PageHeading } from "../shared/ui";
import {
  CaseFilters,
  Disclosure,
  ResourceState,
  filterParams,
  initialFilters,
  useResource,
} from "../ui";
import { dateLabel, words } from "../presentation";
type Report = {
  total: number;
  pending: number;
  disposed: number;
  under_review: number;
  overdue: number;
  missing_deadline: number;
  cohort_disposal_rate: number | null;
  disposal_to_receipt_ratio: number | null;
  period_distinct_disposals: number;
  historical_accepted_transfers: number;
  as_of: string;
  scope: string;
  dimensions: Record<string, Record<string, number>>;
  active_ageing: Record<string, number>;
  relationship_summary: Record<string, number>;
  monthly: Record<string, string | number>[];
  quarterly: Record<string, string | number>[];
  rows: Record<string, string | number | boolean | null>[];
  formulas: Record<string, string>;
};

export function LiveReports() {
  const [filters, setFilters] = useState(() =>
      initialFilters(new URLSearchParams(location.hash.split("?")[1] ?? "")),
    ),
    [view, setView] = useState("summary"),
    [period, setPeriod] = useState("monthly");
  const params = filterParams(filters).toString(),
    resource = useResource<Report>("/api/reports?" + params),
    data = resource.data;
  const institutions = useResource<Institution[]>("/api/institutions");
  const label = (key: string) =>
    institutions.data?.find((i) => i.id === key)
      ? institutions.data.find((i) => i.id === key)!.name +
        ", " +
        institutions.data.find((i) => i.id === key)!.city
      : words(key);
  return (
    <>
      <PageHeading
        eyebrow="Understand the workload"
        title="Reports"
        action={
          data ? (
            <div className="inline">
              <a
                className="button secondary"
                href={"/api/reports/print?" + params}
              >
                Print report
              </a>
              <a
                className="button primary"
                href={"/api/reports/csv?" + params}
                download
              >
                Download CSV
              </a>
            </div>
          ) : undefined
        }
      >
        Counts and downloads include only the complaints your account may see.
      </PageHeading>
      <CaseFilters prefix="report" filters={filters} onChange={setFilters} />
      <div className="spacing-top">
        <ResourceState {...resource} />
      </div>
      {data && !resource.loading && (
        <>
          <div className="section-heading">
            <p className="small muted">
              As of {dateLabel(data.as_of, true)} IST
            </p>
            <a className="text-link" href={"#/cases?" + params}>
              View these complaints →
            </a>
          </div>
          <div className="stats">
            {[
              ["All complaints", data.total],
              ["Open", data.pending],
              ["Closed", data.disposed],
              ["Overdue", data.overdue],
            ].map(([key, value]) => (
              <div className="stat-card" key={key}>
                <span>{key}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div className="view-switch spacing-top" aria-label="Report view">
            {[
              ["summary", "Summary"],
              ["breakdown", "Breakdowns"],
              ["activity", "Activity over time"],
            ].map(([key, label]) => (
              <button
                key={key}
                aria-pressed={view === key}
                onClick={() => setView(key)}
              >
                {label}
              </button>
            ))}
          </div>
          {view === "summary" ? (
            <section className="panel padded">
              <h2>Progress at a glance</h2>
              <div className="measure-list spacing-top">
                <div>
                  <span className="field-caption">
                    Closed in this selected group
                  </span>
                  <strong>
                    {data.cohort_disposal_rate === null
                      ? "—"
                      : (data.cohort_disposal_rate * 100).toFixed(1) + "%"}
                  </strong>
                  <p>
                    {data.disposed} of {data.total} selected complaints are
                    currently closed.
                  </p>
                </div>
                <div>
                  <span className="field-caption">In review</span>
                  <strong>{data.under_review}</strong>
                  <p>Complaints currently being reviewed.</p>
                </div>
                <div>
                  <span className="field-caption">Open without a due date</span>
                  <strong>{data.missing_deadline}</strong>
                  <p>These cases need a deadline to support reminders.</p>
                </div>
              </div>
              <Disclosure title="How to interpret these numbers">
                <p>{data.scope}</p>
                <p>
                  These totals describe the current status of cases received in
                  the selected date range. They do not reconstruct their status
                  on a past date.
                </p>
                <p>
                  Period closures divided by new receipts:{" "}
                  {data.disposal_to_receipt_ratio === null
                    ? "Not available"
                    : (data.disposal_to_receipt_ratio * 100).toFixed(1) + "%"}
                  . This can exceed 100% when older cases are closed.
                </p>
                <p>
                  {data.period_distinct_disposals} distinct complaints closed in
                  the period. {data.historical_accepted_transfers} accepted
                  transfers are counted separately from case status.
                </p>
                {Object.entries(data.formulas).map(([key, value]) => (
                  <p key={key}>
                    <strong>{words(key)}:</strong> {value}
                  </p>
                ))}
              </Disclosure>
            </section>
          ) : view === "breakdown" ? (
            <div className="report-breakdown">
              {Object.entries({
                ...data.dimensions,
                "Open case age": data.active_ageing,
                "Reviewed relationships": data.relationship_summary,
              }).map(([name, values]) => (
                <section className="panel padded" key={name}>
                  <h2>{words(name)}</h2>
                  {Object.entries(values).length ? (
                    Object.entries(values).map(([key, value]) => (
                      <div className="report-bar" key={key}>
                        <span>{label(key)}</span>
                        <strong>{value}</strong>
                        <meter
                          aria-label={label(key) + " count"}
                          min={0}
                          max={Math.max(1, ...Object.values(values))}
                          value={value}
                        />
                      </div>
                    ))
                  ) : (
                    <p className="muted">No records in this breakdown.</p>
                  )}
                </section>
              ))}
            </div>
          ) : (
            <section className="panel padded">
              <h2>Recorded activity</h2>
              <label htmlFor="report-period">Group by</label>
              <select
                id="report-period"
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
              >
                <option value="monthly">Month</option>
                <option value="quarterly">Quarter</option>
              </select>
              <div className="report-periods">
                {(period === "monthly" ? data.monthly : data.quarterly).map(
                  (r) => (
                    <article className="report-period" key={String(r.period)}>
                      <h3>{r.period}</h3>
                      <p>
                        {r.new_receipts} received · {r.distinct_disposals}{" "}
                        distinct complaints closed
                      </p>
                      <small>
                        {r.disposal_events} closure events ·{" "}
                        {r.reopening_events} reopening events
                      </small>
                    </article>
                  ),
                )}
              </div>
              <p className="small muted spacing-top">
                A complaint may be closed, reopened and closed again. Event
                counts and distinct complaint counts measure different things.
              </p>
            </section>
          )}
          <Disclosure
            title={"Included complaints · " + data.rows.length}
            className="panel padded spacing-top"
          >
            <ul className="participant-list">
              {data.rows.map((r) => (
                <li key={String(r.id)}>
                  <div>
                    <a href={"#/cases/" + r.id}>{String(r.id)}</a>
                    <small>{String(r.institution)}</small>
                  </div>
                  <div>
                    {words(String(r.lifecycle))}
                    <small>{words(String(r.bureau))}</small>
                  </div>
                </li>
              ))}
            </ul>
          </Disclosure>
        </>
      )}
    </>
  );
}
type Notification = {
  id: string;
  kind: string;
  title: string;
  state: string;
  created_at: string;
  case_id: string | null;
  group_id: string | null;
  suggestion_id: string | null;
  transfer_id: string | null;
  policy_version: number;
};

export function LiveNotifications({ session }: { session: Session }) {
  const [rows, setRows] = useState<Notification[] | null>(null),
    [error, setError] = useState(""),
    [all, setAll] = useState(false),
    [limit, setLimit] = useState(20),
    [busy, setBusy] = useState("");
  function load() {
    setError("");
    api<Notification[]>("/api/notifications")
      .then(setRows)
      .catch((e) => setError(e.message));
  }
  useEffect(load, []);
  async function acknowledge(id: string) {
    setBusy(id);
    try {
      await api("/api/notifications/" + id + "/acknowledge", {
        method: "POST",
        headers: { "X-CSRF-Token": session.csrf_token },
      });
      load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy("");
    }
  }
  const shown = (rows ?? [])
    .filter((n) => all || n.state === "DELIVERED")
    .sort((a, b) => b.created_at.localeCompare(a.created_at));
  return (
    <>
      <PageHeading
        eyebrow="Stay on top of your work"
        title="Notifications"
        action={
          <button className="secondary" onClick={load}>
            Refresh
          </button>
        }
      >
        In-app reminders for your work. Marking a reminder as read does not
        change the complaint.
      </PageHeading>
      <div className="view-switch" aria-label="Notification view">
        <button
          aria-pressed={!all}
          onClick={() => {
            setAll(false);
            setLimit(20);
          }}
        >
          Unread{" "}
          {rows
            ? "(" + rows.filter((n) => n.state === "DELIVERED").length + ")"
            : ""}
        </button>
        <button
          aria-pressed={all}
          onClick={() => {
            setAll(true);
            setLimit(20);
          }}
        >
          All notifications
        </button>
      </div>
      {error && (
        <p role="alert" className="validation-errors">
          {error}
        </p>
      )}
      {rows === null && !error ? (
        <p role="status" className="loading-state">
          Loading reminders…
        </p>
      ) : shown.length ? (
        <>
          <section className="panel notification-list">
            {shown.slice(0, limit).map((n) => (
              <article key={n.id}>
                <div>
                  <h2>{n.title}</h2>
                  <p className="small muted">{words(n.kind)}</p>
                  <small>
                    {dateLabel(n.created_at, true)} IST ·{" "}
                    {n.state === "ACKNOWLEDGED"
                      ? "Read"
                      : n.state === "DELIVERED"
                        ? "Unread"
                        : "Delivery pending"}
                  </small>
                </div>
                <div className="button-row">
                  <a
                    className="button secondary"
                    href={
                      n.transfer_id
                        ? "#/transfers"
                        : n.case_id
                          ? "#/cases/" + n.case_id
                          : "#/coordination"
                    }
                  >
                    View record
                  </a>
                  {n.state === "DELIVERED" && (
                    <button
                      className="text-button"
                      disabled={busy === n.id}
                      onClick={() => void acknowledge(n.id)}
                    >
                      {busy === n.id ? "Saving…" : "Mark as read"}
                    </button>
                  )}
                </div>
              </article>
            ))}
          </section>
          {shown.length > limit && (
            <button
              className="secondary spacing-top"
              onClick={() => setLimit((n) => n + 20)}
            >
              Show 20 more
            </button>
          )}
          <p className="small muted spacing-top">
            Showing {Math.min(limit, shown.length)} of {shown.length}{" "}
            notifications. No email service is connected.
          </p>
        </>
      ) : (
        !error && (
          <EmptyState
            title={
              all ? "No notifications yet" : "You have no unread reminders"
            }
          >
            Use All notifications to review previous messages and pending
            deliveries.
          </EmptyState>
        )
      )}
    </>
  );
}
type Settings = {
  policy: {
    version: number;
    approaching_hours: number;
    escalation_hours: number;
    auto_escalate: boolean;
    label: string;
  };
  can_administer: boolean;
  context_id: string;
  clock_version: number;
  clock_enabled: boolean;
  clock_offset_seconds: number;
  as_of: string;
  integration: string;
};
export function LiveSettings({ session }: { session: Session }) {
  const [data, setData] = useState<Settings | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  function load() {
    api<Settings>("/api/settings")
      .then(setData)
      .catch((e) => setError(e.message));
  }
  useEffect(load, []);
  const headers = {
    "Content-Type": "application/json",
    "X-CSRF-Token": session.csrf_token,
  };
  async function policy(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!data) return;
    const f = new FormData(e.currentTarget);
    try {
      await api("/api/settings/policy", {
        method: "POST",
        headers,
        body: JSON.stringify({
          expected_version: data.policy.version,
          approaching_hours: Number(f.get("approaching")),
          escalation_hours: Number(f.get("escalation")),
          auto_escalate: f.get("auto") === "on",
          reason: f.get("reason"),
        }),
      });
      setError("");
      setMessage(
        "Illustrative policy saved with an administrative audit event.",
      );
      load();
    } catch (err) {
      setError((err as Error).message);
    }
  }
  async function batch() {
    try {
      await api("/api/settings/run-worker", { method: "POST", headers });
      setMessage(
        "Persisted in-app scheduling/delivery batch completed. No external messages sent.",
      );
      setError("");
    } catch (err) {
      setError((err as Error).message);
    }
  }
  async function clock(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!data) return;
    const f = new FormData(e.currentTarget);
    try {
      await api("/api/demo/clock", {
        method: "POST",
        headers,
        body: JSON.stringify({
          expected_version: data.clock_version,
          advance_seconds: Number(f.get("hours")) * 3600,
          reason: f.get("reason"),
        }),
      });
      setError("");
      setMessage("Demo time advanced. Stored deadlines were preserved.");
      window.dispatchEvent(new Event("demo-clock-changed"));
      load();
    } catch (err) {
      setError((err as Error).message);
    }
  }
  async function scopes(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    try {
      await api("/api/demo/rehearsal-scope", {
        method: "POST",
        headers,
        body: JSON.stringify({ reason: f.get("reason") }),
      });
      setMessage(
        "Explicit synthetic scopes saved: management Pune metadata only; coordinator current Pune N/I; attachments remain protected.",
      );
      setError("");
    } catch (err) {
      setError((err as Error).message);
    }
  }
  async function fresh(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    try {
      const result = await api<{ context_id: string; reused: boolean }>(
        "/api/demo/new-context",
        {
          method: "POST",
          headers,
          body: JSON.stringify({
            run_key: f.get("key"),
            reason: f.get("reason"),
          }),
        },
      );
      setMessage(
        `Separate context ${result.context_id} ${result.reused ? "reused" : "created"}. This context and all complaints remain. Start it with scripts/run-service.ps1 -Service api -ContextId ${result.context_id} and matching frontend/worker services.`,
      );
      setError("");
    } catch (err) {
      setError((err as Error).message);
    }
  }
  return (
    <>
      <PageHeading eyebrow="Help & demo" title="A quick guide to Samanvay">
        Understand the workspace and the limits of this student prototype.
      </PageHeading>
      <section className="panel padded">
        <h2>Four things to keep separate</h2>
        <dl className="readable-fields">
          <div>
            <dt>Institution</dt>
            <dd>The organisation and city the complaint concerns.</dd>
          </div>
          <div>
            <dt>Case owner</dt>
            <dd>
              The officer responsible for one complaint and its next step.
            </dd>
          </div>
          <div>
            <dt>Coordination lead</dt>
            <dd>
              The person bringing bureaus together around a shared institution
              plan.
            </dd>
          </div>
          <div>
            <dt>Complaint relationship</dt>
            <dd>
              A reviewed evidence decision: repeated complaint, related
              complaints, separate matters or insufficient evidence.
            </dd>
          </div>
        </dl>
        <p className="spacing-top">
          Every complaint stays in the record. Suggestions require authorised
          review and never merge, transfer or close a case.
        </p>
        <Disclosure title="Prototype limits & illustrative preview">
          <p>
            All records are fictional. No AICTE, email, semantic AI or LLM
            service is connected. Local rule-based checks suggest comparisons
            for human review. Real malware scanning and production deployment
            are not established.
          </p>
          <a href="/?preview=1#/overview">
            Open the earlier illustrative UI preview
          </a>
          <p className="small muted">
            The preview uses separate static fixtures, not your saved records.
          </p>
        </Disclosure>
      </section>
      {error && (
        <div role="alert" className="validation-errors">
          <p>{error}</p>
          <button onClick={load}>Reload policy and compare</button>
        </div>
      )}
      {message && (
        <p role="status" className="notice blue">
          {message}
        </p>
      )}
      {!data ? (
        <p role="status">Reading administrative policy…</p>
      ) : (
        <>
          <section className="panel padded spacing-top">
            <h2>Demo reminder policy</h2>
            <p>{data.policy.label}</p>
            <p>
              Approaching window: {data.policy.approaching_hours} hours ·
              escalation threshold: {data.policy.escalation_hours} hours after
              due time · automatic alert escalation{" "}
              {data.policy.auto_escalate ? "enabled" : "disabled"}.
            </p>
            <p>{data.integration}</p>
            {data.can_administer ? (
              <Disclosure title="Edit reminder policy (administrator)">
                <form
                  key={data.policy.version}
                  onSubmit={policy}
                  className="intake-form"
                >
                  <label htmlFor="policy-approaching">
                    Approaching window (hours)
                  </label>
                  <input
                    id="policy-approaching"
                    name="approaching"
                    type="number"
                    min={0}
                    max={720}
                    defaultValue={data.policy.approaching_hours}
                    required
                  />
                  <label htmlFor="policy-escalation">
                    Escalation threshold (hours after due)
                  </label>
                  <input
                    id="policy-escalation"
                    name="escalation"
                    type="number"
                    min={1}
                    max={720}
                    defaultValue={data.policy.escalation_hours}
                    required
                  />
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      name="auto"
                      defaultChecked={data.policy.auto_escalate}
                    />
                    Enable illustrative policy alert escalation (never changes
                    owner)
                  </label>
                  <label htmlFor="policy-reason">Policy change reason *</label>
                  <textarea
                    id="policy-reason"
                    name="reason"
                    required
                    minLength={5}
                    maxLength={1000}
                  />
                  <button className="primary">
                    Save administrative policy
                  </button>
                  <button type="button" className="secondary" onClick={batch}>
                    Process in-app reminders now
                  </button>
                </form>
              </Disclosure>
            ) : (
              <Notice>
                Your account can read this policy. Only a demo administrator can
                change it.
              </Notice>
            )}
          </section>
          <Disclosure
            title="Demo clock & administration"
            className="panel padded spacing-top"
          >
            <h2>Separate demo workspace</h2>
            <p>
              Demo date: {dateLabel(data.as_of, true)} IST · advanced by{" "}
              {data.clock_offset_seconds / 3600} hours.
            </p>
            <Disclosure title="Workspace reference">
              <code>{data.context_id}</code>
            </Disclosure>
            {data.can_administer && data.clock_enabled ? (
              <>
                <form onSubmit={clock} className="intake-form">
                  <label htmlFor="clock-hours">
                    Advance isolated context (hours, maximum 2160)
                  </label>
                  <input
                    id="clock-hours"
                    name="hours"
                    type="number"
                    min={0}
                    max={2160}
                    step={1}
                    required
                  />
                  <label htmlFor="clock-reason">Demo clock reason *</label>
                  <input
                    id="clock-reason"
                    name="reason"
                    minLength={5}
                    maxLength={1000}
                    required
                  />
                  <button className="secondary">
                    Advance isolated demo clock
                  </button>
                </form>
                <section className="spacing-top">
                  <h3>Explicit synthetic rehearsal access</h3>
                  <p>
                    Management receives Pune metadata only. The coordinator
                    receives narrative/identity access to current Pune synthetic
                    cases. Attachments remain protected; ownership does not
                    change.
                  </p>
                  <form className="intake-form" onSubmit={scopes}>
                    <label htmlFor="scope-reason">
                      Rehearsal scope reason *
                    </label>
                    <input
                      id="scope-reason"
                      name="reason"
                      required
                      minLength={5}
                      maxLength={1000}
                    />
                    <button className="secondary">
                      Apply explicit synthetic rehearsal scopes
                    </button>
                  </form>
                  <h3 className="spacing-top">
                    Start a fresh rehearsal without deleting records
                  </h3>
                  <p>
                    A new run key creates a separate database. Repeating the
                    same key reuses its persistent state. This current context
                    is preserved.
                  </p>
                  <form className="intake-form" onSubmit={fresh}>
                    <label htmlFor="fresh-key">New non-secret run key *</label>
                    <input
                      id="fresh-key"
                      name="key"
                      required
                      minLength={8}
                      maxLength={80}
                      pattern="[A-Za-z0-9_-]+"
                    />
                    <label htmlFor="fresh-reason">New-context reason *</label>
                    <input
                      id="fresh-reason"
                      name="reason"
                      required
                      minLength={5}
                      maxLength={1000}
                    />
                    <button className="secondary">
                      Create separate fresh context
                    </button>
                  </form>
                </section>
              </>
            ) : (
              <Notice>
                Clock/reset controls are guarded. The normal workspace cannot be
                advanced or cleared. Use an explicitly enabled marked context
                under .demo-contexts for rehearsal. Existing complaint records
                are preserved.
              </Notice>
            )}
          </Disclosure>
        </>
      )}
    </>
  );
}
