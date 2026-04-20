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
  recommended_platform?: string;
  platform_reason?: string;
  troyer_filters: TroyerFilters;
  red_flags: string[];
  hpc_alternative: string;
  ai_alternative?: string;
  explanation: string;
  similar_problems: string[];
  references: string[];
  model_used?: string;
  tokens_used?: number;
  qsharp_code?: string;
  estimation?: Record<string, unknown>;
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
  const [generateCode, setGenerateCode] = useState(false);
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
        body: JSON.stringify({ problem: problem.trim(), generate_code: generateCode }),
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
    if (v === 'AI_ML_PREFERRED') return { bg: '#f3e8ff', fg: '#6b21a8', icon: '🤖' };
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.75rem' }}>
            <button
              onClick={handleEvaluate}
              disabled={loading || !problem.trim()}
              style={{
                padding: '0.75rem 2rem', fontSize: '1rem',
                background: loading ? '#9ca3af' : '#667eea', color: 'white',
                border: 'none', borderRadius: '8px', cursor: loading ? 'wait' : 'pointer',
                fontWeight: 600,
              }}
            >
              {loading ? 'Evaluating...' : 'Evaluate Problem'}
            </button>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.9rem', color: '#374151', cursor: 'pointer' }}>
              <input type="checkbox" checked={generateCode} onChange={(e) => setGenerateCode(e.target.checked)} />
              Generate Q# code
            </label>
          </div>
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
              {result.recommended_platform && (
                <div style={{ marginTop: '0.75rem', padding: '0.5rem 1rem', background: `${vc?.fg}11`, borderRadius: '6px', fontSize: '0.95rem', color: vc?.fg }}>
                  <strong>Recommended platform:</strong> {result.recommended_platform.replace(/_/g, ' ')}
                  {result.platform_reason && <span> — {result.platform_reason}</span>}
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

            {/* AI/ML Alternative */}
            {result.ai_alternative && (
              <div style={{ marginBottom: '1.5rem', padding: '1.25rem', background: '#faf5ff', borderRadius: '10px', border: '1px solid #e9d5ff' }}>
                <h3 style={{ marginTop: 0, color: '#6b21a8' }}>🤖 AI/ML Alternative</h3>
                <p style={{ margin: 0, color: '#581c87', lineHeight: 1.6 }}>{result.ai_alternative}</p>
              </div>
            )}

            {/* HPC Alternative */}
            {result.hpc_alternative && (
              <div style={{ marginBottom: '1.5rem', padding: '1.25rem', background: '#eff6ff', borderRadius: '10px', border: '1px solid #bfdbfe' }}>
                <h3 style={{ marginTop: 0, color: '#1e40af' }}>💻 Azure HPC Alternative</h3>
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

            {/* Q# Code */}
            {result.qsharp_code && (
              <div style={{ marginBottom: '1.5rem', padding: '1.25rem', background: '#1e1e2e', borderRadius: '10px', border: '1px solid #313244' }}>
                <h3 style={{ marginTop: 0, color: '#cdd6f4' }}>Generated Q# Code</h3>
                <pre style={{ margin: 0, color: '#a6e3a1', fontSize: '0.85rem', overflow: 'auto', maxHeight: '400px', lineHeight: 1.5 }}>
                  {result.qsharp_code}
                </pre>
                {result.estimation && !('error' in result.estimation) && (
                  <div style={{ marginTop: '0.75rem', padding: '0.5rem', background: '#313244', borderRadius: '6px', color: '#89b4fa', fontSize: '0.85rem' }}>
                    Resource Estimate: {JSON.stringify(result.estimation)}
                  </div>
                )}
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

            {/* Model info */}
            {result.model_used && (
              <div style={{ fontSize: '0.8rem', color: '#9ca3af', textAlign: 'right' }}>
                Model: {result.model_used}{result.tokens_used ? ` | ${result.tokens_used} tokens` : ''}
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

        {/* Hybrid Compute Platform — inspired by Microsoft Quantum Architecture Series */}
        <section style={{ marginTop: '2.5rem', padding: '2rem', background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)', borderRadius: '12px', textAlign: 'center' }}>
          <p style={{ fontSize: '0.85rem', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.1em', margin: '0 0 0.25rem' }}>
            Microsoft Quantum Architecture
          </p>
          <h2 style={{ marginTop: 0, fontSize: '1.4rem', color: '#1a1a2e' }}>
            These problems will use a <span style={{ fontWeight: 800 }}>hybrid compute platform</span>
          </h2>

          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginTop: '1.5rem' }}>
            {/* AI */}
            <div style={{
              width: '180px', padding: '1.25rem', borderRadius: '12px', background: 'white', boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
              borderTop: '4px solid #e74c8b', textAlign: 'center',
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🧠</div>
              <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#6b7280' }}>Intelligent</div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: '#1a1a2e' }}>Artificial Intelligence</div>
            </div>

            {/* Connectors */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div style={{ width: '40px', height: '3px', background: '#e74c8b', borderRadius: '2px' }} />
              <div style={{ width: '40px', height: '3px', background: '#a855f7', borderRadius: '2px' }} />
              <div style={{ width: '40px', height: '3px', background: '#3b82f6', borderRadius: '2px' }} />
            </div>

            {/* Quantum */}
            <div style={{
              width: '200px', padding: '1.5rem', borderRadius: '50%', background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%)',
              boxShadow: '0 4px 20px rgba(59,130,246,0.3)', textAlign: 'center',
              aspectRatio: '1', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
            }}>
              <div style={{ fontSize: '0.6rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#bfdbfe' }}>Fast and Reliable</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'white' }}>Quantum</div>
            </div>

            {/* Connectors */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div style={{ width: '40px', height: '3px', background: '#3b82f6', borderRadius: '2px' }} />
              <div style={{ width: '40px', height: '3px', background: '#a855f7', borderRadius: '2px' }} />
              <div style={{ width: '40px', height: '3px', background: '#10b981', borderRadius: '2px' }} />
            </div>

            {/* HPC */}
            <div style={{
              width: '180px', padding: '1.25rem', borderRadius: '12px', background: 'white', boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
              borderTop: '4px solid #10b981', textAlign: 'center',
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>⚡</div>
              <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#6b7280' }}>Advanced</div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: '#1a1a2e' }}>High Performance Compute</div>
            </div>
          </div>

          <p style={{ fontSize: '0.8rem', color: '#9ca3af', marginTop: '1.25rem', marginBottom: 0 }}>
            Based on Dr. Matthias Troyer&apos;s &ldquo;Building the Modern Quantum Architecture&rdquo; series &mdash;{' '}
            <a href="https://quantum.microsoft.com/en-us/insights/industry-insights/quantum-architecture-series" target="_blank" rel="noopener noreferrer" style={{ color: '#667eea', textDecoration: 'none' }}>
              quantum.microsoft.com
            </a>
          </p>
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
