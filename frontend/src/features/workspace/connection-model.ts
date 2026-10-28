/** Read-only presentation of an already authorised coordination response. */
export type ConnectionCase = {
  id: string;
  owner: string;
  bureau: string;
  lifecycle: string;
  current_institution_id: string;
  historical_participation: boolean;
  due_at: string | null;
};

export type InstitutionConnection = {
  id: string;
  institution_id: string;
  institution: string;
  condition_active: boolean;
  state: string;
  version: number;
  lead: string | null;
  lead_id: string | null;
  lead_bureau: string | null;
  next_action: string;
  due_at: string | null;
  can_review: boolean;
  cases: ConnectionCase[];
};

export function connectionView(group: InstitutionConnection) {
  const active: ConnectionCase[] = [];
  const closed: ConnectionCase[] = [];
  const historical: ConnectionCase[] = [];
  for (const record of group.cases) {
    // The server flag is authoritative; the ID comparison also guards stale data.
    if (
      record.historical_participation ||
      record.current_institution_id !== group.institution_id
    ) {
      historical.push(record);
    } else if (record.lifecycle === "DISPOSED") {
      closed.push(record);
    } else {
      active.push(record);
    }
  }
  const byBureau = new Map<string, ConnectionCase[]>();
  for (const record of active) {
    const rows = byBureau.get(record.bureau) ?? [];
    rows.push(record);
    byBureau.set(record.bureau, rows);
  }
  const bureaus = [...byBureau]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([id, cases]) => ({
      id,
      cases: cases.slice().sort((a, b) => a.id.localeCompare(b.id)),
    }));
  return {
    activeCount: active.length,
    bureauCount: bureaus.length,
    bureaus,
    closed,
    historical,
    retainedCount: closed.length + historical.length,
  };
}

export function orderedConnections(groups: readonly InstitutionConnection[]) {
  return groups
    .slice()
    .sort(
      (a, b) =>
        Number(b.condition_active) - Number(a.condition_active) ||
        a.institution.localeCompare(b.institution) ||
        a.id.localeCompare(b.id),
    );
}
