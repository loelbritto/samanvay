import test from "node:test";
import assert from "node:assert/strict";
import {
  connectionView,
  orderedConnections,
} from "../src/features/workspace/connection-model.ts";
import type {
  ConnectionCase,
  InstitutionConnection,
} from "../src/features/workspace/connection-model.ts";

const record = (
  id: string,
  changes: Partial<ConnectionCase> = {},
): ConnectionCase => ({
  id,
  owner: "Demo Officer " + id,
  bureau: "RB",
  lifecycle: "UNDER_REVIEW",
  current_institution_id: "INST-PUNE",
  historical_participation: false,
  due_at: null,
  ...changes,
});
const group = (
  changes: Partial<InstitutionConnection> = {},
): InstitutionConnection => ({
  id: "GROUP-PUNE",
  institution_id: "INST-PUNE",
  institution: "Demo Institute, Pune",
  condition_active: true,
  state: "PLANNED",
  version: 1,
  lead: "Demo Coordinator",
  lead_id: "COORD-1",
  lead_bureau: "RB",
  next_action: "Agree a response",
  due_at: null,
  can_review: true,
  cases: [],
  ...changes,
});

test("current open work excludes closed and historical participation without dropping records", () => {
  const input = group({
    cases: [
      record("A"),
      record("B", { bureau: "PGRC" }),
      record("C", { lifecycle: "DISPOSED" }),
      record("D", {
        historical_participation: true,
        current_institution_id: "INST-NAGPUR",
      }),
      record("E", {
        lifecycle: "DISPOSED",
        historical_participation: true,
        current_institution_id: "INST-NAGPUR",
      }),
    ],
  });
  const view = connectionView(input);
  assert.equal(view.activeCount, 2);
  assert.equal(view.bureauCount, 2);
  assert.deepEqual(
    view.closed.map((row) => row.id),
    ["C"],
  );
  assert.deepEqual(
    view.historical.map((row) => row.id),
    ["D", "E"],
  );
  assert.equal(view.retainedCount, 3);
  assert.deepEqual(
    [
      ...view.bureaus.flatMap((bureau) => bureau.cases),
      ...view.closed,
      ...view.historical,
    ]
      .map((row) => row.id)
      .sort(),
    ["A", "B", "C", "D", "E"],
  );
});

test("separate complaints keep their IDs and owners when they share a bureau and institution", () => {
  const input = group({
    cases: [
      record("B", { owner: "Demo Officer Two" }),
      record("A", { owner: "Demo Officer One" }),
    ],
  });
  const before = JSON.stringify(input);
  const view = connectionView(input);
  assert.equal(view.bureaus.length, 1);
  assert.deepEqual(
    view.bureaus[0].cases.map((row) => [row.id, row.owner]),
    [
      ["A", "Demo Officer One"],
      ["B", "Demo Officer Two"],
    ],
  );
  assert.equal(input.lead, "Demo Coordinator");
  assert.equal(JSON.stringify(input), before);
});

test("an institution mismatch cannot inflate current participation even if the flag is stale", () => {
  const view = connectionView(
    group({
      cases: [
        record("MOVED", {
          current_institution_id: "INST-NAGPUR",
          historical_participation: false,
        }),
      ],
    }),
  );
  assert.equal(view.activeCount, 0);
  assert.equal(view.bureauCount, 0);
  assert.deepEqual(
    view.historical.map((row) => row.id),
    ["MOVED"],
  );
});

test("institution choices prioritise active plans without changing the authorised input", () => {
  const input = [
    group({
      id: "OLD",
      condition_active: false,
      institution: "A institute, Pune",
    }),
    group({ id: "LIVE", institution: "Z institute, Nagpur" }),
  ];
  const before = JSON.stringify(input);
  assert.deepEqual(
    orderedConnections(input).map((item) => item.id),
    ["LIVE", "OLD"],
  );
  assert.equal(JSON.stringify(input), before);
  assert.deepEqual(connectionView(group()).bureaus, []);
});
