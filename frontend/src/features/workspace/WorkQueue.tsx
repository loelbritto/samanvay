import { useState } from "react";
import type { CaseRecord, Session } from "../../api";
import { PageHeading, EmptyState, Icon } from "../../shared/ui";
import { ResourceState, useResource } from "../../ui";
import { dateLabel, mayCreate } from "../../presentation";
import { LiveTable } from "../cases/CaseList";
import { FocusCase } from "./FocusCase";
import { InstitutionConnections } from "./InstitutionConnections";

type Queue = "open" | "overdue" | "mine";
type Workspace = {
  as_of: string;
  queue: Queue;
  counts: Record<Queue | "total", number>;
  matching: number;
  limit: number;
  items: CaseRecord[];
};

export function WorkQueue({ session }: { session: Session }) {
  const [queue, setQueue] = useState<Queue>("open");
  const [view, setView] = useState<"cases" | "institutions">("cases");
  const [selectedGroupId, setSelectedGroupId] = useState("");
  const resource = useResource<Workspace>("/api/workspace?queue=" + queue);
  const data = resource.data;
  function openSharedPlans() {
    setView("institutions");
    requestAnimationFrame(() =>
      document.getElementById("workspace-plan-view")?.focus(),
    );
  }
  return (
    <>
      <PageHeading
        title="Your workspace"
        action={
          mayCreate(session) ? (
            <a className="button primary" href="#/cases/new">
              New complaint <Icon name="arrow" size={16} />
            </a>
          ) : undefined
        }
      >
        Every complaint has an owner. Every team has a next step.
      </PageHeading>
      <div className="workspace-viewbar">
        <div className="workspace-view-switch" aria-label="Workspace view">
          <button
            aria-pressed={view === "cases"}
            onClick={() => setView("cases")}
          >
            <Icon name="cases" size={18} />
            Case queue
          </button>
          <button
            aria-pressed={view === "institutions"}
            onClick={() => setView("institutions")}
          >
            <Icon name="coordination" size={18} />
            Shared plans
          </button>
        </div>
        <span className="workspace-date">
          {data
            ? dateLabel(data.as_of) + " · demo date"
            : "Persistent synthetic workspace"}
        </span>
      </div>
      {view === "institutions" ? (
        <section
          id="workspace-plan-view"
          aria-label="Shared institution plans"
          tabIndex={-1}
        >
          <InstitutionConnections
            selectedGroupId={selectedGroupId}
            onGroupChange={setSelectedGroupId}
          />
        </section>
      ) : (
        <div className="desk-layout">
          <section
            className="queue-workspace"
            aria-label="Complaint work queue"
          >
            <div className="queue-toolbar">
              <div className="queue-tabs" aria-label="Show complaints">
                {(
                  [
                    ["open", "All open"],
                    ["overdue", "Overdue"],
                    ["mine", "Assigned to me"],
                  ] as const
                ).map(([key, label]) => (
                  <button
                    key={key}
                    aria-pressed={queue === key}
                    onClick={() => setQueue(key)}
                  >
                    {label}
                    {data && <span className="count">{data.counts[key]}</span>}
                  </button>
                ))}
              </div>
              <button className="text-button" onClick={resource.reload}>
                Refresh
              </button>
            </div>
            <ResourceState {...resource} />
            {data && !resource.loading && (
              <>
                {data.items.length ? (
                  <>
                    <FocusCase record={data.items[0]} asOf={data.as_of} />
                    {data.items.length > 1 && (
                      <>
                        <div className="queue-rest-heading">
                          <h2>Also in your queue</h2>
                          <span>{data.items.length - 1} shown</span>
                        </div>
                        <LiveTable
                          records={data.items.slice(1)}
                          asOf={data.as_of}
                        />
                      </>
                    )}
                  </>
                ) : (
                  <EmptyState
                    title={
                      queue === "overdue"
                        ? "No overdue complaints"
                        : "No complaints in this queue"
                    }
                  >
                    Try another view or browse all complaints, including closed
                    records.
                  </EmptyState>
                )}
                <div className="queue-footer">
                  <span>
                    Showing {data.items.length} of {data.matching} matching
                    complaints
                  </span>
                  <a href="#/cases">
                    All {data.counts.total} records{" "}
                    <Icon name="arrow" size={16} />
                  </a>
                </div>
              </>
            )}
          </section>
          <aside
            className="desk-context"
            aria-label="Shared work and review guidance"
          >
            <InstitutionConnections
              compact
              selectedGroupId={selectedGroupId}
              onGroupChange={setSelectedGroupId}
              onExpand={openSharedPlans}
            />
            <section className="desk-review-note">
              <Icon name="check" size={20} />
              <h2>You make the decision.</h2>
              <p>
                Suggested connections are a starting point. Review the evidence
                before recording a relationship.
              </p>
              <a href="#/coordination?view=reviews">
                Open evidence reviews <Icon name="arrow" size={15} />
              </a>
            </section>
          </aside>
        </div>
      )}
    </>
  );
}
