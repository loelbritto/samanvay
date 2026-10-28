import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api";
import type { CaseRecord, Session } from "../api";
import { Notice, PageHeading } from "../shared/ui";
import { Disclosure, Fields } from "../ui";
import { actionFields, availableActions, person, words } from "../presentation";
type Target = {
  id: string;
  name: string;
  bureau: string;
  region: string | null;
};
type Transfer = {
  id: string;
  case_id: string;
  case_version: number;
  source_owner: string;
  source_owner_id: string;
  source_bureau: string;
  target_owner_id: string;
  target_owner: string;
  target_bureau: string;
  status: string;
  version: number;
  expires_at: string;
  reason: string;
  response_reason: string | null;
};

export function WorkflowPanel({
  record: c,
  session,
  onSaved,
}: {
  record: CaseRecord;
  session: Session;
  onSaved: () => void;
}) {
  const [targets, setTargets] = useState<Target[]>([]),
    [action, setAction] = useState(""),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    api<Target[]>("/api/workflow-targets")
      .then(setTargets)
      .catch((e) => setError(e.message));
  }, []);
  const owner = c.owner.id === session.user.id,
    commands = availableActions(c, session),
    chosen = commands.includes(action) ? action : commands[0],
    fields = actionFields(chosen ?? "");
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setBusy(true);
    setError("");
    try {
      await api("/api/cases/" + c.id + "/actions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": session.csrf_token,
        },
        body: JSON.stringify({
          action: chosen,
          expected_version: c.version,
          reason: f.get("reason"),
          text: fields.text ? f.get("text") || "" : "",
          next_action: fields.next ? f.get("next_action") || "" : "",
          due_at:
            fields.due && f.get("due_at")
              ? new Date(String(f.get("due_at"))).toISOString()
              : null,
        }),
      });
      onSaved();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function transfer(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget),
      target = targets.find((t) => t.id === f.get("target"));
    if (!target) return;
    setBusy(true);
    setError("");
    try {
      await api("/api/cases/" + c.id + "/transfers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": session.csrf_token,
        },
        body: JSON.stringify({
          expected_version: c.version,
          target_owner_id: target.id,
          target_bureau_id: target.bureau,
          reason: f.get("reason"),
          expires_at: new Date(String(f.get("expiry"))).toISOString(),
        }),
      });
      onSaved();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel padded spacing-top" id="workflow-panel">
      <div className="section-heading">
        <div>
          <h2>Case actions</h2>
        </div>
        <a className="text-link" href={"#/cases/" + c.id + "/timeline"}>
          View past activity →
        </a>
      </div>
      {error && (
        <div className="validation-errors" role="alert">
          <p>{error}</p>
          <button onClick={onSaved}>Reload the latest record</button>
          <p>Your attempted changes have not been confirmed.</p>
        </div>
      )}
      {commands.length ? (
        <Disclosure title="Update this case">
          <form onSubmit={submit} className="intake-form">
            <label htmlFor="workflow-action">What would you like to do?</label>
            <select
              id="workflow-action"
              value={chosen}
              onChange={(e) => setAction(e.target.value)}
            >
              {commands.map((a) => (
                <option key={a} value={a}>
                  {words(a)}
                </option>
              ))}
            </select>
            {chosen === "REVIEW" && c.lifecycle === "AWAITING_INFORMATION" && (
              <p className="small muted">
                Add the latest requested information before resuming review.
              </p>
            )}
            <div key={chosen}>
              {fields.text && (
                <>
                  <label htmlFor="workflow-text">
                    {chosen === "DISPOSE"
                      ? "Resolution"
                      : chosen === "AMEND"
                        ? "Corrected description (original retained)"
                        : chosen === "REQUEST_INFORMATION"
                          ? "What information is needed?"
                          : "Information received"}{" "}
                    *
                  </label>
                  <textarea
                    id="workflow-text"
                    name="text"
                    rows={4}
                    required
                    minLength={fields.textMinimum}
                    maxLength={20000}
                    defaultValue={
                      chosen === "AMEND" ? (c.description ?? "") : ""
                    }
                  />
                </>
              )}
              {fields.next && (
                <>
                  <label htmlFor="workflow-next">Next step *</label>
                  <input
                    id="workflow-next"
                    name="next_action"
                    required
                    minLength={3}
                    maxLength={500}
                    defaultValue={chosen === "NEXT_ACTION" ? c.next_action : ""}
                  />
                </>
              )}
              {fields.due && (
                <>
                  <label htmlFor="workflow-due">New due date and time</label>
                  <input
                    id="workflow-due"
                    name="due_at"
                    type="datetime-local"
                  />
                  <p className="small muted">
                    Uses your browser's time zone. Leave blank to remove the due
                    date.
                  </p>
                </>
              )}
            </div>
            <label htmlFor="workflow-reason">
              Why are you making this update? *
            </label>
            <textarea
              id="workflow-reason"
              name="reason"
              rows={2}
              required
              minLength={5}
              maxLength={2000}
            />
            <button className="primary" disabled={busy}>
              {busy ? "Saving…" : "Save case update"}
            </button>
          </form>
        </Disclosure>
      ) : (
        <p className="muted">
          Your account can view this case but has no available case action.
        </p>
      )}
      {(owner || c.can_assign) && c.lifecycle !== "DISPOSED" && (
        <Disclosure title="Transfer to another bureau">
          {c.pending_transfer ? (
            <p>
              A transfer is awaiting acceptance.{" "}
              <a href="#/transfers">Review transfer</a>.
            </p>
          ) : (
            <>
              <p>
                The current owner stays responsible until the receiving officer
                accepts.
              </p>
              <form onSubmit={transfer} className="intake-form">
                <label htmlFor="transfer-target">Receiving officer *</label>
                <select id="transfer-target" name="target" required>
                  <option value="">Choose an officer in another bureau</option>
                  {targets
                    .filter((t) => t.bureau !== c.owner.bureau)
                    .map((t) => (
                      <option key={t.id} value={t.id}>
                        {person(t.name)} · {words(t.bureau)}
                      </option>
                    ))}
                </select>
                <label htmlFor="transfer-reason">Reason for transfer *</label>
                <textarea
                  id="transfer-reason"
                  name="reason"
                  required
                  minLength={5}
                  maxLength={1000}
                />
                <label htmlFor="transfer-expiry">
                  Accept by (browser time zone) *
                </label>
                <input
                  id="transfer-expiry"
                  name="expiry"
                  type="datetime-local"
                  required
                />
                <p className="small muted">
                  Choose a future time within 30 days of the demo clock.
                </p>
                <button className="primary" disabled={busy}>
                  Request transfer
                </button>
              </form>
            </>
          )}
        </Disclosure>
      )}
      {!!c.actions?.length && (
        <Disclosure title="Previous information & updates">
          {c.actions.map((a, i) => (
            <article className="history-record" key={i}>
              <h3>{words(a.kind)}</h3>
              {a.payload ? (
                <Fields
                  values={Object.fromEntries(
                    Object.entries(a.payload).filter(([k]) =>
                      [
                        "reason",
                        "text",
                        "next_action",
                        "due_at",
                        "facts",
                      ].includes(k),
                    ),
                  )}
                />
              ) : (
                <p>Details restricted.</p>
              )}
            </article>
          ))}
        </Disclosure>
      )}
      {!!c.identity_history?.length && (
        <Disclosure title="Institution corrections">
          {c.identity_history?.map((h, i) => (
            <article className="history-record" key={i}>
              <h3>
                {h.previous_institution_id} → {h.institution_id}
              </h3>
              <p>
                {person(h.actor)}: {h.reason}
              </p>
              <p>Evidence source: {h.provenance}</p>
              <p>Originally supplied: {h.original_text ?? "Restricted"}</p>
            </article>
          ))}
        </Disclosure>
      )}
      {!!c.resolutions?.length && (
        <Disclosure title="Saved resolutions">
          {c.resolutions.map((r) => (
            <p key={r.id}>{r.text}</p>
          ))}
        </Disclosure>
      )}
    </section>
  );
}
export function TransferInbox({ session }: { session: Session }) {
  const [rows, setRows] = useState<Transfer[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState(false);
  const [busy, setBusy] = useState(false);
  function load() {
    setLoading(true);
    setError("");
    api<Transfer[]>("/api/transfers")
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }
  useEffect(load, []);
  async function decide(e: FormEvent<HTMLFormElement>, t: Transfer) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setError("");
    setBusy(true);
    try {
      await api(`/api/transfers/${t.id}/decision`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": session.csrf_token,
        },
        body: JSON.stringify({
          action: f.get("action"),
          expected_version: t.case_version,
          transfer_version: t.version,
          reason: f.get("reason"),
        }),
      });
      load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading eyebrow="Ownership handoff" title="Transfers">
        The current owner remains responsible until the receiving officer
        accepts.
      </PageHeading>
      {error && (
        <div role="alert" className="validation-errors">
          <p>{error}</p>
          <button onClick={load}>Reload transfers and compare</button>
        </div>
      )}
      <div className="view-switch" aria-label="Transfer view">
        <button aria-pressed={!history} onClick={() => setHistory(false)}>
          Awaiting acceptance (
          {rows.filter((t) => t.status === "PENDING").length})
        </button>
        <button aria-pressed={history} onClick={() => setHistory(true)}>
          All transfers
        </button>
      </div>
      {loading ? (
        <p role="status">Loading transfers…</p>
      ) : rows.filter((t) => history || t.status === "PENDING").length ? (
        rows
          .filter((t) => history || t.status === "PENDING")
          .map((t) => {
            const receiver =
              t.target_owner_id === session.user.id ||
              session.user.memberships.some(
                (m) =>
                  m.role === "BUREAU_SUPERVISOR" &&
                  m.bureau === t.target_bureau,
              );
            return (
              <article className="panel padded spacing-top" key={t.id}>
                <div className="inline spread">
                  <h2>
                    <a href={"#/cases/" + t.case_id}>{t.case_id}</a>
                  </h2>
                  <span className="badge blue">{words(t.status)}</span>
                </div>
                <p>
                  {t.source_owner} ({t.source_bureau}) → {t.target_owner} (
                  {t.target_bureau})
                </p>
                <p>{t.reason}</p>
                <p>Expires {new Date(t.expires_at).toLocaleString()}</p>
                {t.response_reason && (
                  <p>Recorded response: {t.response_reason}</p>
                )}
                {t.status === "PENDING" && (
                  <form onSubmit={(e) => decide(e, t)} className="intake-form">
                    <label htmlFor={"decision-" + t.id}>
                      Transfer decision
                    </label>
                    <select id={"decision-" + t.id} name="action">
                      {receiver ? (
                        <>
                          <option value="ACCEPT">Accept</option>
                          <option value="REJECT">Reject</option>
                        </>
                      ) : (
                        <option value="CANCEL">Cancel</option>
                      )}
                    </select>
                    <label htmlFor={"reason-" + t.id}>Decision reason *</label>
                    <input
                      id={"reason-" + t.id}
                      name="reason"
                      required
                      minLength={5}
                      maxLength={1000}
                    />
                    <button className="primary" disabled={busy}>
                      {busy ? "Saving…" : "Save decision"}
                    </button>
                  </form>
                )}
              </article>
            );
          })
      ) : (
        <Notice>No transfers in this view.</Notice>
      )}
    </>
  );
}
