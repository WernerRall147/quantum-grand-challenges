import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';

interface TroyerFilters {
  F1_proven_speedup?: boolean;
  F2_io_survives?: boolean;
  F3_qec_survives?: boolean;
  F4_naturally_quantum?: boolean;
  F5_crossover_feasible?: boolean;
  [key: string]: boolean | undefined;
}

interface EvaluationResult {
  verdict: string;
  confidence: number;
  advantage_class: string;
  recommended_algorithm: string;
  troyer_filters: TroyerFilters;
  red_flags: string[];
  hpc_alternative: string;
  explanation: string;
  similar_problems: string[];
  references: string[];
}

const EXAMPLE_PROBLEMS = [
  "Simulate the ground state energy of a 50-atom lithium cobalt oxide battery cathode material",
  "Factor a 2048-bit RSA public key to test post-quantum cryptographic resilience",
  "Optimize a vehicle routing problem with 500 delivery stops and time windows",
  "Simulate real-time quark-gluon plasma dynamics in a heavy-ion collision",
  "Train a neural network on 10 million images for medical diagnosis",
  "Model exciton transport in an organic photovoltaic thin film",
];

const FILTER_LABELS: Record<string, string> = {
  F1_proven_speedup: 'F1: Proven Speedup',
  F2_io_survives: 'F2: I/O Survives',
  F3_qec_survives: 'F3: QEC Survives',
  F4_naturally_quantum: 'F4: Naturally Quantum',
  F5_crossover_feasible: 'F5: Crossover Feasible',
};

