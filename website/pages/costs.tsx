import { useEffect, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import CostReference, { CostAnalysis, hasCostFigures } from '../components/CostReference';

export const LAST_COST_KEY = 'qgc:lastCostAnalysis';

interface StoredCost {
  problem?: string;
  verdict?: string;
  cost_analysis?: CostAnalysis;
  at?: string;
}

const BILLING_MODELS = [
  {
    platform: 'Quantum',
    unit: 'Per shot',
    detail: 'You are billed per circuit execution. A job is many shots, so cost scales with how many times you repeat the circuit, not with wall-clock time.',
    colour: '#1d4ed8',
    bg: '#eff6ff',
    border: '#bfdbfe',
  },
  {
    platform: 'Azure AI / ML',
    unit: 'Per compute-hour',
    detail: 'You are billed for the VM while it is running, whether it is busy or idle. Cost scales with time and instance size.',
    colour: '#6d28d9',
    bg: '#f5f3ff',
    border: '#ddd6fe',
  },
  {
    platform: 'Azure HPC / GPU',
    unit: 'Per compute-hour',
    detail: 'Same billing shape as AI/ML, at much higher hourly rates for large multi-GPU or InfiniBand-connected nodes.',
    colour: '#a16207',
    bg: '#fefce8',
    border: '#fde68a',
  },
];

export default function CostsPage() {
  const [stored, setStored] = useState<StoredCost | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(LAST_COST_KEY);
      if (raw) setStored(JSON.parse(raw) as StoredCost);
    } catch {
      // A malformed or unavailable store just means we show the explainer alone.
    }
    setLoaded(true);
  }, []);

  const ca = stored?.cost_analysis;

  return (
    <>
      <Head>
        <title>Cost model | Quantum Grand Challenges</title>
        <meta name="description" content="How per-run costs are estimated across quantum, AI/ML and HPC, why the three figures are not directly comparable, and why cost does not decide quantum advantage." />
      </Head>

      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        <Link href="/evaluate/" style={{ color: '#0070f3', textDecoration: 'none', fontSize: '0.9rem' }}>
          &larr; Back to the Evaluator
        </Link>

        <h1 style={{ fontSize: '2.5rem', marginTop: '1rem', marginBottom: '0.5rem' }}>Cost model</h1>
        <p style={{ color: '#666', fontSize: '1.1rem', marginBottom: '2rem', maxWidth: '70ch' }}>
          What a reference run costs on each platform, where those numbers come from, and why they do
          not decide the recommendation.
        </p>

        <section style={{ padding: '1.25rem 1.5rem', background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: '10px', marginBottom: '2rem' }}>
          <h2 style={{ marginTop: 0, fontSize: '1.15rem', color: '#9a3412' }}>Read this before reading the numbers</h2>
          <p style={{ margin: '0 0 0.6rem', color: '#7c2d12', fontSize: '0.95rem', lineHeight: 1.6 }}>
            The three figures are priced in different units. Quantum is billed per shot; AI/ML and HPC are
            billed per compute-hour. Putting them side by side is useful for order of magnitude and
            actively misleading if read as a like-for-like comparison.
          </p>
          <p style={{ margin: 0, color: '#7c2d12', fontSize: '0.95rem', lineHeight: 1.6 }}>
            More importantly: <strong>cost does not determine quantum advantage.</strong> A problem with an
            exponential speedup can be expensive per run and still be the right answer. A problem with no
            speedup is not made suitable by being cheap. Feasibility and the speedup class decide the
            verdict; these rates are context.
          </p>
        </section>

        {/* Result-specific figures, carried over from the last evaluation in this tab. */}
        <section style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.4rem' }}>Your last evaluation</h2>
          {!loaded && (
            <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Loading...</p>
          )}
          {loaded && hasCostFigures(ca) && (
            <>
              {stored?.problem && (
                <div style={{ margin: '0.5rem 0 1rem', padding: '0.75rem 1rem', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b' }}>Problem</div>
                  <div style={{ fontSize: '0.9rem', color: '#334155', marginTop: '0.25rem' }}>{stored.problem}</div>
                  {stored.verdict && (
                    <div style={{ fontSize: '0.8rem', color: '#475569', marginTop: '0.4rem' }}>
                      Verdict: <strong>{stored.verdict.replace(/_/g, ' ')}</strong>
                    </div>
                  )}
                </div>
              )}
              <CostReference ca={ca as CostAnalysis} />
            </>
          )}
          {loaded && !hasCostFigures(ca) && (
            <div style={{ padding: '1.25rem 1.5rem', background: '#f8fafc', border: '1px dashed #cbd5e1', borderRadius: '10px' }}>
              <p style={{ margin: '0 0 0.75rem', color: '#475569', fontSize: '0.95rem' }}>
                No evaluation in this browser tab yet. Run one and the per-run figures for that problem
                will appear here.
              </p>
              <Link href="/evaluate/" style={{ color: '#0070f3', textDecoration: 'none', fontWeight: 600, fontSize: '0.9rem' }}>
                Go to the Evaluator &rarr;
              </Link>
            </div>
          )}
        </section>

        <section style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.4rem' }}>How each platform is billed</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
            {BILLING_MODELS.map((b) => (
              <div key={b.platform} style={{ padding: '1.1rem 1.25rem', background: b.bg, border: `1px solid ${b.border}`, borderRadius: '10px' }}>
                <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: b.colour }}>{b.platform}</div>
                <div style={{ fontSize: '1.15rem', fontWeight: 700, color: b.colour, margin: '0.3rem 0 0.5rem' }}>{b.unit}</div>
                <p style={{ margin: 0, fontSize: '0.87rem', color: '#334155', lineHeight: 1.55 }}>{b.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.4rem' }}>Where the rates come from</h2>
          <ol style={{ color: '#334155', fontSize: '0.95rem', lineHeight: 1.8, paddingLeft: '1.2rem', maxWidth: '75ch' }}>
            <li>
              <strong>Live retail prices.</strong> Compute rates are looked up from the public Azure retail
              pricing service at evaluation time, so they track list price rather than a number typed into
              this repository months ago.
            </li>
            <li>
              <strong>Pinned fallback.</strong> If that lookup fails or times out, a pinned rate table is used
              instead. The figures stay sensible, but they can drift from list price.
            </li>
            <li>
              <strong>Quantum rates</strong> are per-shot provider rates, applied to a hardware-grounded
              representative circuit whose width and depth are capped to what current devices actually expose.
            </li>
          </ol>
          <p style={{ color: '#64748b', fontSize: '0.88rem', lineHeight: 1.6, maxWidth: '75ch' }}>
            All of it is list pricing. No reservations, no negotiated discounts, no egress, no storage, no
            support plan. Treat the output as an order of magnitude for a single reference run and validate
            against the pricing calculator before anyone commits a budget.
          </p>
        </section>

        <section style={{ padding: '1.25rem 1.5rem', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '10px' }}>
          <h2 style={{ marginTop: 0, fontSize: '1.05rem', color: '#1e3a8a' }}>The trap this page exists to avoid</h2>
          <p style={{ margin: 0, color: '#1e40af', fontSize: '0.92rem', lineHeight: 1.6, maxWidth: '75ch' }}>
            A quantum figure can look enormous next to an HPC hourly rate and produce a confident-sounding
            &quot;HPC strongly preferred&quot; on pure cost, for a problem where quantum has an exponential
            advantage and classical simulation is simply intractable at scale. That per-unit comparison is
            a separate, narrower statement than the verdict, and it is labelled as such wherever it appears.
          </p>
        </section>

        <div style={{ marginTop: '2.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <Link href="/evaluate/" style={{ padding: '0.7rem 1.5rem', background: '#667eea', color: 'white', borderRadius: '8px', textDecoration: 'none', fontWeight: 600 }}>
            Back to the Evaluator
          </Link>
          <Link href="/architecture/" style={{ padding: '0.7rem 1.5rem', background: '#f1f5f9', color: '#334155', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, border: '1px solid #e2e8f0' }}>
            How the system is built
          </Link>
        </div>
      </div>
    </>
  );
}
