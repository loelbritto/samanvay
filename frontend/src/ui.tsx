import type { ReactNode } from "react";
import type { Institution } from "./api";
import { words } from "./presentation";

import { useResource } from "./shared/useResource";
export { useResource } from "./shared/useResource";

export function ResourceState({
  loading,
  error,
  reload,
}: {
  loading: boolean;
  error: string;
  reload: () => void;
}) {
  return loading ? (
    <p className="loading-state" role="status">
      Loading your workspace…
    </p>
  ) : error ? (
    <div role="alert" className="validation-errors">
      <p>{error}</p>
      <button onClick={reload}>Try again</button>
    </div>
  ) : null;
}
export function Disclosure({
  title,
  children,
  className = "",
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <details className={"disclosure " + className}>
      <summary>{title}</summary>
      <div className="disclosure-content">{children}</div>
    </details>
  );
}
export function Fields({ values }: { values: Record<string, unknown> }) {
  return (
    <dl className="readable-fields">
      {Object.entries(values)
        .filter(([, v]) => v !== null && v !== undefined && v !== "")
        .map(([key, value]) => (
          <div key={key}>
            <dt>{words(key)}</dt>
            <dd>
              {typeof value === "object" ? (
                Array.isArray(value) ? (
                  value.map(String).join(", ")
                ) : (
                  <Fields values={value as Record<string, unknown>} />
                )
              ) : (
                String(value)
              )}
            </dd>
          </div>
        ))}
    </dl>
  );
}
export const emptyFilters: Record<string, string> = {
  q: "",
  bureau: "all",
  institution: "all",
  region: "all",
  category: "all",
  lifecycle: "all",
  received_from: "",
  received_to: "",
};
export function initialFilters(query: URLSearchParams) {
  return Object.fromEntries(
    Object.entries(emptyFilters).map(([k, v]) => [k, query.get(k) ?? v]),
  );
}
export const filterParams = (filters: Record<string, string>) =>
  new URLSearchParams(
    Object.entries(filters).filter(([, v]) => v && v !== "all"),
  );

export function CaseFilters({
  filters,
  onChange,
  prefix,
}: {
  filters: Record<string, string>;
  onChange: (filters: Record<string, string>) => void;
  prefix: string;
}) {
  const institutions = useResource<Institution[]>("/api/institutions");
  const change = (key: string, value: string) =>
    onChange({ ...filters, [key]: value });
  const extras = Object.entries(filters).filter(
    ([key, value]) =>
      !["q", "lifecycle"].includes(key) && value && value !== "all",
  ).length;
  return (
    <section className="panel filter-panel" aria-label="Search and filters">
      <div className="filter-bar">
        <div className="search-field">
          <label htmlFor={prefix + "-search"}>Find a case</label>
          <input
            id={prefix + "-search"}
            type="search"
            maxLength={200}
            placeholder="Case reference, institution or complaint…"
            value={filters.q}
            onChange={(e) => change("q", e.target.value)}
          />
        </div>
        <div>
          <label htmlFor={prefix + "-status"}>Status</label>
          <select
            id={prefix + "-status"}
            value={filters.lifecycle}
            onChange={(e) => change("lifecycle", e.target.value)}
          >
            <option value="all">All statuses</option>
            {[
              "RECEIVED",
              "ASSIGNED",
              "UNDER_REVIEW",
              "AWAITING_INFORMATION",
              "DISPOSED",
            ].map((s) => (
              <option key={s} value={s}>
                {words(s)}
              </option>
            ))}
          </select>
        </div>
        <button
          className="text-button"
          onClick={() => onChange({ ...emptyFilters })}
        >
          Clear filters
        </button>
      </div>
      <Disclosure
        title={`More filters${extras ? " · " + extras + " applied" : ""}`}
      >
        <div className="filters">
          <div>
            <label htmlFor={prefix + "-institution"}>Institution</label>
            <select
              id={prefix + "-institution"}
              value={filters.institution}
              onChange={(e) => change("institution", e.target.value)}
            >
              <option value="all">All institutions</option>
              {institutions.data?.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.name}, {i.city} · {i.id}
                </option>
              ))}
              {filters.institution !== "all" &&
                !institutions.data?.some(
                  (i) => i.id === filters.institution,
                ) && (
                  <option value={filters.institution}>
                    {filters.institution}
                  </option>
                )}
            </select>
            {institutions.error && (
              <span role="status">
                Institution choices unavailable.{" "}
                <button className="text-button" onClick={institutions.reload}>
                  Retry
                </button>
              </span>
            )}
          </div>
          <div>
            <label htmlFor={prefix + "-bureau"}>Current bureau</label>
            <select
              id={prefix + "-bureau"}
              value={filters.bureau}
              onChange={(e) => change("bureau", e.target.value)}
            >
              <option value="all">All bureaus</option>
              {["RB", "PGRC"].map((b) => (
                <option key={b} value={b}>
                  {words(b)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor={prefix + "-region"}>Region</label>
            <select
              id={prefix + "-region"}
              value={filters.region}
              onChange={(e) => change("region", e.target.value)}
            >
              <option value="all">All regions</option>
              {Array.from(
                new Set(institutions.data?.map((i) => i.region) ?? []),
              ).map((r) => (
                <option key={r} value={r}>
                  {words(r)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor={prefix + "-category"}>Complaint category</label>
            <select
              id={prefix + "-category"}
              value={filters.category}
              onChange={(e) => change("category", e.target.value)}
            >
              <option value="all">All categories</option>
              {[
                "Fee refund",
                "Faculty grievance",
                "Infrastructure",
                "Other",
              ].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
            <small>Only complaints you may read are included.</small>
          </div>
          {[
            ["received_from", "Received on or after"],
            ["received_to", "Received before"],
          ].map(([key, label]) => (
            <div key={key}>
              <label htmlFor={prefix + "-" + key}>{label}</label>
              <input
                id={prefix + "-" + key}
                type="date"
                value={filters[key]}
                onChange={(e) => change(key, e.target.value)}
              />
            </div>
          ))}
        </div>
        <p className="small muted">
          “Received before” excludes the selected day. Dates use India Standard
          Time.
        </p>
      </Disclosure>
    </section>
  );
}
