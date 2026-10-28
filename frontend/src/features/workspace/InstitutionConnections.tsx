import { useId, useState } from "react";
import { useResource } from "../../shared/useResource";
import { Badge, Icon } from "../../shared/ui";
import { dateLabel, person, words } from "../../presentation";
import { connectionView, orderedConnections } from "./connection-model";
import type { ConnectionCase, InstitutionConnection } from "./connection-model";
import "../../design-system/connections.css";

function CaseOwnerRow({ record }: { record: ConnectionCase }) {
  return (
    <li className="connection-case">
      <div className="connection-case-title">
        <a href={"#/cases/" + encodeURIComponent(record.id)}>{record.id}</a>
        <Badge tone={record.lifecycle === "DISPOSED" ? "neutral" : "blue"}>
          {words(record.lifecycle)}
        </Badge>
      </div>
      <p>
        Case owner <strong>{person(record.owner)}</strong>
      </p>
      {record.due_at && <small>Due {dateLabel(record.due_at, true)} IST</small>}
    </li>
  );
}

export function InstitutionConnections({
  compact = false,
  onExpand,
  selectedGroupId,
  onGroupChange,
}: {
  compact?: boolean;
  onExpand?: () => void;
  selectedGroupId?: string;
  onGroupChange?: (id: string) => void;
}) {
  const resource = useResource<InstitutionConnection[]>("/api/coordination");
  const [selectedId, setSelectedId] = useState("");
  const [expanded, setExpanded] = useState(false);
  const selectorId = useId(),
    headingId = useId(),
    connectionId = useId();
  const groups = orderedConnections(resource.data ?? []);
  const selected =
    groups.find((group) => group.id === (selectedGroupId ?? selectedId)) ??
    groups[0];
  const view = selected ? connectionView(selected) : null;
  const showConnections = !compact || expanded;

  return (
    <section
      className={"institution-connections" + (compact ? " is-compact" : "")}
      aria-labelledby={headingId}
    >
      <header className="connection-heading">
        <Icon name="coordination" size={22} />
        <div>
          <h2 id={headingId}>Shared institution work</h2>
          <p>One shared plan. Separate case owners.</p>
        </div>
      </header>
      {resource.loading && (
        <p className="connection-message" role="status">
          Loading shared plans…
        </p>
      )}
      {resource.error && (
        <div className="validation-errors" role="alert">
          <p>{resource.error}</p>
          <button onClick={resource.reload}>Retry shared plans</button>
        </div>
      )}
      {!resource.loading && !resource.error && !selected && (
        <div className="connection-message">
          <h3>No shared plans in your view</h3>
          <p>
            Shared plans appear here when available to your account. Your
            complaints keep their own owners and next steps.
          </p>
          <a className="text-link" href="#/coordination">
            Open coordination <Icon name="arrow" size={16} />
          </a>
        </div>
      )}
      {!resource.loading && !resource.error && selected && view && (
        <>
          {groups.length > 1 && (
            <div className="connection-selector">
              <label htmlFor={selectorId}>Institution and city</label>
              <select
                id={selectorId}
                value={selected.id}
                onChange={(event) => {
                  setSelectedId(event.target.value);
                  onGroupChange?.(event.target.value);
                }}
              >
                {groups.map((group) => (
                  <option key={group.id} value={group.id}>
                    {group.institution}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div className="connection-plan">
            <div className="connection-plan-title">
              <h3>
                <a
                  href={
                    "#/institutions/" +
                    encodeURIComponent(selected.institution_id)
                  }
                >
                  {selected.institution}
                </a>
              </h3>
              <Badge
                tone={
                  selected.state === "RESOLVED"
                    ? "neutral"
                    : selected.lead
                      ? "blue"
                      : "amber"
                }
              >
                {words(selected.state)}
              </Badge>
            </div>
            <dl className="connection-plan-details">
              <div>
                <dt>Coordination lead</dt>
                <dd>
                  {selected.lead ? person(selected.lead) : "Not assigned yet"}
                  {selected.lead_bureau && (
                    <small>{words(selected.lead_bureau)}</small>
                  )}
                </dd>
              </div>
              <div>
                <dt>Shared next step</dt>
                <dd>
                  {selected.next_action ||
                    "A shared next step has not been recorded."}
                </dd>
              </div>
            </dl>
            <div className="connection-plan-footer">
              <span>
                {view.activeCount} open{" "}
                {view.activeCount === 1 ? "complaint" : "complaints"} across{" "}
                {view.bureauCount}{" "}
                {view.bureauCount === 1 ? "bureau" : "bureaus"}
              </span>
              {selected.due_at && (
                <span>Plan due {dateLabel(selected.due_at)}</span>
              )}
            </div>
            {!selected.condition_active && (
              <p className="connection-boundary">
                This plan is retained. It is not currently flagged for
                coordination across bureaus.
              </p>
            )}
          </div>
          {compact && (
            <button
              type="button"
              className="connection-expand"
              aria-expanded={onExpand ? undefined : expanded}
              aria-controls={onExpand ? undefined : connectionId}
              onClick={() =>
                onExpand ? onExpand() : setExpanded((value) => !value)
              }
            >
              {onExpand
                ? "View shared plans"
                : expanded
                  ? "Hide case owners"
                  : "See how the work connects"}
              <Icon name="arrow" size={16} />
            </button>
          )}
          <div id={connectionId} hidden={!showConnections}>
            {view.bureaus.length ? (
              <div
                className={
                  "connection-branches" +
                  (view.bureaus.length > 1 ? " has-many" : "")
                }
              >
                {view.bureaus.map((bureau) => (
                  <section
                    key={bureau.id}
                    className="connection-bureau"
                    aria-label={words(bureau.id) + " case owners"}
                  >
                    <h4>
                      {words(bureau.id)} <span>{bureau.cases.length}</span>
                    </h4>
                    <ul>
                      {bureau.cases.map((record) => (
                        <CaseOwnerRow key={record.id} record={record} />
                      ))}
                    </ul>
                  </section>
                ))}
              </div>
            ) : (
              <p className="connection-message">
                No current open complaints remain in this shared plan.
              </p>
            )}
            {view.retainedCount > 0 && (
              <details className="connection-history">
                <summary>
                  {view.retainedCount} retained{" "}
                  {view.retainedCount === 1 ? "record" : "records"}
                </summary>
                {view.closed.length > 0 && (
                  <section>
                    <h4>Closed complaints</h4>
                    <p>Retained in the record; not counted as open work.</p>
                    <ul>
                      {view.closed.map((record) => (
                        <CaseOwnerRow key={record.id} record={record} />
                      ))}
                    </ul>
                  </section>
                )}
                {view.historical.length > 0 && (
                  <section>
                    <h4>Previous institution links</h4>
                    <p>
                      These records now belong to another institution. Their
                      earlier participation remains visible here.
                    </p>
                    <ul>
                      {view.historical.map((record) => (
                        <CaseOwnerRow key={record.id} record={record} />
                      ))}
                    </ul>
                  </section>
                )}
              </details>
            )}
            <p className="connection-boundary">
              The coordination lead agrees the shared plan. Each case owner
              remains responsible for their complaint.
            </p>
          </div>
          <footer className="connection-footer">
            <a
              className="text-link"
              href={
                "#/coordination?institution=" +
                encodeURIComponent(selected.institution_id)
              }
            >
              {selected.can_review ? "Review shared plan" : "View shared plan"}
              <Icon name="arrow" size={16} />
            </a>
            <span>Saved synthetic records</span>
          </footer>
        </>
      )}
    </section>
  );
}
