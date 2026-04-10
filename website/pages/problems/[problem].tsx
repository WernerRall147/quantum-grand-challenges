import { GetStaticPaths, GetStaticProps } from 'next';
import Head from 'next/head';
import Link from 'next/link';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { problemHighlights } from '../../data/projectStatus';
import resourceEstimates from '../../data/resourceEstimates.json';
import calibrationData from '../../data/calibrationData.json';

interface CalibrationStats {
  num_runs: number;
  mean_value?: number;
  std_value?: number;
  ci95_half_width?: number;
  ci95_lower?: number;
  ci95_upper?: number;
  mean_elapsed_s: number;
}

interface EstimateData {
  physicalQubits: number | null;
  logicalQubits: number | null;
  tCount: number | null;
  rotationCount: number | null;
  runtime: number | null;
  numQubits: number | null;
}

interface ProblemPageProps {
  problem: {
    title: string;
    status: string;
    description: string;
    href: string;
    id: string;
    number: string;
    estimate: EstimateData | null;
    calibration: CalibrationStats | null;
  };
}

const PROBLEM_IDS = [
  '01_hubbard', '02_catalysis', '03_qae_risk', '04_linear_solvers',
  '05_qaoa_maxcut', '06_high_frequency_trading', '07_drug_discovery',
  '08_protein_folding', '09_factorization', '10_post_quantum_cryptography',
  '11_quantum_machine_learning', '12_quantum_optimization', '13_climate_modeling',
  '14_materials_discovery', '15_database_search', '16_error_correction',
  '17_nuclear_physics', '18_photovoltaics', '19_quantum_chromodynamics',
  '20_space_mission_planning',
];

const ALGORITHM_MAP: Record<string, string> = {
  '01_hubbard': 'VQE (Variational Quantum Eigensolver)',
  '02_catalysis': 'VQE for H₂ ground state (STO-3G)',
  '03_qae_risk': 'Quantum Amplitude Estimation (IQAE)',
  '04_linear_solvers': 'HHL Algorithm (QPE + eigenvalue inversion)',
  '05_qaoa_maxcut': 'QAOA (Quantum Approximate Optimization)',
  '06_high_frequency_trading': 'Amplitude Estimation for VaR',
  '07_drug_discovery': 'VQE Molecular Binding Energy',
  '08_protein_folding': 'QAOA Lattice Folding',
  '09_factorization': "Shor's Algorithm (QPE + modular multiply)",
  '10_post_quantum_cryptography': 'Grover Key Search',
  '11_quantum_machine_learning': 'Swap Test Kernel',
  '12_quantum_optimization': 'QAOA Job Scheduling',
  '13_climate_modeling': 'HHL for Diffusion PDE',
  '14_materials_discovery': 'VQE Band Gap Estimation',
  '15_database_search': "Grover's Search Algorithm",
  '16_error_correction': '3-Qubit Repetition Code',
  '17_nuclear_physics': 'VQE Deuteron Binding Energy',
  '18_photovoltaics': 'Quantum Walk (Exciton Transport)',
  '19_quantum_chromodynamics': 'Trotter Lattice Gauge Simulation',
  '20_space_mission_planning': 'QAOA Trajectory Optimization',
};

const QUBIT_MAP: Record<string, number> = {
  '01_hubbard': 2, '02_catalysis': 2, '03_qae_risk': 5, '04_linear_solvers': 6,
  '05_qaoa_maxcut': 3, '06_high_frequency_trading': 3, '07_drug_discovery': 2,
  '08_protein_folding': 3, '09_factorization': 8, '10_post_quantum_cryptography': 3,
  '11_quantum_machine_learning': 5, '12_quantum_optimization': 4, '13_climate_modeling': 5,
  '14_materials_discovery': 2, '15_database_search': 4, '16_error_correction': 5,
  '17_nuclear_physics': 2, '18_photovoltaics': 3, '19_quantum_chromodynamics': 4,
  '20_space_mission_planning': 3,
};

function statusColor(status: string): string {
  const s = status.toLowerCase();
  if (s.includes('stage c')) return '#166534';
  if (s.includes('stage b')) return '#1e40af';
  if (s.includes('azure')) return '#5b21b6';
  return '#92400e';
}

function statusBg(status: string): string {
  const s = status.toLowerCase();
  if (s.includes('stage c')) return '#dcfce7';
  if (s.includes('stage b')) return '#dbeafe';
  if (s.includes('azure')) return '#ede9fe';
  return '#fef3c7';
}

