import type { CaseRecord } from "../../api";
import { Icon } from "../../shared/ui";
import { dateLabel, person, words } from "../../presentation";
import { isOverdue } from "./queue-model";

export function FocusCase({
  record,
  asOf,
}: {
  record: CaseRecord;
  asOf: string;
}) {
  const late = isOverdue(record, asOf);
  return (
    <section className="focus-case" aria-labelledby="focus-case-title">
      <div className="focus-case-heading">
        <h2 id="focus-case-title">Next in your queue</h2>
        <span className="focus-order">
          <Icon name="clock" size={15} /> Earliest due first
        </span>
      </div>
      <h3>
        <a href={"#/cases/" + record.id}>{record.subject}</a>
      </h3>
      <p className="focus-case-origin">
        {record.institution_name}, {record.city} <span>· {record.id}</span>
      </p>
      <div className="focus-responsibility">
        <div className="focus-owner">
          <span className="owner-initials" aria-hidden="true">
            {person(record.owner.name)
              .split(" ")
              .slice(0, 2)
              .map((word) => word[0])
              .join("")}
          </span>
          <div>
            <span>Case owner</span>
            <strong>{person(record.owner.name)}</strong>
            <small>{words(record.owner.bureau)}</small>
          </div>
        </div>
        <div className="focus-deadline">
          <span>{late ? "Overdue" : "Due date"}</span>
          <strong>{dateLabel(record.expected_disposal_date)}</strong>
        </div>
      </div>
      <div className="focus-next">
        <Icon name="arrow" size={18} />
        <div>
          <span>Next step</span>
          <p>{record.next_action}</p>
        </div>
      </div>
      <div className="focus-footer">
        <span>
          {record.transfer_state === "PENDING"
            ? "Transfer pending · current owner remains responsible"
            : words(record.lifecycle)}
        </span>
        <a className="button" href={"#/cases/" + record.id}>
          Open complaint <Icon name="arrow" size={16} />
        </a>
      </div>
    </section>
  );
}
