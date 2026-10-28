import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "../../api";
import type { CaseRecord, Session } from "../../api";
import { Badge, PageHeading, Notice } from "../../shared/ui";
import { ResourceState, Disclosure, useResource } from "../../ui";
import {
  dateLabel as date,
  person,
  words as titleState,
} from "../../presentation";
import { WorkflowPanel } from "../../screens/WorkflowScreens";

export function LiveDetail({
  id,
  timeline,
  session,
}: {
  id: string;
  timeline: boolean;
  session: Session;
}) {
  const resource = useResource<CaseRecord>(
      "/api/cases/" + encodeURIComponent(id),
    ),
    c = resource.data;
  return (
    <>
      <a href="#/cases" className="back-link">
        ← Complaints
      </a>
      <PageHeading eyebrow={id} title={c?.subject ?? "Complaint"}>
        {id} · Every update stays with this complaint.
      </PageHeading>
      <ResourceState {...resource} />
      {c && !resource.loading && (
        <>
          <div className="detail-tabs">
            <a
              href={"#/cases/" + id}
              aria-current={!timeline ? "page" : undefined}
            >
              Case overview
            </a>
            <a
              href={"#/cases/" + id + "/timeline"}
              aria-current={timeline ? "page" : undefined}
            >
              Activity & history
            </a>
          </div>
          <section className="case-summary panel">
            <div>
              <span className="field-caption">Case owner</span>
              <h2>{person(c.owner.name)}</h2>
              <p>{titleState(c.owner.bureau)}</p>
            </div>
            <div>
              <span className="field-caption">Status</span>
              <Badge tone={c.lifecycle === "DISPOSED" ? "neutral" : "blue"}>
                {titleState(c.lifecycle)}
              </Badge>
              <p>Due {date(c.expected_disposal_date)}</p>
            </div>
            <div className="next-step">
              <span className="field-caption">Next step</span>
              <strong>{c.next_action}</strong>
              {c.transfer_state === "PENDING" && (
                <p className="small">
                  Transfer awaiting acceptance. Current owner remains
                  responsible.
                </p>
              )}
              {c.escalation_level > 0 && (
                <p className="small">Escalated · level {c.escalation_level}</p>
              )}
            </div>
          </section>
          {timeline ? (
            <>
              <section className="panel padded spacing-top">
                <h2>Activity history</h2>
                <ol className="timeline">
                  {c.history?.map((e) => (
                    <li key={e.id}>
                      <span className="timeline-dot" />
                      <div>
                        <p className="small muted">
                          {date(e.at, true)} IST · {person(e.actor)}
                        </p>
                        <h3>{titleState(e.type)}</h3>
                        <p>{e.reason}</p>
                      </div>
                    </li>
                  ))}
                </ol>
              </section>
              <Disclosure
                title="Previous case owners"
                className="panel padded spacing-top"
              >
                {c.assignments?.map((a, index) => (
                  <p key={index}>
                    <strong>{person(a.owner)}</strong> · {titleState(a.bureau)}
                    <span className="cell-sub">
                      {date(a.from)} → {a.to ? date(a.to) : "Current"} ·{" "}
                      {a.reason}
                    </span>
                  </p>
                ))}
              </Disclosure>
            </>
          ) : (
            <>
              <div className="detail-grid spacing-top">
                <section className="panel padded">
                  <h2>Complaint details</h2>
                  <dl className="evidence-fields">
                    <div>
                      <dt>Institution</dt>
                      <dd>
                        <a href={"#/institutions/" + c.institution_id}>
                          {c.institution_name}, {c.city}
                        </a>
                      </dd>
                    </div>
                    <div>
                      <dt>Received</dt>
                      <dd>{date(c.received_date)}</dd>
                    </div>
                    <div>
                      <dt>Category</dt>
                      <dd>{c.category ?? "Restricted"}</dd>
                    </div>
                  </dl>
                  {c.can_read_narrative ? (
                    <>
                      <h3>Current description</h3>
                      <blockquote className="preserve-text">
                        {c.description}
                      </blockquote>
                      <Disclosure title="Original submission & reference details">
                        <p className="preserve-text">
                          {typeof c.original_submission?.description ===
                          "string"
                            ? c.original_submission.description
                            : "Original structured submission retained by the server."}
                        </p>
                        <dl className="evidence-fields">
                          <div>
                            <dt>Institution as submitted</dt>
                            <dd>{c.original_institution_text}</dd>
                          </div>
                          <div>
                            <dt>Institution reference</dt>
                            <dd>{c.institution_id}</dd>
                          </div>
                          <div>
                            <dt>Complainant reference</dt>
                            <dd>{c.complainant?.token ?? "Restricted"}</dd>
                          </div>
                        </dl>
                        <p className="small muted">
                          Saved original checksum (SHA-256)
                        </p>
                        <code>{c.original_sha256}</code>
                        <p className="small muted">
                          The original is retained when details are corrected. A
                          checksum is not a guarantee against database
                          tampering.
                        </p>
                      </Disclosure>
                    </>
                  ) : (
                    <Notice>
                      Your account can see the owner and status. The complaint
                      description and personal details are restricted.
                    </Notice>
                  )}
                </section>
                <aside className="panel padded">
                  <h2>Supporting files</h2>
                  {c.attachments?.length ? (
                    c.attachments.map((a) => (
                      <div className="attachment-record" key={a.id}>
                        <a href={a.download_url}>{a.filename}</a>
                        <p className="small muted">
                          {(a.size / 1024).toFixed(1)} KB ·{" "}
                          {a.integrity_checked_at
                            ? "Stored checksum checked"
                            : "Checksum check pending"}
                        </p>
                        <Disclosure title="File details">
                          <p>{a.type}</p>
                          <code>{a.sha256}</code>
                        </Disclosure>
                      </div>
                    ))
                  ) : (
                    <p className="muted">No files available in your view.</p>
                  )}
                  <hr />
                  <h2>Shared institution work</h2>
                  <p>
                    Coordination brings bureaus together. It does not replace
                    this case owner.
                  </p>
                  <a className="text-link" href="#/coordination">
                    View coordination →
                  </a>
                </aside>
              </div>
              <WorkflowPanel
                record={c}
                session={session}
                onSaved={resource.reload}
              />
              {c.can_assign && (
                <AssignmentForm
                  record={c}
                  session={session}
                  onSaved={resource.reload}
                />
              )}
            </>
          )}
        </>
      )}
    </>
  );
}
function AssignmentForm({
  record,
  session,
  onSaved,
}: {
  record: CaseRecord;
  session: Session;
  onSaved: () => void;
}) {
  const officers =
    useResource<{ id: string; name: string; bureau: string }[]>(
      "/api/officers",
    );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function assign(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    setError("");
    try {
      await api<CaseRecord>(`/api/cases/${record.id}/assignment`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": session.csrf_token,
        },
        body: JSON.stringify({
          owner_id: data.get("owner"),
          expected_version: record.version,
          reason: data.get("reason"),
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
    <Disclosure
      title="Change the case owner within this bureau"
      className="panel padded spacing-top"
    >
      <p>
        Choose the responsible officer and record why the owner is changing.
      </p>
      <ResourceState {...officers} />
      {error && (
        <div role="alert" className="validation-errors">
          <p>{error}</p>
          <button onClick={onSaved}>Reload current owner and version</button>
        </div>
      )}
      <form onSubmit={assign}>
        <div className="two-column">
          <div>
            <label htmlFor="assign-owner">New case owner *</label>
            <select id="assign-owner" name="owner" required>
              <option value="">Choose eligible officer</option>
              {officers.data
                ?.filter(
                  (o) =>
                    o.bureau === record.owner.bureau &&
                    o.id !== record.owner.id,
                )
                .map((o) => (
                  <option value={o.id} key={o.id}>
                    {o.name} · {o.bureau}
                  </option>
                ))}
            </select>
          </div>
          <div>
            <label htmlFor="assign-reason">Reason *</label>
            <input
              id="assign-reason"
              name="reason"
              minLength={5}
              maxLength={500}
              required
            />
          </div>
        </div>
        <button className="primary spacing-top" disabled={busy} type="submit">
          {busy ? "Saving…" : "Save assignment"}
        </button>
      </form>
    </Disclosure>
  );
}