export default function ProblemPage({ problem }: ProblemPageProps) {
  const algorithm = ALGORITHM_MAP[problem.id] || 'Quantum Algorithm';
  const qubits = QUBIT_MAP[problem.id] || '?';
  const est = problem.estimate;

  function fmtNum(n: number | null | undefined): string {
    if (n == null) return '—';
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
    return String(n);
  }

  function fmtRuntime(ns: number | null | undefined): string {
    if (ns == null) return '—';
    if (ns >= 1e9) return `${(ns / 1e9).toFixed(1)}s`;
    if (ns >= 1e6) return `${(ns / 1e6).toFixed(1)}ms`;
    if (ns >= 1e3) return `${(ns / 1e3).toFixed(1)}μs`;
    return `${ns}ns`;
  }

  return (
    <>
      <Head>
        <title>{problem.title} — Quantum Grand Challenges</title>
        <meta name="description" content={problem.description} />
      </Head>
      <main style={{ maxWidth: '900px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        <Link href="/" style={{ color: '#0070f3', textDecoration: 'none', fontSize: '0.9rem' }}>
          &larr; Back to Dashboard
        </Link>

        <h1 style={{ fontSize: '2.5rem', marginTop: '1rem', marginBottom: '0.5rem' }}>
          {problem.number}. {problem.title}
        </h1>

        <span style={{
          display: 'inline-block',
          background: statusBg(problem.status),
          color: statusColor(problem.status),
          fontWeight: 700,
          fontSize: '0.85rem',
          borderRadius: '999px',
          padding: '0.3rem 0.8rem',
          marginBottom: '1.5rem',
        }}>
          {problem.status}
        </span>

        <p style={{ fontSize: '1.15rem', color: '#374151', lineHeight: 1.7 }}>
          {problem.description}
        </p>

        <section style={{ marginTop: '2rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div style={{ background: '#f0f4ff', borderRadius: '10px', padding: '1.25rem' }}>
            <strong style={{ color: '#1e40af' }}>Algorithm</strong>
            <div style={{ marginTop: '0.5rem', color: '#374151' }}>{algorithm}</div>
          </div>
          <div style={{ background: '#f0fdf4', borderRadius: '10px', padding: '1.25rem' }}>
            <strong style={{ color: '#166534' }}>Logical Qubits</strong>
            <div style={{ marginTop: '0.5rem', fontSize: '1.5rem', color: '#166534' }}>{qubits}</div>
          </div>
          <div style={{ background: '#fefce8', borderRadius: '10px', padding: '1.25rem' }}>
            <strong style={{ color: '#92400e' }}>Framework</strong>
            <div style={{ marginTop: '0.5rem', color: '#374151' }}>Modern QDK (qsharp 1.27+)</div>
          </div>
        </section>

        {est && (
          <section style={{ marginTop: '2rem', padding: '1.5rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '12px', color: 'white' }}>
            <h2 style={{ marginTop: 0, color: 'white' }}>Resource Estimation (Azure Quantum RE)</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
              <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '0.8rem', color: '#e0e0ff' }}>Physical Qubits</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 700 }}>{fmtNum(est.physicalQubits)}</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '0.8rem', color: '#e0e0ff' }}>Logical Qubits</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 700 }}>{fmtNum(est.logicalQubits)}</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '0.8rem', color: '#e0e0ff' }}>T-Gates</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 700 }}>{fmtNum(est.tCount)}</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '0.8rem', color: '#e0e0ff' }}>Rotations</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 700 }}>{fmtNum(est.rotationCount)}</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '0.8rem', color: '#e0e0ff' }}>Runtime</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 700 }}>{fmtRuntime(est.runtime)}</div>
              </div>
            </div>
          </section>
        )}

        {est && (
          <section style={{ marginTop: '2rem' }}>
            <h2>Resource Breakdown</h2>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <BarChart data={[
                  { name: 'Physical Qubits', value: est.physicalQubits || 0, color: '#667eea' },
                  { name: 'Logical Qubits', value: est.logicalQubits || 0, color: '#764ba2' },
                  { name: 'T-Gates', value: est.tCount || 0, color: '#f59e0b' },
                  { name: 'Rotations', value: est.rotationCount || 0, color: '#10b981' },
                ].filter(d => d.value > 0)} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => fmtNum(value)} />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {[
                      { name: 'Physical Qubits', value: est.physicalQubits || 0, color: '#667eea' },
                      { name: 'Logical Qubits', value: est.logicalQubits || 0, color: '#764ba2' },
                      { name: 'T-Gates', value: est.tCount || 0, color: '#f59e0b' },
                      { name: 'Rotations', value: est.rotationCount || 0, color: '#10b981' },
                    ].filter(d => d.value > 0).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>
        )}

        {problem.calibration && problem.calibration.mean_value != null && (
          <section style={{ marginTop: '2rem', padding: '1.5rem', background: '#f0fdf4', borderRadius: '12px' }}>
            <h2 style={{ marginTop: 0, color: '#166534' }}>Calibration Evidence (20-Run Ensemble)</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', textAlign: 'center', border: '1px solid #bbf7d0' }}>
                <div style={{ fontSize: '0.8rem', color: '#166534' }}>Mean Value</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#15803d' }}>{problem.calibration.mean_value.toFixed(3)}</div>
              </div>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', textAlign: 'center', border: '1px solid #bbf7d0' }}>
                <div style={{ fontSize: '0.8rem', color: '#166534' }}>95% CI</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#15803d' }}>
                  &plusmn; {(problem.calibration.ci95_half_width || 0).toFixed(3)}
                </div>
              </div>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', textAlign: 'center', border: '1px solid #bbf7d0' }}>
                <div style={{ fontSize: '0.8rem', color: '#166534' }}>Runs</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#15803d' }}>{problem.calibration.num_runs}</div>
              </div>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', textAlign: 'center', border: '1px solid #bbf7d0' }}>
                <div style={{ fontSize: '0.8rem', color: '#166534' }}>Std Dev</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#15803d' }}>{(problem.calibration.std_value || 0).toFixed(3)}</div>
              </div>
            </div>
          </section>
        )}

        <section style={{ marginTop: '2rem' }}>
          <h2>Reproduce It</h2>
          <div style={{ background: '#0f172a', color: '#e2e8f0', borderRadius: '8px', padding: '1.25rem', fontFamily: 'monospace', fontSize: '0.9rem', lineHeight: 1.6 }}>
            <code style={{ whiteSpace: 'pre' }}>{`cd problems/${problem.id}
make classical        # Run classical baseline
make analyze          # Generate plots
make build            # Validate Q# compilation
make run              # Run Q# entry point`}</code>
          </div>
        </section>

        <section style={{ marginTop: '2rem' }}>
          <h2>Key Files</h2>
          <ul style={{ lineHeight: 2 }}>
            <li><code>qsharp/src/Main.qs</code> — Quantum algorithm implementation</li>
            <li><code>qsharp/HardwareKernel.qs</code> — Azure-submittable QIR kernel</li>
            <li><code>python/classical_baseline.py</code> — Classical reference implementation</li>
            <li><code>estimates/classical_baseline.json</code> — Baseline metrics</li>
          </ul>
        </section>

        <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f5f3ff', borderRadius: '10px' }}>
          <a href={problem.href} style={{ color: '#5b21b6', fontWeight: 600, fontSize: '1.1rem', textDecoration: 'none' }}>
            View on GitHub &rarr;
          </a>
        </div>

        <footer style={{ marginTop: '4rem', padding: '1.5rem 0', borderTop: '1px solid #ddd', textAlign: 'center', color: '#999' }}>
          <Link href="/" style={{ color: '#0070f3', textDecoration: 'none' }}>
            Quantum Grand Challenges Dashboard
          </Link>
        </footer>
      </main>
    </>
  );
}

