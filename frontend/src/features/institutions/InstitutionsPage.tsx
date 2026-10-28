import type { CaseRecord, Institution } from "../../api";
import { Badge, PageHeading, Notice, EmptyState, Icon } from "../../shared/ui";
import { ResourceState, useResource } from "../../ui";
import { LiveTable } from "../cases/CaseList";

export function LiveInstitutions({ id }: { id?: string }) {
  const institutions = useResource<Institution[]>("/api/institutions");
  const cases = useResource<{ total: number; items: CaseRecord[] }>(
    "/api/cases?institution=" + encodeURIComponent(id ?? "all"),
  );
  const chosen = institutions.data?.find((i) => i.id === id);
  return (
    <>
      <PageHeading
        eyebrow="Institution directory"
        title={chosen ? `${chosen.name}, ${chosen.city}` : "Institutions"}
      >
        Choose an institution to see its complaints and recorded activity. Check
        the city: similar names may refer to different institutions.
      </PageHeading>
      <ResourceState {...institutions} />
      {id && institutions.data && !chosen ? (
        <EmptyState title="Institution not found">
          Select a fictional institution from the directory.
        </EmptyState>
      ) : chosen ? (
        <>
          <section className="panel padded">
            <Badge>Fictional institution · {chosen.id}</Badge>
            <dl className="evidence-fields">
              <div>
                <dt>City / region</dt>
                <dd>
                  {chosen.city} · {chosen.region}
                </dd>
              </div>
              {chosen.aliases.map((a) => (
                <div key={a.alias}>
                  <dt>Stored alias</dt>
                  <dd>
                    {a.alias}
                    <span className="cell-sub">{a.provenance}</span>
                  </dd>
                </div>
              ))}
            </dl>
            <Notice>
              A shared institution can have separate complaints. Visit
              Coordination to review its shared plan and compare evidence.
            </Notice>
          </section>
          <section className="panel spacing-top">
            <div className="panel-heading">
              <h2>Complaints at this institution</h2>
            </div>
            <ResourceState {...cases} />
            {cases.data && (
              <>
                <p className="padded small muted">
                  {cases.data.total} cases in your scope. Up to 200 recent cases
                  shown.
                </p>
                <LiveTable records={cases.data.items} />
                <div className="padded">
                  <a
                    className="text-link"
                    href={"#/cases?institution=" + chosen.id}
                  >
                    Browse all cases for this institution →
                  </a>
                </div>
              </>
            )}
          </section>
        </>
      ) : (
        <div className="institution-grid">
          {institutions.data?.map((i) => (
            <article className="panel padded" key={i.id}>
              <Badge>Fictional institution · {i.city}</Badge>
              <h2 className="spacing-top">
                {i.name}, {i.city}
              </h2>
              <p className="mono">{i.id}</p>
              <a href={`#/institutions/${i.id}`} className="button secondary">
                Open {i.city} institution <Icon name="arrow" size={15} />
              </a>
            </article>
          ))}
        </div>
      )}
    </>
  );
}
