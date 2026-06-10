import { GetStaticPaths, GetStaticProps } from 'next';
import Head from 'next/head';
import Link from 'next/link';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { problemHighlights } from '../../data/projectStatus';
import resourceEstimates from '../../data/resourceEstimates.json';
import calibrationData from '../../data/calibrationData.json';
import problemReadmes from '../../data/problemReadmes.json';
import stageDEvidence from '../../data/stageDEvidence.json';
import noisySimResults from '../../data/noisySimResults.json';
import emulatorResults from '../../data/emulatorResults.json';
import multiModelEstimates from '../../data/multiModelEstimates.json';
import troyerAssessment from '../../data/troyerAssessment.json';

interface EmulatorData {
  h2_top: string | null;
  h2_pct: number | null;
  rigetti_top: string | null;
  rigetti_pct: number | null;
  match: boolean;
  h2_histogram: Array<{ outcome: string; count: number }>;
  rigetti_histogram: Array<{ outcome: string; count: number }>;
}

interface MultiModelEntry {
  qubitLabel: string;
  qecScheme: string;
  physicalQubits: number;
  runtime: number | null;
  logicalQubits: number | null;
  family: string;
}

interface TroyerData {
  category: string;
  categoryLabel: string;
  speedup: string;
  classicalBest: string;
  assessment: string;
}

interface NoisyData {
  ideal_top: string;
  ideal_prob: number;
  fidelity_001: number | null;
  fidelity_01: number | null;
  fidelity_05: number | null;
}

interface ScalingProjection {
  [key: string]: unknown;
}

interface StageDData {
  claimCategory: string;
  classicalComplexity: string;
  quantumComplexity: string;
  theoreticalSpeedup: string;
  crossoverEstimate: string;
  honestAssessment: string;
  projections: ScalingProjection[];
  residualRisks: string[];
}

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
    readmeHtml: string | null;
    stageD: StageDData | null;
    noisy: NoisyData | null;
    emulator: EmulatorData | null;
    multiModel: MultiModelEntry[] | null;
    troyer: TroyerData | null;
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
  '01_hubbard': 'QPE (Quantum Phase Estimation)',
  '02_catalysis': 'QPE for H₂ ground state (STO-3G)',
  '03_qae_risk': 'Quantum Amplitude Estimation (IQAE)',
  '04_linear_solvers': 'HHL Algorithm (QPE + eigenvalue inversion)',
  '05_qaoa_maxcut': 'QAOA (Quantum Approximate Optimization)',
  '06_high_frequency_trading': 'Amplitude Estimation for VaR',
  '07_drug_discovery': 'QPE Molecular Binding Energy',
  '08_protein_folding': 'QAOA Lattice Folding',
  '09_factorization': "Shor's Algorithm (QPE + modular multiply)",
  '10_post_quantum_cryptography': 'Grover Key Search',
  '11_quantum_machine_learning': 'Swap Test Kernel',
  '12_quantum_optimization': 'QAOA Job Scheduling',
  '13_climate_modeling': 'HHL for Diffusion PDE',
  '14_materials_discovery': 'QPE Band Gap Estimation',
  '15_database_search': "Grover's Search Algorithm",
  '16_error_correction': '3-Qubit Repetition Code',
  '17_nuclear_physics': 'QPE Deuteron Binding Energy',
  '18_photovoltaics': 'Quantum Walk (Exciton Transport)',
  '19_quantum_chromodynamics': 'Trotter Lattice Gauge Simulation',
  '20_space_mission_planning': 'QAOA Trajectory Optimization',
};

const QUBIT_MAP: Record<string, number> = {
  '01_hubbard': 5, '02_catalysis': 5, '03_qae_risk': 5, '04_linear_solvers': 6,
  '05_qaoa_maxcut': 3, '06_high_frequency_trading': 3, '07_drug_discovery': 5,
  '08_protein_folding': 3, '09_factorization': 8, '10_post_quantum_cryptography': 3,
  '11_quantum_machine_learning': 5, '12_quantum_optimization': 4, '13_climate_modeling': 5,
  '14_materials_discovery': 5, '15_database_search': 4, '16_error_correction': 5,
  '17_nuclear_physics': 5, '18_photovoltaics': 3, '19_quantum_chromodynamics': 4,
  '20_space_mission_planning': 3,
};

