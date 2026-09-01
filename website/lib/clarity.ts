/**
 * Microsoft Clarity: the browser half of end-to-end traceability.
 *
 * `docs/tracing.md` covers what the API did during a request. It starts at
 * `POST /api/evaluate` and ends when the response is written, which leaves the
 * part a person actually experiences untraced: landing on the page, typing a
 * problem, ticking "generate code", and then waiting twenty to fifty seconds
 * for an answer.
 *
 * The bridge between the two halves is `tagEvaluation()`. Every evaluate
 * response carries `trace.operation_id`, and setting it as a Clarity custom tag
 * means a session recording can be taken to Application Insights and resolved
 * to the exact backend trace behind what you just watched someone see. Without
 * it you have two tools that each know half of a story and cannot be joined.
 *
 * Off unless `NEXT_PUBLIC_CLARITY_PROJECT_ID` is set at build time. The site is
 * a static export, so that value is inlined during `npm run build`; unsetting
 * the repository variable and rebuilding removes the script entirely, with no
 * code change. Nothing here throws: analytics that can break the evaluator is
 * worse than no analytics.
 */

export const CLARITY_PROJECT_ID = process.env.NEXT_PUBLIC_CLARITY_PROJECT_ID || '';

type ClarityFn = (...args: unknown[]) => void;

declare global {
  interface Window {
    clarity?: ClarityFn;
  }
}

export function isClarityConfigured(): boolean {
  return CLARITY_PROJECT_ID.length > 0;
}

/**
 * The official snippet, inlined rather than added as a dependency.
 *
 * It is injected from `_app.tsx` after mount so it never blocks first paint,
 * and it queues calls made before the remote script arrives - `window.clarity`
 * is defined synchronously as a queue, so tagging immediately after a fetch
 * resolves is safe even on a cold load.
 */
export function loadClarity(): void {
  if (typeof window === 'undefined' || !isClarityConfigured()) return;
  if (window.clarity) return; // already loaded, or loaded twice by a re-render

  try {
    /* eslint-disable @typescript-eslint/no-explicit-any */
    const w = window as any;
    w.clarity = w.clarity || function (...args: unknown[]) {
      (w.clarity.q = w.clarity.q || []).push(args);
    };
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.clarity.ms/tag/' + CLARITY_PROJECT_ID;
    const first = document.getElementsByTagName('script')[0];
    if (first && first.parentNode) {
      first.parentNode.insertBefore(script, first);
    } else {
      document.head.appendChild(script);
    }
    /* eslint-enable @typescript-eslint/no-explicit-any */
  } catch {
    // A blocked or failed tag must not affect the page.
  }
}

/** Set a custom tag. Filterable under Filters > Custom tags in the dashboard. */
export function tag(key: string, value: string): void {
  if (typeof window === 'undefined' || !window.clarity) return;
  if (!value) return;
  try {
    // Clarity caps tag values at 255 characters and drops longer ones.
    window.clarity('set', key, value.slice(0, 255));
  } catch {
    // Ignored on purpose - see the module comment.
  }
}

/** Record a named event, so sessions can be filtered by what happened in them. */
export function event(name: string): void {
  if (typeof window === 'undefined' || !window.clarity) return;
  try {
    window.clarity('event', name);
  } catch {
    // Ignored on purpose.
  }
}

export interface TaggableResult {
  verdict?: string;
  recommended_platform?: string;
  trace?: { operation_id?: string; total_ms?: number };
  code_requested?: boolean;
}

/** Bucketed so the dashboard can filter on it; an exact millisecond value per
 *  request would make the filter useless. Exported for the unit test. */
export function latencyBucket(totalMs: number): string {
  if (totalMs < 10000) return 'under_10s';
  if (totalMs < 30000) return '10_30s';
  if (totalMs < 60000) return '30_60s';
  return 'over_60s';
}

/**
 * Tag one evaluation. This is what makes the two halves a single trace.
 *
 * `qgc_operation_id` is the `operation_Id` in Application Insights:
 *
 *     union requests, dependencies
 *     | where operation_Id == "<the tag value>"
 *
 * `qgc_verdict` and `qgc_demo_mode` are here because they answer questions
 * neither tool can answer alone: whether people abandon during the wait, and
 * how often a real visitor saw DEMO MODE. The uptime probe checks the API; it
 * has never checked what a browser actually rendered.
 */
export function tagEvaluation(result: TaggableResult | null | undefined): void {
  if (!result) return;

  const operationId = result.trace?.operation_id;
  if (operationId) tag('qgc_operation_id', operationId);

  if (result.verdict) tag('qgc_verdict', result.verdict);
  if (result.recommended_platform) tag('qgc_platform', result.recommended_platform);
  if (result.code_requested) tag('qgc_code_requested', 'true');

  if (result.verdict === 'DEMO_MODE') {
    // The failure that looks like a feature: the site renders a plausible page
    // when the backend call fails, so a broken demo and a working one look the
    // same from outside.
    tag('qgc_demo_mode', 'true');
    event('qgc_demo_mode');
  } else {
    event('qgc_evaluation_shown');
  }

  const totalMs = result.trace?.total_ms;
  if (typeof totalMs === 'number') {
    tag('qgc_latency_bucket', latencyBucket(totalMs));
  }
}
