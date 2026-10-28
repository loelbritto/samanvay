import { useState } from "react";
import type { CaseRecord, Session } from "../../api";
import { PageHeading, EmptyState } from "../../shared/ui";
import {
  CaseFilters,
  ResourceState,
  useResource,
  filterParams,
  initialFilters,
} from "../../ui";
import { mayCreate } from "../../presentation";
import { LiveTable } from "./CaseList";

export function LiveCases({
  query,
  session,
}: {
  query: URLSearchParams;
  session: Session;
}) {
  const [filters, setFilters] = useState(() => initialFilters(query)),
    [page, setPage] = useState(0);
  const params = filterParams(filters);
  params.set("offset", String(page * 25));
  params.set("limit", "25");
  const resource = useResource<{ total: number; items: CaseRecord[] }>(
    "/api/cases?" + params,
  );
  return (
    <>
      <PageHeading
        eyebrow="Case workspace"
        title="Complaints"
        action={
          mayCreate(session) ? (
            <a className="button primary" href="#/cases/new">
              + New complaint
            </a>
          ) : undefined
        }
      >
        Find a case, check its owner and follow the next step.
      </PageHeading>
      <CaseFilters
        prefix="case"
        filters={filters}
        onChange={(f) => {
          setFilters(f);
          setPage(0);
        }}
      />
      <div className="spacing-top">
        <ResourceState {...resource} />
      </div>
      {resource.data && !resource.loading && (
        <>
          <div className="section-heading">
            <p role="status">{resource.data.total} complaints in your scope</p>
            <span className="small muted">Page {page + 1}</span>
          </div>
          {resource.data.items.length ? (
            <section className="panel">
              <LiveTable records={resource.data.items} />
            </section>
          ) : (
            <EmptyState title="No matching complaints">
              Try a different search or clear the filters.
            </EmptyState>
          )}
          <div className="pagination">
            <button disabled={!page} onClick={() => setPage((p) => p - 1)}>
              ← Previous
            </button>
            <button
              disabled={(page + 1) * 25 >= resource.data.total}
              onClick={() => setPage((p) => p + 1)}
            >
              Next →
            </button>
          </div>
        </>
      )}
    </>
  );
}