function statusColor(status: string): string {
  const s = status.toLowerCase();
  if (s.includes('archived')) return '#991b1b';
  if (s.includes('stage d')) return '#7c2d12';
  if (s.includes('qpe')) return '#0e7490';
  if (s.includes('stage c')) return '#166534';
  if (s.includes('stage b')) return '#1e40af';
  if (s.includes('azure')) return '#5b21b6';
  return '#92400e';
}

function statusBg(status: string): string {
  const s = status.toLowerCase();
  if (s.includes('archived')) return '#fef2f2';
  if (s.includes('stage d')) return '#fff7ed';
  if (s.includes('qpe')) return '#ecfeff';
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
    if (n == null) return '';
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
    return String(n);
  }

  function fmtRuntime(ns: number | null | undefined): string {
    if (ns == null) return '';
    if (ns >= 1e9) return `${(ns / 1e9).toFixed(1)}s`;
    if (ns >= 1e6) return `${(ns / 1e6).toFixed(1)}ms`;
    if (ns >= 1e3) return `${(ns / 1e3).toFixed(1)}μs`;
    return `${ns}ns`;
  }

  return (
    <>
      <Head>
        <title>{problem.title}  Quantum Grand Challenges</title>
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

        {problem.stageD && (
          <section style={{ marginTop: '2rem', padding: '1.5rem', background: '#fef3c7', borderRadius: '12px', border: '2px solid #f59e0b' }}>
            <h2 style={{ marginTop: 0, color: '#92400e' }}>Stage D: Advantage Evidence Package</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #fde68a' }}>
                <div style={{ fontSize: '0.8rem', color: '#92400e', fontWeight: 600 }}>Claim Category</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#78350f', textTransform: 'capitalize' }}>{problem.stageD.claimCategory}</div>
              </div>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #fde68a' }}>
                <div style={{ fontSize: '0.8rem', color: '#92400e', fontWeight: 600 }}>Theoretical Speedup</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#78350f' }}>{problem.stageD.theoreticalSpeedup}</div>
              </div>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #fde68a' }}>
                <div style={{ fontSize: '0.8rem', color: '#92400e', fontWeight: 600 }}>Crossover Estimate</div>
                <div style={{ fontSize: '0.9rem', color: '#78350f' }}>{problem.stageD.crossoverEstimate}</div>
              </div>
            </div>
            <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #fde68a' }}>
                <div style={{ fontSize: '0.85rem', color: '#92400e', fontWeight: 600 }}>Classical</div>
                <div style={{ color: '#374151', marginTop: '0.25rem' }}>{problem.stageD.classicalComplexity}</div>
              </div>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #fde68a' }}>
                <div style={{ fontSize: '0.85rem', color: '#92400e', fontWeight: 600 }}>Quantum</div>
                <div style={{ color: '#374151', marginTop: '0.25rem' }}>{problem.stageD.quantumComplexity}</div>
              </div>
            </div>
            <div style={{ marginTop: '1rem', background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #fde68a' }}>
              <div style={{ fontSize: '0.85rem', color: '#92400e', fontWeight: 600, marginBottom: '0.5rem' }}>Honest Assessment</div>
              <p style={{ color: '#374151', margin: 0, lineHeight: 1.6 }}>{problem.stageD.honestAssessment}</p>
            </div>
            {problem.stageD.residualRisks.length > 0 && (
              <div style={{ marginTop: '1rem', background: '#fef2f2', borderRadius: '8px', padding: '1rem', border: '1px solid #fca5a5' }}>
                <div style={{ fontSize: '0.85rem', color: '#991b1b', fontWeight: 600, marginBottom: '0.5rem' }}>Residual Risks</div>
                <ul style={{ margin: 0, paddingLeft: '1.2rem', color: '#7f1d1d', lineHeight: 1.6 }}>
                  {problem.stageD.residualRisks.map((risk, i) => <li key={i}>{risk}</li>)}
                </ul>
              </div>
            )}
          </section>
        )}

        {problem.noisy && (
          <section style={{ marginTop: '2rem', padding: '1.5rem', background: '#eff6ff', borderRadius: '12px', border: '1px solid #bfdbfe' }}>
            <h2 style={{ marginTop: 0, color: '#1e40af' }}>Noise Resilience (Depolarizing Simulation)</h2>
            <p style={{ color: '#1e3a5f', fontSize: '0.9rem', marginBottom: '1rem' }}>
              Ideal outcome: <code>{problem.noisy.ideal_top}</code> ({(problem.noisy.ideal_prob * 100).toFixed(0)}% probability)
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
              {[
                { label: 'p = 0.001', fid: problem.noisy.fidelity_001, color: '#22c55e' },
                { label: 'p = 0.01', fid: problem.noisy.fidelity_01, color: '#f59e0b' },
                { label: 'p = 0.05', fid: problem.noisy.fidelity_05, color: '#ef4444' },
              ].map((n) => (
                <div key={n.label} style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #dbeafe' }}>
                  <div style={{ fontSize: '0.8rem', color: '#1e40af', fontWeight: 600 }}>{n.label}</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: n.fid != null && n.fid > 0.8 ? '#166534' : n.fid != null && n.fid > 0.5 ? '#92400e' : '#991b1b' }}>
                    {n.fid != null ? `${(n.fid * 100).toFixed(1)}%` : ''}
                  </div>
                  {n.fid != null && (
                    <div style={{ marginTop: '0.5rem', background: '#e5e7eb', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                      <div style={{ width: `${n.fid * 100}%`, height: '100%', background: n.color, borderRadius: '4px' }} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {problem.emulator && (
          <section style={{ marginTop: '2rem', padding: '1.5rem', background: '#f5f3ff', borderRadius: '12px', border: '1px solid #ddd6fe' }}>
            <h2 style={{ marginTop: 0, color: '#5b21b6' }}>Cross-Platform Emulator Results (100 shots)</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #ddd6fe' }}>
                <div style={{ fontSize: '0.85rem', color: '#5b21b6', fontWeight: 600 }}>Quantinuum H2-1E</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#1e1b4b', marginTop: '0.25rem' }}>
                  {problem.emulator.h2_top || ''}
                </div>
                <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>
                  {problem.emulator.h2_pct != null ? `${problem.emulator.h2_pct}% of shots` : ''}
                </div>
              </div>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #ddd6fe' }}>
                <div style={{ fontSize: '0.85rem', color: '#5b21b6', fontWeight: 600 }}>Rigetti QVM</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#1e1b4b', marginTop: '0.25rem' }}>
                  {problem.emulator.rigetti_top || ''}
                </div>
                <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>
                  {problem.emulator.rigetti_pct != null ? `${problem.emulator.rigetti_pct}% of shots` : ''}
                </div>
              </div>
            </div>
            {problem.emulator.match && (
              <div style={{ marginTop: '0.75rem', padding: '0.5rem 1rem', background: '#dcfce7', borderRadius: '6px', color: '#166534', fontSize: '0.9rem' }}>
                ✓ Cross-platform agreement: both simulators find the same dominant outcome
              </div>
            )}
            {(problem.emulator.h2_histogram.length > 0 || problem.emulator.rigetti_histogram.length > 0) && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                {problem.emulator.h2_histogram.length > 0 && (
                  <div>
                    <div style={{ fontSize: '0.8rem', color: '#5b21b6', fontWeight: 600, marginBottom: '0.5rem' }}>H2-1E Distribution</div>
                    <div style={{ width: '100%', height: 180 }}>
                      <ResponsiveContainer>
                        <BarChart data={problem.emulator.h2_histogram} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                          <XAxis dataKey="outcome" fontSize={9} angle={-30} textAnchor="end" height={50} />
                          <YAxis fontSize={10} />
                          <Tooltip />
                          <Bar dataKey="count" fill="#7c3aed" radius={[3, 3, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
                {problem.emulator.rigetti_histogram.length > 0 && (
                  <div>
                    <div style={{ fontSize: '0.8rem', color: '#5b21b6', fontWeight: 600, marginBottom: '0.5rem' }}>Rigetti QVM Distribution</div>
                    <div style={{ width: '100%', height: 180 }}>
                      <ResponsiveContainer>
                        <BarChart data={problem.emulator.rigetti_histogram} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                          <XAxis dataKey="outcome" fontSize={9} angle={-30} textAnchor="end" height={50} />
                          <YAxis fontSize={10} />
                          <Tooltip />
                          <Bar dataKey="count" fill="#06b6d4" radius={[3, 3, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {problem.troyer && (
          <section style={{ marginTop: '2rem', padding: '1.5rem', background: problem.troyer.category === 'proven_speedup' ? '#f0fdf4' : problem.troyer.category === 'simulation_native' ? '#eff6ff' : '#fefce8', borderRadius: '12px', border: `2px solid ${problem.troyer.category === 'proven_speedup' ? '#22c55e' : problem.troyer.category === 'simulation_native' ? '#3b82f6' : '#f59e0b'}` }}>
            <h2 style={{ marginTop: 0, color: '#1a1a1a' }}>Troyer Utility-Scale Classification</h2>
            <div style={{ display: 'inline-block', padding: '0.3rem 0.8rem', borderRadius: '999px', fontSize: '0.85rem', fontWeight: 700, background: problem.troyer.category === 'proven_speedup' ? '#dcfce7' : problem.troyer.category === 'simulation_native' ? '#dbeafe' : '#fef3c7', color: problem.troyer.category === 'proven_speedup' ? '#166534' : problem.troyer.category === 'simulation_native' ? '#1e40af' : '#92400e', marginBottom: '1rem' }}>
              {problem.troyer.categoryLabel}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #e5e7eb' }}>
                <div style={{ fontSize: '0.8rem', color: '#6b7280', fontWeight: 600 }}>Quantum Speedup</div>
                <div style={{ marginTop: '0.25rem', color: '#1a1a1a' }}>{problem.troyer.speedup}</div>
              </div>
              <div style={{ background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #e5e7eb' }}>
                <div style={{ fontSize: '0.8rem', color: '#6b7280', fontWeight: 600 }}>Classical Competitor</div>
                <div style={{ marginTop: '0.25rem', color: '#1a1a1a' }}>{problem.troyer.classicalBest}</div>
              </div>
            </div>
            <div style={{ marginTop: '1rem', background: 'white', borderRadius: '8px', padding: '1rem', border: '1px solid #e5e7eb' }}>
              <div style={{ fontSize: '0.8rem', color: '#6b7280', fontWeight: 600, marginBottom: '0.5rem' }}>Honest Assessment (Troyer Framework)</div>
              <p style={{ margin: 0, color: '#374151', lineHeight: 1.6, fontSize: '0.95rem' }}>{problem.troyer.assessment}</p>
            </div>
          </section>
        )}

        {problem.multiModel && problem.multiModel.length > 0 && (
          <section style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <h2 style={{ marginTop: 0, color: '#0f172a' }}>Multi-Model Resource Comparison</h2>
            <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '1rem' }}>
              Physical qubit requirements across 6 qubit technologies × 2 QEC schemes (inspired by Troyer Architecture Series, Part 3).
            </p>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <BarChart data={problem.multiModel} margin={{ top: 5, right: 20, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="qubitLabel" fontSize={9} angle={-35} textAnchor="end" height={80} />
                  <YAxis fontSize={10} tickFormatter={(v: number) => v >= 1e6 ? `${(v/1e6).toFixed(1)}M` : v >= 1e3 ? `${(v/1e3).toFixed(0)}k` : String(v)} />
                  <Tooltip formatter={(value: number) => [`${value.toLocaleString()} qubits`, 'Physical Qubits']} />
                  <Bar dataKey="physicalQubits" radius={[4, 4, 0, 0]}>
                    {problem.multiModel.map((entry, index) => (
                      <Cell key={`mm-${index}`} fill={entry.family === 'gate_based' ? (entry.qecScheme === 'surface_code' ? '#667eea' : '#a78bfa') : (entry.qecScheme === 'surface_code' ? '#10b981' : '#34d399')} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', justifyContent: 'center', fontSize: '0.8rem', color: '#64748b' }}>
              <span>■ Gate-based + Surface (blue)</span>
              <span style={{ color: '#10b981' }}>■ Majorana + Surface (green)</span>
              <span style={{ color: '#34d399' }}>■ Majorana + Floquet (light green)</span>
            </div>
            <div style={{ marginTop: '1rem', overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ background: '#f1f5f9' }}>
                    <th style={{ textAlign: 'left', padding: '0.5rem' }}>Qubit Model</th>
                    <th style={{ textAlign: 'left', padding: '0.5rem' }}>QEC</th>
                    <th style={{ textAlign: 'right', padding: '0.5rem' }}>Physical Qubits</th>
                    <th style={{ textAlign: 'right', padding: '0.5rem' }}>Logical Qubits</th>
                  </tr>
                </thead>
                <tbody>
                  {problem.multiModel.map((m, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '0.4rem 0.5rem' }}>{m.qubitLabel}</td>
                      <td style={{ padding: '0.4rem 0.5rem' }}>{m.qecScheme}</td>
                      <td style={{ padding: '0.4rem 0.5rem', textAlign: 'right', fontWeight: 600 }}>{m.physicalQubits.toLocaleString()}</td>
                      <td style={{ padding: '0.4rem 0.5rem', textAlign: 'right' }}>{m.logicalQubits ?? ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {problem.readmeHtml && (
          <section style={{ marginTop: '2rem' }}>
            <h2>Problem Documentation</h2>
            <div
              style={{
                padding: '1.5rem',
                background: '#fafafa',
                borderRadius: '10px',
                border: '1px solid #e5e7eb',
                lineHeight: 1.7,
                fontSize: '0.95rem',
                color: '#374151',
                overflow: 'auto',
              }}
              dangerouslySetInnerHTML={{ __html: problem.readmeHtml }}
            />
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
            <li><code>qsharp/src/Main.qs</code>  Quantum algorithm implementation</li>
            <li><code>qsharp/HardwareKernel.qs</code>  Azure-submittable QIR kernel</li>
            <li><code>python/classical_baseline.py</code>  Classical reference implementation</li>
            <li><code>estimates/classical_baseline.json</code>  Baseline metrics</li>
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

  const rawReadme = (problemReadmes as Record<string, Record<string, string>>)[id] || null;
  const readmeHtml = rawReadme?.html || null;

  const rawStageD = (stageDEvidence as Record<string, Record<string, Record<string, unknown>>>)[id] || null;
  const stageD = rawStageD ? {
    claimCategory: String((rawStageD.advantage_claim_contract as Record<string, unknown>)?.claim_category || ''),
    classicalComplexity: String((rawStageD.scaling_analysis_stage_d as Record<string, unknown>)?.classical_complexity || ''),
    quantumComplexity: String((rawStageD.scaling_analysis_stage_d as Record<string, unknown>)?.quantum_complexity || ''),
    theoreticalSpeedup: String((rawStageD.scaling_analysis_stage_d as Record<string, unknown>)?.theoretical_speedup || ''),
    crossoverEstimate: String((rawStageD.scaling_analysis_stage_d as Record<string, unknown>)?.crossover_estimate || ''),
    honestAssessment: String((rawStageD.scaling_analysis_stage_d as Record<string, unknown>)?.honest_assessment || ''),
    projections: ((rawStageD.scaling_analysis_stage_d as Record<string, unknown>)?.projections || []) as ScalingProjection[],
    residualRisks: ((rawStageD.advantage_claim_contract as Record<string, unknown>)?.residual_risks || []) as string[],
  } : null;

  const rawNoisy = (noisySimResults as Record<string, unknown>).problems as Record<string, Record<string, unknown>> | undefined;
  const noisyProblem = rawNoisy?.[id];
  const noisy = noisyProblem ? (() => {
    const ideal = (noisyProblem.ideal as Array<Record<string, unknown>>) || [];
    const top = ideal[0] || {};
    const noisyData = noisyProblem.noisy as Record<string, Record<string, unknown>> || {};
    return {
      ideal_top: String(top.outcome || '?'),
      ideal_prob: Number(top.probability || 0),
      fidelity_001: typeof noisyData['0.001']?.fidelity_vs_ideal === 'number' ? noisyData['0.001'].fidelity_vs_ideal as number : null,
      fidelity_01: typeof noisyData['0.01']?.fidelity_vs_ideal === 'number' ? noisyData['0.01'].fidelity_vs_ideal as number : null,
      fidelity_05: typeof noisyData['0.05']?.fidelity_vs_ideal === 'number' ? noisyData['0.05'].fidelity_vs_ideal as number : null,
    };
  })() : null;

  const rawEmulator = emulatorResults as unknown as Record<string, Record<string, Record<string, unknown>>>;
  const h2Data = rawEmulator.quantinuum_h2_1e?.[id] as Record<string, unknown> | undefined;
  const riData = rawEmulator.rigetti_qvm?.[id] as Record<string, unknown> | undefined;
  const h2Hist = (h2Data?.histogram as Array<Record<string, unknown>>) || [];
  const riHist = (riData?.histogram as Array<Record<string, unknown>>) || [];
  const h2Top = h2Hist[0];
  const riTop = riHist[0];
  const emulator = (h2Top || riTop) ? {
    h2_top: h2Top ? String(h2Top.outcome) : null,
    h2_pct: h2Top ? Number(h2Top.count) : null,
    rigetti_top: riTop ? String(riTop.outcome) : null,
    rigetti_pct: riTop ? Number(riTop.count) : null,
    match: !!(h2Top && riTop && String(h2Top.outcome) === String(riTop.outcome)),
    h2_histogram: h2Hist.slice(0, 6).map(h => ({ outcome: String(h.outcome), count: Number(h.count) })),
    rigetti_histogram: riHist.slice(0, 6).map(h => ({ outcome: String(h.outcome), count: Number(h.count) })),
  } : null;

  // Multi-model estimates
  const rawMultiModel = (multiModelEstimates as Record<string, unknown>).problems as Record<string, Record<string, unknown>> | undefined;
  const problemModels = rawMultiModel?.[id] as Record<string, unknown> | undefined;
  const modelsMap = (problemModels?.models || {}) as Record<string, Record<string, unknown>>;
  const multiModel = Object.values(modelsMap).map(m => ({
    qubitLabel: `${String(m.qubitLabel || '')}${m.qecScheme === 'floquet_code' ? ' (Floquet)' : ''}`,
    qecScheme: String(m.qecScheme || 'surface_code'),
    physicalQubits: Number(m.physicalQubits || 0),
    runtime: typeof m.runtime === 'number' ? m.runtime : null,
    logicalQubits: typeof m.logicalQubits === 'number' ? m.logicalQubits : null,
    family: String(m.family || 'gate_based'),
  })).sort((a, b) => a.physicalQubits - b.physicalQubits);

  // Troyer utility-scale assessment
  const troyerCategories = (troyerAssessment as Record<string, unknown>).categories as Record<string, Record<string, unknown>> | undefined;
  let troyer: { category: string; categoryLabel: string; speedup: string; classicalBest: string; assessment: string } | null = null;
  if (troyerCategories) {
    for (const [catKey, catData] of Object.entries(troyerCategories)) {
      const problems = (catData.problems || []) as Array<Record<string, string>>;
      const match = problems.find(p => p.id === id);
      if (match) {
        troyer = {
          category: catKey,
          categoryLabel: String(catData.label || catKey),
          speedup: match.speedup || 'Unknown',
          classicalBest: match.classical_best || 'Unknown',
          assessment: match.troyer_assessment || '',
        };
        break;
      }
    }
  }

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
        readmeHtml,
        stageD,
        noisy,
        emulator,
        multiModel: multiModel.length > 0 ? multiModel : null,
        troyer,
      },
    },
  };
};
