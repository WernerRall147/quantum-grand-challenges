/**
 * Does the Clarity tag actually load in a browser, and do the custom tags fire?
 *
 * The built bundle containing "clarity.ms" is shape, not behaviour - this repo
 * has shipped four checks that measured shape and stayed green while the thing
 * they guarded was broken. So this drives the real page in Chromium, records
 * every clarity() call, and asserts on what was passed.
 *
 * The remote tag is stubbed: the point is that our code calls the API correctly,
 * not that Microsoft's CDN is up, and a test that silently depends on a third
 * party is a test that fails for the wrong reason.
 *
 *   node website/scripts/verify-clarity.mjs http://127.0.0.1:8090/quantum-grand-challenges
 */

import { chromium } from 'playwright';

const base = process.argv[2] || 'http://127.0.0.1:8090/quantum-grand-challenges';
const failures = [];
const checks = [];

function check(name, condition, detail = '') {
  checks.push({ name, ok: Boolean(condition), detail });
  if (!condition) failures.push(`${name}${detail ? ` - ${detail}` : ''}`);
}

const browser = await chromium.launch();
const context = await browser.newContext();

// Stub the Clarity CDN so the queue drains without a network dependency.
await context.route('**/clarity.ms/**', (route) =>
  route.fulfill({ status: 200, contentType: 'application/javascript', body: '/* stub */' }),
);

const page = await context.newPage();
const pageErrors = [];
page.on('pageerror', (e) => pageErrors.push(e.message));

// Record every clarity() call before any app code runs.
await page.addInitScript(() => {
  window.__clarityCalls = [];
  let inner;
  Object.defineProperty(window, 'clarity', {
    configurable: true,
    get() {
      return inner;
    },
    set(fn) {
      inner = (...args) => {
        window.__clarityCalls.push(args);
        return fn?.(...args);
      };
      inner.q = [];
    },
  });
});

await page.goto(`${base}/evaluate/`, { waitUntil: 'networkidle' });

const tagRequested = await page.evaluate(
  () => performance.getEntriesByType('resource').some((r) => r.name.includes('clarity.ms/tag/')),
);
check('the Clarity tag script is requested', tagRequested,
  'nothing fetched clarity.ms/tag/ - loadClarity() did not run');

const clarityDefined = await page.evaluate(() => typeof window.clarity === 'function');
check('window.clarity is callable', clarityDefined);

// Intercept the evaluate call and answer with a response shaped like the real
// one, including the trace the API now returns.
const FAKE_OPERATION_ID = '0ca524a7250d89202ef8fec8c2cf010b';
await context.route('**/api/evaluate', (route) =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    headers: { 'Access-Control-Allow-Origin': '*' },
    body: JSON.stringify({
      verdict: 'HPC_PREFERRED',
      confidence: 0.8,
      advantage_class: 'quadratic',
      recommended_algorithm: 'Classical solver',
      recommended_platform: 'HPC',
      troyer_filters: {},
      red_flags: [],
      hpc_alternative: 'Use Azure HPC',
      explanation: 'stub',
      similar_problems: [],
      references: [],
      trace: { trace_id: 'abc', operation_id: FAKE_OPERATION_ID, total_ms: 21999 },
    }),
  }),
);

await page.fill('textarea', 'Optimize a portfolio of 500 assets using mean-variance optimisation');
await page.getByRole('button', { name: /evaluate/i }).first().click();
await page.waitForFunction(
  () => (window.__clarityCalls || []).some((c) => c[0] === 'set' && c[1] === 'qgc_operation_id'),
  { timeout: 20000 },
).catch(() => {});

const calls = await page.evaluate(() => window.__clarityCalls || []);
const sets = new Map(calls.filter((c) => c[0] === 'set').map((c) => [c[1], c[2]]));
const events = calls.filter((c) => c[0] === 'event').map((c) => c[1]);

check('qgc_operation_id is tagged', sets.get('qgc_operation_id') === FAKE_OPERATION_ID,
  `got ${JSON.stringify(sets.get('qgc_operation_id'))}`);
check('qgc_verdict is tagged', sets.get('qgc_verdict') === 'HPC_PREFERRED',
  `got ${JSON.stringify(sets.get('qgc_verdict'))}`);
check('qgc_platform is tagged', sets.get('qgc_platform') === 'HPC',
  `got ${JSON.stringify(sets.get('qgc_platform'))}`);
check('qgc_latency_bucket is bucketed', sets.get('qgc_latency_bucket') === '10_30s',
  `got ${JSON.stringify(sets.get('qgc_latency_bucket'))} for 21999 ms`);
check('an evaluation event is recorded', events.includes('qgc_evaluation_shown'),
  `events: ${JSON.stringify(events)}`);
check('DEMO MODE was not tagged on a good response', !sets.has('qgc_demo_mode'));

// Now the failure path: the site renders a plausible DEMO_MODE page when the
// backend call fails, which is why it has to be countable.
await page.evaluate(() => { window.__clarityCalls = []; });
await context.unroute('**/api/evaluate');
await context.route('**/api/evaluate', (route) => route.abort());

await page.fill('textarea', 'a problem that will fail');
await page.getByRole('button', { name: /evaluate/i }).first().click();
await page.waitForFunction(
  () => (window.__clarityCalls || []).some((c) => c[0] === 'set' && c[1] === 'qgc_demo_mode'),
  { timeout: 20000 },
).catch(() => {});

const demoCalls = await page.evaluate(() => window.__clarityCalls || []);
const demoSets = new Map(demoCalls.filter((c) => c[0] === 'set').map((c) => [c[1], c[2]]));
const demoEvents = demoCalls.filter((c) => c[0] === 'event').map((c) => c[1]);

check('DEMO MODE is tagged when the backend call fails',
  demoSets.get('qgc_demo_mode') === 'true', `got ${JSON.stringify(demoSets.get('qgc_demo_mode'))}`);
check('a DEMO MODE event is recorded', demoEvents.includes('qgc_demo_mode'),
  `events: ${JSON.stringify(demoEvents)}`);

check('no uncaught page errors', pageErrors.length === 0, pageErrors.join('; '));

await browser.close();

for (const c of checks) {
  console.log(`${c.ok ? 'PASS' : 'FAIL'}  ${c.name}${c.ok || !c.detail ? '' : ` (${c.detail})`}`);
}
console.log(`\n${checks.length - failures.length}/${checks.length} checks passed`);
process.exit(failures.length ? 1 : 0);
