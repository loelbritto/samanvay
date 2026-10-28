import type { CaseRecord } from "../../api";
import { isOverdue } from "../workspace/queue-model";
import { Badge, Icon } from "../../shared/ui";
import {
  dateLabel as date,
  person,
  words as titleState,
} from "../../presentation";

export function LiveTable({
  records,
  asOf,
}: {
  records: CaseRecord[];
  asOf?: string;
}) {
  return (
    <div className="case-list" aria-label="Complaints in your scope">
      {records.map((c) => (
        <article className="case-row" key={c.id}>
          <div className="case-row-main">
            <span className="case-reference">{c.id}</span>
            <h3>
              <a href={"#/cases/" + c.id}>{c.subject}</a>
            </h3>
            <p>
              {c.institution_name}, {c.city}
            </p>
          </div>
          <div className="case-row-owner">
            <span className="field-caption">Case owner</span>
            <strong>{person(c.owner.name)}</strong>
            <small>{titleState(c.owner.bureau)}</small>
          </div>
          <div className="case-row-status">
            <Badge
              tone={
                c.lifecycle === "DISPOSED"
                  ? "neutral"
                  : c.lifecycle === "AWAITING_INFORMATION"
                    ? "amber"
                    : "blue"
              }
            >
              {titleState(c.lifecycle)}
            </Badge>
            <small className={isOverdue(c, asOf) ? "due-overdue" : undefined}>
              {isOverdue(c, asOf)
                ? "Overdue · "
                : c.expected_disposal_date
                  ? "Due "
                  : ""}
              {date(c.expected_disposal_date)}
            </small>
          </div>
          <div className="case-row-next">
            <span className="field-caption">Next step</span>
            <p>{c.next_action}</p>
          </div>
          <a
            className="row-arrow"
            href={"#/cases/" + c.id}
            aria-label={"Open " + c.id}
          >
            <Icon name="arrow" />
          </a>
        </article>
      ))}
    </div>
  );
}
