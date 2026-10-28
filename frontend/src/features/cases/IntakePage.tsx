import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "../../api";
import type { CaseRecord, Institution, Session } from "../../api";
import { PageHeading, Notice } from "../../shared/ui";
import { ResourceState, useResource } from "../../ui";

export function LiveIntake({ session }: { session: Session }) {
  const institutions = useResource<Institution[]>("/api/institutions");
  const [original, setOriginal] = useState("");
  const [requestKey, setRequestKey] = useState(() => crypto.randomUUID());
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const eligible = session.user.memberships.some((m) =>
    ["RB_OFFICER", "PGRC_OFFICER", "REGIONAL_OFFICER"].includes(m.role),
  );
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const values = new FormData(form);
    setBusy(true);
    setError("");
    const payload = {
      institution_id: values.get("institution"),
      original_institution_text: values.get("originalInstitution"),
      received_date: values.get("received"),
      subject: values.get("subject"),
      description: values.get("description"),
      category: values.get("category"),
      next_action: values.get("nextAction"),
      expected_disposal_date: values.get("deadline") || null,
      complainant_token: values.get("complainant"),
      synthetic: true,
      facts: {
        incident_reference: values.get("incident_reference") || "",
        incident_date: values.get("incident_date") || null,
        receipt_reference: values.get("receipt_reference") || "",
        amount: values.get("amount") || "",
        remedy: values.get("remedy") || "",
      },
    };
    const body = new FormData();
    body.append("payload", JSON.stringify(payload));
    for (const file of values.getAll("evidence")) {
      if (file instanceof File && file.size) body.append("files", file);
    }
    try {
      const saved = await api<CaseRecord>("/api/cases", {
        method: "POST",
        body,
        headers: {
          "X-CSRF-Token": session.csrf_token,
          "Idempotency-Key": requestKey,
        },
      });
      location.hash = `#/cases/${saved.id}`;
    } catch (err) {
      setError((err as Error).message);
      requestAnimationFrame(() =>
        document.getElementById("save-error")?.focus(),
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading eyebrow="New case" title="New complaint">
        Record a fictional complaint and decide what should happen next.
      </PageHeading>
      <Notice>
        Use fictional data only. This case will be owned by:{" "}
        <strong>{session.user.display_name}</strong>. Choose the institution and
        city carefully. Connected complaints can be reviewed after saving.
      </Notice>
      <ResourceState {...institutions} />
      {!eligible ? (
        <Notice tone="amber">
          This role cannot create complaints. Administration does not grant
          officer intake authority.
        </Notice>
      ) : (
        institutions.data && (
          <form
            className="panel padded spacing-top intake-form"
            onSubmit={submit}
          >
            {error && (
              <div
                className="validation-errors"
                id="save-error"
                tabIndex={-1}
                role="alert"
              >
                <p>{error}</p>
                <p>
                  The form is retained. Retry unchanged content with this
                  request key; no success is confirmed.
                </p>
                {error.includes("request key") && (
                  <button
                    type="button"
                    onClick={() => {
                      setRequestKey(crypto.randomUUID());
                      setError("");
                    }}
                  >
                    Start a separate intake request
                  </button>
                )}
              </div>
            )}
            <h2>1. Describe the complaint</h2>
            <div className="two-column">
              <div>
                <label htmlFor="new-inst">Institution and city *</label>
                <select
                  id="new-inst"
                  name="institution"
                  required
                  onChange={(e) => {
                    const i = institutions.data?.find(
                      (i) => i.id === e.target.value,
                    );
                    setOriginal(i ? `${i.name}, ${i.city}` : "");
                  }}
                >
                  <option value="">Choose the institution and city</option>
                  {institutions.data.map((i) => (
                    <option key={i.id} value={i.id}>
                      {i.name}, {i.city} · {i.id}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="new-received">Received date *</label>
                <input id="new-received" name="received" type="date" required />
              </div>
            </div>
            <label htmlFor="new-original">
              Institution text as originally supplied *
            </label>
            <input
              id="new-original"
              name="originalInstitution"
              required
              maxLength={500}
              value={original}
              onChange={(e) => setOriginal(e.target.value)}
            />
            <label htmlFor="new-subject">Subject *</label>
            <input
              id="new-subject"
              name="subject"
              minLength={3}
              maxLength={200}
              required
            />
            <label htmlFor="new-category">Category *</label>
            <select id="new-category" name="category" required>
              <option value="">Choose category</option>
              <option>Fee refund</option>
              <option>Faculty grievance</option>
              <option>Infrastructure</option>
              <option>Other</option>
            </select>
            <label htmlFor="new-description">
              Original complaint description *
            </label>
            <textarea
              id="new-description"
              name="description"
              rows={5}
              minLength={10}
              maxLength={20000}
              required
            />
            <label htmlFor="new-token">Fictional complainant reference *</label>
            <input
              id="new-token"
              name="complainant"
              placeholder="DEMO-STU-999"
              pattern="DEMO-.+"
              required
              maxLength={80}
            />
            <details className="spacing-top">
              <summary>Add incident or receipt details (optional)</summary>
              {[
                "incident_reference",
                "incident_date",
                "receipt_reference",
                "amount",
                "remedy",
              ].map((field) => (
                <div key={field}>
                  <label htmlFor={"fact-" + field}>
                    {field.replaceAll("_", " ")}
                  </label>
                  <input
                    id={"fact-" + field}
                    name={field}
                    type={field === "incident_date" ? "date" : "text"}
                    maxLength={field === "remedy" ? 300 : 80}
                  />
                </div>
              ))}
            </details>
            <h2 className="spacing-top">2. Plan the next step</h2>
            <label htmlFor="new-action">What happens next? *</label>
            <input
              id="new-action"
              name="nextAction"
              required
              minLength={3}
              maxLength={500}
            />
            <div className="two-column">
              <div>
                <label htmlFor="new-deadline">Due date (optional)</label>
                <input id="new-deadline" name="deadline" type="date" />
                <p className="small muted">
                  Prototype date entered by the officer; no official timetable
                  is implied.
                </p>
              </div>
              <div>
                <label htmlFor="new-evidence">
                  Supporting evidence (optional)
                </label>
                <input
                  id="new-evidence"
                  name="evidence"
                  type="file"
                  multiple
                  accept=".txt,.pdf,.png,.jpg,.jpeg"
                />
                <p className="small muted">
                  Up to 3 files, 5 MiB each. PDF, PNG, JPEG or UTF-8 TXT.
                  Private storage; no malware scanning service.
                </p>
              </div>
            </div>
            <button className="primary" type="submit" disabled={busy}>
              {busy ? "Saving complaint…" : "Create synthetic complaint"}
            </button>
            <p className="small muted">
              The complaint and its files are saved together. Each new complaint
              keeps its own record.
            </p>
          </form>
        )
      )}
    </>
  );
}
