/**
 * One call to the evaluator API, with a deadline and a named failure.
 *
 * Every failure used to render the same DEMO MODE card, whose text blamed a static site
 * with no backend. The live API does exist, and a timeout, an HTTP 500 and an unreachable
 * host are different problems, so each is now reported as itself.
 */

export type EvaluatorFailureKind = 'timeout' | 'http' | 'network' | 'invalid_response';

export class EvaluatorRequestError extends Error {
  readonly kind: EvaluatorFailureKind;
  readonly status?: number;

  constructor(kind: EvaluatorFailureKind, message: string, status?: number) {
    super(message);
    this.name = 'EvaluatorRequestError';
    this.kind = kind;
    this.status = status;
  }
}

// The model call alone has been seen at 98 s (docs/AzureFriday/deck-notes.md), and code
// generation adds compilation, retries and resource estimation on top of it.
export const EVALUATE_TIMEOUT_MS = 150_000;
export const GENERATE_TIMEOUT_MS = 300_000;

function timedOut(timeoutMs: number): EvaluatorRequestError {
  return new EvaluatorRequestError(
    'timeout',
    `The evaluator did not answer within ${Math.round(timeoutMs / 1000)} seconds.`,
  );
}

export async function requestEvaluation(
  url: string,
  body: unknown,
  timeoutMs: number,
  fetchImpl: typeof fetch = fetch,
): Promise<Record<string, unknown>> {
  const controller = new AbortController();
  // The deadline covers reading the body too: a server that sends headers and then
  // stalls would otherwise hang the page as surely as one that never answers.
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    let res: Response;
    try {
      res = await fetchImpl(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
    } catch {
      throw controller.signal.aborted
        ? timedOut(timeoutMs)
        : new EvaluatorRequestError('network', 'The evaluator could not be reached.');
    }

    if (!res.ok) {
      throw new EvaluatorRequestError('http', `The evaluator returned HTTP ${res.status}.`, res.status);
    }

    let text: string;
    try {
      text = await res.text();
    } catch {
      throw controller.signal.aborted
        ? timedOut(timeoutMs)
        : new EvaluatorRequestError('network', 'The connection dropped before the answer arrived.');
    }

    let data: unknown;
    try {
      data = JSON.parse(text);
    } catch {
      throw new EvaluatorRequestError('invalid_response', 'The evaluator answered, but not with a readable result.');
    }
    if (!data || typeof data !== 'object' || typeof (data as { verdict?: unknown }).verdict !== 'string') {
      throw new EvaluatorRequestError('invalid_response', 'The evaluator answered without a verdict.');
    }
    return data as Record<string, unknown>;
  } finally {
    clearTimeout(timer);
  }
}
