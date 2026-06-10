import Head from 'next/head';
import Link from 'next/link';
import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import resourceEstimates from '../data/resourceEstimates.json';
import { problemHighlights } from '../data/projectStatus';

type SortKey = 'name' | 'physicalQubits' | 'logicalQubits' | 'tCount' | 'rotationCount';

interface ProblemRow {
  id: string;
  name: string;
  algorithm: string;
  status: string;
  physicalQubits: number;
  logicalQubits: number;
  tCount: number;
  rotationCount: number;
  runtime: number;
}

const ALGORITHM_MAP: Record<string, string> = {
  '01_hubbard': 'QPE', '02_catalysis': 'QPE', '03_qae_risk': 'QAE/IQAE',
  '04_linear_solvers': 'HHL', '05_qaoa_maxcut': 'QAOA', '06_high_frequency_trading': 'Amplitude Est.',
  '07_drug_discovery': 'QPE', '08_protein_folding': 'QAOA', '09_factorization': 'Shor',
  '10_post_quantum_cryptography': 'Grover', '11_quantum_machine_learning': 'Swap Test',
  '12_quantum_optimization': 'QAOA', '13_climate_modeling': 'HHL', '14_materials_discovery': 'QPE',
  '15_database_search': 'Grover', '16_error_correction': 'QEC', '17_nuclear_physics': 'QPE',
  '18_photovoltaics': 'Quantum Walk', '19_quantum_chromodynamics': 'Trotter',
  '20_space_mission_planning': 'QAOA',
};

const COLORS = ['#667eea', '#764ba2', '#f59e0b', '#10b981', '#ef4444', '#06b6d4', '#8b5cf6', '#ec4899'];

function fmtNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

function fmtRuntime(ns: number): string {
  if (ns >= 1e9) return `${(ns / 1e9).toFixed(1)}s`;
  if (ns >= 1e6) return `${(ns / 1e6).toFixed(1)}ms`;
  if (ns >= 1e3) return `${(ns / 1e3).toFixed(1)}μs`;
  return `${ns}ns`;
}

