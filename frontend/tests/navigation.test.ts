import test from 'node:test';
import assert from 'node:assert/strict';
import { parseRoute } from '../src/app/navigation.ts';

test('deep links preserve case history and filtered list navigation', () => {
  assert.deepEqual(parseRoute('#/cases/DEMO-123/timeline'), { section: 'cases', id: 'DEMO-123', timeline: true, query: '', label: 'Complaints' });
  const route = parseRoute('#/cases?institution=DEMO-PUNE&lifecycle=UNDER_REVIEW');
  assert.equal(new URLSearchParams(route.query).get('institution'), 'DEMO-PUNE');
  assert.equal(route.id, undefined);
  assert.equal(parseRoute('').label, 'Work queue');
  assert.equal(parseRoute('#/missing').label, 'Page not found');
});
