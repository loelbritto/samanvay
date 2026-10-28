import test from "node:test";
import assert from "node:assert/strict";
import { isOverdue } from "../src/features/workspace/queue-model.ts";

test("overdue uses the supplied context clock and excludes retained closed records", () => {
  const record = { due_at: "2026-10-28T09:00:00Z", lifecycle: "UNDER_REVIEW" };
  assert.equal(isOverdue(record, "2026-10-28T10:00:00Z"), true);
  assert.equal(isOverdue(record, "2026-10-28T08:00:00Z"), false);
  assert.equal(isOverdue(record, record.due_at), false);
  assert.equal(
    isOverdue({ ...record, lifecycle: "DISPOSED" }, "2026-10-29T10:00:00Z"),
    false,
  );
  assert.equal(
    isOverdue({ ...record, due_at: null }, "2026-10-29T10:00:00Z"),
    false,
  );
  assert.equal(isOverdue(record), false);
  assert.equal(isOverdue(record, "invalid"), false);
});