export default function ComparePage() {
  const rows: ProblemRow[] = Object.entries(resourceEstimates as unknown as Record<string, Record<string, number>>)
    .map(([id, est]) => {
      const highlight = problemHighlights.find((p) => p.href.includes(`/${id}`));
      return {
        id,
        name: highlight?.title || id.replace(/^\d+_/, '').replace(/_/g, ' '),
        algorithm: ALGORITHM_MAP[id] || '?',
        status: highlight?.status || 'Unknown',
        physicalQubits: est.physicalQubits || 0,
        logicalQubits: est.logicalQubits || 0,
        tCount: est.tCount || 0,
        rotationCount: est.rotationCount || 0,
        runtime: est.runtime || 0,
      };
    })
    .sort((a, b) => a.id.localeCompare(b.id));

  const [sortKey, setSortKey] = useState<SortKey>('name');
  const [sortAsc, setSortAsc] = useState(true);

  const sorted = [...rows].sort((a, b) => {
    const va = a[sortKey];
    const vb = b[sortKey];
    if (typeof va === 'string' && typeof vb === 'string') return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
    return sortAsc ? (va as number) - (vb as number) : (vb as number) - (va as number);
  });

  function handleSort(key: SortKey) {
    if (sortKey === key) { setSortAsc(!sortAsc); } else { setSortKey(key); setSortAsc(key === 'name'); }
  }

  const headerStyle = (key: SortKey) => ({
    padding: '0.75rem', textAlign: 'left' as const, cursor: 'pointer', userSelect: 'none' as const,
    background: sortKey === key ? '#e0e7ff' : '#f1f5f9', color: '#1e293b', fontWeight: 700, fontSize: '0.85rem',
    borderBottom: '2px solid #cbd5e1',
  });

  const chartData = rows.map((r) => ({ name: r.id.split('_')[0], pq: r.physicalQubits, lq: r.logicalQubits }));

  return (
    <>
      <Head>
        <title>Problem Comparison  Quantum Grand Challenges</title>
        <meta name="description" content="Side-by-side comparison of all quantum problems with resource estimates" />
      </Head>
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        <Link href="/" style={{ color: '#0070f3', textDecoration: 'none', fontSize: '0.9rem' }}>
          &larr; Back to Dashboard
        </Link>

        <h1 style={{ fontSize: '2.5rem', marginTop: '1rem' }}>Problem Comparison</h1>
        <p style={{ color: '#666', fontSize: '1.1rem' }}>
          All quantum problems with real Azure Quantum Resource Estimator data. Click column headers to sort.
        </p>

        <section style={{ marginTop: '2rem' }}>
          <h2>Physical Qubits by Problem</h2>
          <div style={{ width: '100%', height: 350 }}>
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" fontSize={11} />
                <YAxis tickFormatter={(v: number) => fmtNum(v)} />
                <Tooltip formatter={(value: number) => fmtNum(value)} />
                <Bar dataKey="pq" name="Physical Qubits" radius={[4, 4, 0, 0]}>
                  {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section style={{ marginTop: '2rem', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', borderRadius: '10px', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <thead>
              <tr>
                <th style={headerStyle('name')} onClick={() => handleSort('name')}>Problem {sortKey === 'name' ? (sortAsc ? '▲' : '▼') : ''}</th>
                <th style={{ ...headerStyle('name'), cursor: 'default' }}>Algorithm</th>
                <th style={{ ...headerStyle('name'), cursor: 'default' }}>Stage</th>
                <th style={headerStyle('physicalQubits')} onClick={() => handleSort('physicalQubits')}>Physical Qubits {sortKey === 'physicalQubits' ? (sortAsc ? '▲' : '▼') : ''}</th>
                <th style={headerStyle('logicalQubits')} onClick={() => handleSort('logicalQubits')}>Logical Qubits {sortKey === 'logicalQubits' ? (sortAsc ? '▲' : '▼') : ''}</th>
                <th style={headerStyle('tCount')} onClick={() => handleSort('tCount')}>T-Gates {sortKey === 'tCount' ? (sortAsc ? '▲' : '▼') : ''}</th>
                <th style={headerStyle('rotationCount')} onClick={() => handleSort('rotationCount')}>Rotations {sortKey === 'rotationCount' ? (sortAsc ? '▲' : '▼') : ''}</th>
                <th style={{ ...headerStyle('name'), cursor: 'default' }}>Runtime</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((r, i) => (
                <tr key={r.id} style={{ borderTop: '1px solid #e2e8f0', background: i % 2 === 0 ? '#ffffff' : '#f8fafc' }}>
                  <td style={{ padding: '0.75rem' }}>
                    <Link href={`/problems/${r.id}/`} style={{ color: '#2563eb', textDecoration: 'none', fontWeight: 600 }}>
                      {r.name}
                    </Link>
                  </td>
                  <td style={{ padding: '0.75rem', color: '#475569' }}>{r.algorithm}</td>
                  <td style={{ padding: '0.75rem' }}>
                    <span style={{ background: '#dcfce7', color: '#166534', fontWeight: 600, fontSize: '0.75rem', borderRadius: '999px', padding: '0.15rem 0.5rem' }}>
                      Stage C
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem', fontWeight: 600, color: '#1e293b' }}>{fmtNum(r.physicalQubits)}</td>
                  <td style={{ padding: '0.75rem', color: '#475569' }}>{r.logicalQubits}</td>
                  <td style={{ padding: '0.75rem', color: r.tCount > 0 ? '#dc2626' : '#475569', fontWeight: r.tCount > 0 ? 700 : 400 }}>{r.tCount}</td>
                  <td style={{ padding: '0.75rem', color: '#475569' }}>{r.rotationCount}</td>
                  <td style={{ padding: '0.75rem', color: '#475569' }}>{fmtRuntime(r.runtime)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section style={{ marginTop: '2rem', padding: '1.5rem', background: '#fefce8', borderRadius: '10px' }}>
          <h3 style={{ marginTop: 0, color: '#92400e' }}>Key Observations</h3>
          <ul style={{ color: '#78350f', lineHeight: 1.8 }}>
            <li><strong>Qubit range:</strong> 1.8k (QEC) to 401k (Materials)  230x variation across problems</li>
            <li><strong>T-gate intensive:</strong> QAE (15), HHL (12), Shor (6), Climate HHL (3)  these require T-state factories</li>
            <li><strong>Rotation dominated:</strong> VQE and QAOA problems use rotations instead of T-gates  simpler for near-term hardware</li>
            <li><strong>All estimates from real Azure Quantum Resource Estimator</strong>  not mock data</li>
          </ul>
        </section>

        <footer style={{ marginTop: '4rem', padding: '1.5rem 0', borderTop: '1px solid #ddd', textAlign: 'center', color: '#999' }}>
          <Link href="/" style={{ color: '#0070f3', textDecoration: 'none' }}>
            Quantum Grand Challenges Dashboard
          </Link>
        </footer>
      </main>
    </>
  );
}