export const getStaticPaths: GetStaticPaths = async () => {
  const paths = PROBLEM_IDS.map((id) => ({ params: { problem: id } }));
  return { paths, fallback: false };
};

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const id = params?.problem as string;
  const number = id.split('_')[0];
  const highlight = problemHighlights.find((p) =>
    p.href.includes(`/${id}`)
  );

  const rawEstimate = (resourceEstimates as Record<string, Record<string, unknown>>)[id] || null;
  const estimate = rawEstimate ? {
    physicalQubits: rawEstimate.physicalQubits ?? null,
    logicalQubits: rawEstimate.logicalQubits ?? null,
    tCount: rawEstimate.tCount ?? null,
    rotationCount: rawEstimate.rotationCount ?? null,
    runtime: rawEstimate.runtime ?? null,
    numQubits: rawEstimate.numQubits ?? null,
  } : null;

  const rawCal = (calibrationData as Record<string, Record<string, unknown>>)[id] || null;
  const calibration = rawCal ? {
    num_runs: (rawCal.num_runs as number) ?? 0,
    mean_value: typeof rawCal.mean_value === 'number' ? rawCal.mean_value : null,
    std_value: typeof rawCal.std_value === 'number' ? rawCal.std_value : null,
    ci95_half_width: typeof rawCal.ci95_half_width === 'number' ? rawCal.ci95_half_width : null,
    ci95_lower: typeof rawCal.ci95_lower === 'number' ? rawCal.ci95_lower : null,
    ci95_upper: typeof rawCal.ci95_upper === 'number' ? rawCal.ci95_upper : null,
    mean_elapsed_s: (rawCal.mean_elapsed_s as number) ?? 0,
  } : null;

  return {
    props: {
      problem: {
        id,
        number,
        title: highlight?.title || id,
        status: highlight?.status || 'In Progress',
        description: highlight?.description || '',
        href: highlight?.href || '#',
        estimate,
        calibration,
      },
    },
  };
};
