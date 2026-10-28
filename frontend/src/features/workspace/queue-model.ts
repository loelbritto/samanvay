import type { CaseRecord } from "../../api";

/** Deadline state uses the server's context clock, never the device's real clock. */
export function isOverdue(
  record: Pick<CaseRecord, "due_at" | "lifecycle">,
  asOf?: string,
): boolean {
  if (!asOf || !record.due_at || record.lifecycle === "DISPOSED") return false;
  const due = Date.parse(record.due_at),
    at = Date.parse(asOf);
  return Number.isFinite(due) && Number.isFinite(at) && due < at;
}
