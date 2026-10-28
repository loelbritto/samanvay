import test from 'node:test';
import assert from 'node:assert/strict';
import { api, ApiError } from '../src/api.ts';

test('cancelled navigation is not reported as a server outage', async () => {
  const previous = globalThis.fetch;
  const controller = new AbortController();
  controller.abort();
  const abort = new DOMException('Cancelled', 'AbortError');
  globalThis.fetch = async () => { throw abort; };
  try { await assert.rejects(api('/api/cases', { signal: controller.signal }), error => error === abort); }
  finally { globalThis.fetch = previous; }
});

test('network failures do not imply a successful write', async () => {
  const previous = globalThis.fetch;
  globalThis.fetch = async () => { throw new TypeError('offline'); };
  try { await assert.rejects(api('/api/cases', { method: 'POST' }), error => error instanceof ApiError && error.status === 0 && error.message.includes('No success is confirmed')); }
  finally { globalThis.fetch = previous; }
});