export default function EvaluatePage() {
  const [problem, setProblem] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);

  const handleEvaluate = async () => {
    if (!problem.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      // Live API backend on Azure Container Apps
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io';
      const res = await fetch(`${apiBase}/api/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ problem: problem.trim() }),
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch {
      // Fallback: show a demo result for the static site
      setResult({
        verdict: 'DEMO_MODE',
        confidence: 0,
        advantage_class: 'unknown',
        recommended_algorithm: 'N/A',
        troyer_filters: {},
        red_flags: ['This is a demo — the live evaluator requires the Python backend (agents/orchestrator/evaluate.py) connected to Azure AI'],
        hpc_alternative: 'Run `python agents/orchestrator/evaluate.py "your problem"` locally to get a real evaluation',
        explanation: 'The Quantum Advantage Evaluator is a Python backend that connects to Azure OpenAI (GPT-5.4-mini) and the knowledge base (Cosmos DB + AI Search). On the static GitHub Pages site, the backend is not available. Run it locally or deploy as an Azure Function for live evaluations.',
        similar_problems: [],
        references: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const verdictColor = (v: string) => {
    if (v === 'QUANTUM_ADVANTAGE') return { bg: '#dcfce7', fg: '#166534', icon: '✅' };
    if (v === 'HPC_PREFERRED') return { bg: '#dbeafe', fg: '#1e40af', icon: '💻' };
    if (v === 'INCONCLUSIVE') return { bg: '#fef3c7', fg: '#92400e', icon: '🔍' };
    return { bg: '#f3f4f6', fg: '#374151', icon: '❓' };
  };

  const vc = result ? verdictColor(result.verdict) : null;

  return (
    <>
      <Head>
        <title>Evaluate Your Problem — Quantum Grand Challenges</title>
        <meta name="description" content="AI-powered quantum advantage evaluation" />
      </Head>
      <main style={{ maxWidth: '900px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        <Link href="/" style={{ color: '#0070f3', textDecoration: 'none', fontSize: '0.9rem' }}>
          &larr; Back to Dashboard
        </Link>

        <h1 style={{ fontSize: '2.5rem', marginTop: '1rem', marginBottom: '0.5rem' }}>
          Quantum Advantage Evaluator
        </h1>
        <p style={{ color: '#666', fontSize: '1.1rem', marginBottom: '2rem' }}>
          Describe your computational problem. We&apos;ll evaluate whether it&apos;s better solved on a quantum computer or Azure HPC — backed by peer-reviewed science and Troyer&apos;s utility-scale filters.
        </p>

        {/* Input */}
        <div style={{ marginBottom: '1.5rem' }}>
          <textarea
            value={problem}
            onChange={(e) => setProblem(e.target.value)}
            placeholder="Describe your quantum computing problem..."
            rows={4}
            style={{
              width: '100%', padding: '1rem', fontSize: '1rem', borderRadius: '10px',
              border: '2px solid #e5e7eb', fontFamily: 'inherit', resize: 'vertical',
              outline: 'none', transition: 'border-color 0.2s',
            }}
            onFocus={(e) => { e.currentTarget.style.borderColor = '#667eea'; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = '#e5e7eb'; }}
          />
          <button
            onClick={handleEvaluate}
            disabled={loading || !problem.trim()}
            style={{
              marginTop: '0.75rem', padding: '0.75rem 2rem', fontSize: '1rem',
              background: loading ? '#9ca3af' : '#667eea', color: 'white',
              border: 'none', borderRadius: '8px', cursor: loading ? 'wait' : 'pointer',
              fontWeight: 600,
            }}
          >
            {loading ? 'Evaluating...' : 'Evaluate Problem'}
          </button>
        </div>

        {/* Example problems */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '0.5rem' }}>Try an example:</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {EXAMPLE_PROBLEMS.map((ex, i) => (
              <button
                key={i}
                onClick={() => setProblem(ex)}
                style={{
                  padding: '0.4rem 0.8rem', fontSize: '0.8rem', background: '#f3f4f6',
                  border: '1px solid #e5e7eb', borderRadius: '6px', cursor: 'pointer',
                  color: '#374151', maxWidth: '300px', textAlign: 'left',
                }}
              >
                {ex.slice(0, 60)}...
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        {result && (
          <div style={{ marginTop: '2rem' }}>
            {/* Verdict banner */}
            <div style={{
              padding: '1.5rem', borderRadius: '12px', background: vc?.bg,
              border: `2px solid ${vc?.fg}22`, marginBottom: '1.5rem',
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{vc?.icon}</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: vc?.fg }}>{result.verdict.replace(/_/g, ' ')}</div>
              {result.confidence > 0 && (
                <div style={{ fontSize: '1rem', color: vc?.fg, marginTop: '0.25rem' }}>
                  Confidence: {(result.confidence * 100).toFixed(0)}% | Algorithm: {result.recommended_algorithm} | Class: {result.advantage_class}
                </div>
              )}
            </div>

            {/* Troyer Filters */}
            {Object.keys(result.troyer_filters).length > 0 && (
              <div style={{ marginBottom: '1.5rem', padding: '1.25rem', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginTop: 0, color: '#0f172a' }}>Troyer Utility-Scale Filters</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                  {Object.entries(result.troyer_filters).map(([key, val]) => (
                    <div key={key} style={{
                      padding: '0.75rem', borderRadius: '8px',
                      background: val ? '#dcfce7' : '#fef2f2',
                      border: `1px solid ${val ? '#bbf7d0' : '#fecaca'}`,
                    }}>
                      <span style={{ marginRight: '0.5rem' }}>{val ? '✅' : '❌'}</span>
                      <span style={{ fontSize: '0.85rem', color: val ? '#166534' : '#991b1b' }}>
                        {FILTER_LABELS[key] || key}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Red Flags */}
            {result.red_flags.length > 0 && (
              <div style={{ marginBottom: '1.5rem', padding: '1.25rem', background: '#fef2f2', borderRadius: '10px', border: '1px solid #fecaca' }}>
                <h3 style={{ marginTop: 0, color: '#991b1b' }}>Red Flags</h3>
                <ul style={{ margin: 0, paddingLeft: '1.2rem', color: '#7f1d1d', lineHeight: 1.6 }}>
                  {result.red_flags.map((flag, i) => <li key={i}>{flag}</li>)}
                </ul>
              </div>
            )}

            {/* HPC Alternative */}
            {result.hpc_alternative && (
              <div style={{ marginBottom: '1.5rem', padding: '1.25rem', background: '#eff6ff', borderRadius: '10px', border: '1px solid #bfdbfe' }}>
                <h3 style={{ marginTop: 0, color: '#1e40af' }}>Azure HPC Alternative</h3>
                <p style={{ margin: 0, color: '#1e3a5f', lineHeight: 1.6 }}>{result.hpc_alternative}</p>
              </div>
            )}

            {/* Explanation */}
            {result.explanation && (
              <div style={{ marginBottom: '1.5rem', padding: '1.25rem', background: '#fafafa', borderRadius: '10px', border: '1px solid #e5e7eb' }}>
                <h3 style={{ marginTop: 0 }}>Detailed Assessment</h3>
                <p style={{ margin: 0, color: '#374151', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>{result.explanation}</p>
              </div>
            )}

            {/* References */}
            {result.references && result.references.length > 0 && (
              <div style={{ marginBottom: '1.5rem', padding: '1rem', background: '#f8fafc', borderRadius: '8px' }}>
                <strong>References:</strong>{' '}
                {result.references.map((ref, i) => (
                  <span key={i} style={{ display: 'inline-block', margin: '0.2rem', padding: '0.2rem 0.6rem', background: '#e5e7eb', borderRadius: '4px', fontSize: '0.85rem' }}>
                    {ref}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* How it works */}
        <section style={{ marginTop: '3rem', padding: '2rem', background: '#f0f4ff', borderRadius: '12px' }}>
          <h2 style={{ marginTop: 0 }}>How It Works</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div style={{ background: 'white', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>1️⃣</div>
              <strong>Classify</strong>
              <p style={{ fontSize: '0.9rem', color: '#666', margin: '0.5rem 0 0' }}>Match your problem to known quantum algorithms via hybrid AI Search</p>
            </div>
            <div style={{ background: 'white', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>2️⃣</div>
              <strong>Filter</strong>
              <p style={{ fontSize: '0.9rem', color: '#666', margin: '0.5rem 0 0' }}>Apply Troyer&apos;s 5 utility-scale checks (I/O, QEC, oracle costs)</p>
            </div>
            <div style={{ background: 'white', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>3️⃣</div>
              <strong>Compare</strong>
              <p style={{ fontSize: '0.9rem', color: '#666', margin: '0.5rem 0 0' }}>Honest quantum vs Azure HPC comparison with current capabilities</p>
            </div>
            <div style={{ background: 'white', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>4️⃣</div>
              <strong>Assess</strong>
              <p style={{ fontSize: '0.9rem', color: '#666', margin: '0.5rem 0 0' }}>GPT-5.4 generates a detailed, reference-backed evaluation</p>
            </div>
          </div>
        </section>

        <footer style={{ marginTop: '4rem', padding: '1.5rem 0', borderTop: '1px solid #ddd', textAlign: 'center', color: '#999' }}>
          <p style={{ margin: 0 }}>
            Powered by Azure OpenAI (GPT-5.4-mini) + Cosmos DB + AI Search | <Link href="/" style={{ color: '#0070f3', textDecoration: 'none' }}>Dashboard</Link>
          </p>
        </footer>
      </main>
    </>
  );
}
