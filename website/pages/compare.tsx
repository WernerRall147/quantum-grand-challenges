import Head from 'next/head';
import Link from 'next/link';
import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import resourceEstimates from '../data/resourceEstimates.json';
import { problemHighlights } from '../data/projectStatus';

type SortKey = 'name' | 'physicalQubits' | 'logicalQubits' | 'tCount' | 'cczCount' | 'rotationCount';

interface ProblemRow {
  id: string;
  name: string;
  algorithm: string;
  status: string;
  physicalQubits: number;
  logicalQubits: number;
  // null means the estimator trace did not report a count. Zero T gates and "we
  // could not count the T gates" are different claims, and only one of them is true
  // for these circuits: 16 of the 20 report null, none report a genuine zero.
  tCount: number | null;
  // Toffoli-class gates, each consuming a CCZ magic state. Uncounted until 2026-09-26: the
  // estimator trace names Q#'s CCNOT "CCX", and only "CCZ" was mapped.
  cczCount: number | null;
  rotationCount: number | null;
  tFactoryFraction: number | null;
  runtime: number;
}

const ALGORITHM_MAP: Record<string, string> = {
  '01_hubbard': 'QPE', '02_catalysis': 'QPE', '03_qae_risk': 'QAE/IQAE',
  '04_linear_solvers': 'HHL', '05_qaoa_maxcut': 'QAOA', '06_high_frequency_trading': 'Sampling',
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

const NOT_REPORTED = '—';

/** A count the trace did not report, rendered as absent rather than as zero. */
function fmtCount(n: number | null): string {
  return n === null || n === undefined ? NOT_REPORTED : String(n);
}

/** Sorts nulls last in both directions: "unknown" is not "smallest". */
function compareCounts(a: number | null, b: number | null, asc: boolean): number {
  if (a === null && b === null) return 0;
  if (a === null) return 1;
  if (b === null) return -1;
  return asc ? a - b : b - a;
}

/** The maturity stage from the problem's recorded status, not an assumption.
 *
 * Every row used to render a hardcoded "Stage C" badge while the computed status
 * sat unused. The repository's own distribution is 8 at B, 9 at C and 3 at D, with
 * 11 of the 20 archived after an honest downgrade - so the badge contradicted the
 * project's central claim on the page most likely to be read.
 */
function stageBadge(status: string): { label: string; background: string; color: string } {
  const archived = /archived/i.test(status);
  if (archived) {
    return { label: 'Archived', background: '#fee2e2', color: '#991b1b' };
  }
  const match = status.match(/Stage\s+([A-D])/i);
  if (!match) {
    return { label: 'Stage unrecorded', background: '#f1f5f9', color: '#475569' };
  }
  const stage = match[1].toUpperCase();
  const palette: Record<string, { background: string; color: string }> = {
    A: { background: '#f1f5f9', color: '#475569' },
    B: { background: '#fef3c7', color: '#92400e' },
    C: { background: '#dcfce7', color: '#166534' },
    D: { background: '#dbeafe', color: '#1e40af' },
  };
  return { label: `Stage ${stage}`, ...palette[stage] };
}

export default function ComparePage() {
  const rows: ProblemRow[] = Object.entries(resourceEstimates as unknown as Record<string, Record<string, number | null>>)
    .map(([id, est]) => {
      const highlight = problemHighlights.find((p) => p.href.includes(`/${id}`));
      return {
        id,
        name: highlight?.title || id.replace(/^\d+_/, '').replace(/_/g, ' '),
        algorithm: ALGORITHM_MAP[id] || '?',
        status: highlight?.status || 'Unknown',
        physicalQubits: (est.physicalQubits as number) || 0,
        logicalQubits: (est.logicalQubits as number) || 0,
        // Deliberately not `|| 0`: that turned "not reported" into a measurement of zero.
        tCount: est.tCount ?? null,
        cczCount: est.cczCount ?? null,
        rotationCount: est.rotationCount ?? null,
        tFactoryFraction: est.tFactoryFraction ?? null,
        runtime: (est.runtime as number) || 0,
      };
    })
    .sort((a, b) => a.id.localeCompare(b.id));

  const [sortKey, setSortKey] = useState<SortKey>('name');
  const [sortAsc, setSortAsc] = useState(true);

  const sorted = [...rows].sort((a, b) => {
    if (sortKey === 'tCount' || sortKey === 'cczCount' || sortKey === 'rotationCount') {
      return compareCounts(a[sortKey], b[sortKey], sortAsc);
    }
    const va = a[sortKey];
    const vb = b[sortKey];
    if (typeof va === 'string' && typeof vb === 'string') return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
    return sortAsc ? (va as number) - (vb as number) : (vb as number) - (va as number);
  });

  function handleSort(key: SortKey) {
    if (sortKey === key) { setSortAsc(!sortAsc); } else { setSortKey(key); setSortAsc(key === 'name'); }
  }

  const headerStyle = (key?: SortKey) => ({
    padding: '0.75rem', textAlign: 'left' as const,
    background: key && sortKey === key ? '#e0e7ff' : '#f1f5f9', color: '#1e293b', fontWeight: 700, fontSize: '0.85rem',
    borderBottom: '2px solid #cbd5e1',
  });

  // A clickable <th> cannot be reached by keyboard and does not tell a screen reader
  // that the column sorts, or which way; a button inside the header does both.
  const sortableHeader = (key: SortKey, label: string) => (
    <th style={headerStyle(key)} scope="col" aria-sort={sortKey === key ? (sortAsc ? 'ascending' : 'descending') : 'none'}>
      <button
        type="button"
        onClick={() => handleSort(key)}
        style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', color: 'inherit', cursor: 'pointer', textAlign: 'left' }}
      >
        {label} <span aria-hidden="true">{sortKey === key ? (sortAsc ? '▲' : '▼') : ''}</span>
      </button>
    </th>
  );

  const chartData = rows.map((r) => ({ name: r.id.split('_')[0], pq: r.physicalQubits, lq: r.logicalQubits }));

  // Computed from the estimates, never typed in: the hardcoded version still said
  // "1.7k (QEC) to 369k (QAE risk)" and "the QPE problems report no T gates" after both
  // had stopped being true, and called rotation-only kernels "zero T-gates, simpler",
  // when every rotation is synthesized from T states in a fault-tolerant machine.
  const byQubits = [...rows].filter((r) => r.physicalQubits > 0).sort((a, b) => a.physicalQubits - b.physicalQubits);
  const smallest = byQubits[0];
  const largest = byQubits[byQubits.length - 1];
  const factoryPercents = rows
    .map((r) => r.tFactoryFraction)
    .filter((f): f is number => typeof f === 'number')
    .map((f) => Math.round(f * 100));
  const most = (key: 'tCount' | 'cczCount' | 'rotationCount') =>
    rows.filter((r) => typeof r[key] === 'number' && (r[key] as number) > 0)
      .sort((a, b) => (b[key] as number) - (a[key] as number))[0];
  const mostRotations = most('rotationCount');
  const mostToffolis = most('cczCount');
  const mostT = most('tCount');

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
                {sortableHeader('name', 'Problem')}
                <th style={headerStyle()} scope="col">Algorithm</th>
                <th style={headerStyle()} scope="col">Stage</th>
                {sortableHeader('physicalQubits', 'Physical Qubits')}
                {sortableHeader('logicalQubits', 'Logical Qubits')}
                {sortableHeader('tCount', 'T-Gates')}
                {sortableHeader('cczCount', 'Toffolis')}
                {sortableHeader('rotationCount', 'Rotations')}
                <th style={headerStyle()} scope="col">Runtime</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((r, i) => {
                const badge = stageBadge(r.status);
                return (
                <tr key={r.id} style={{ borderTop: '1px solid #e2e8f0', background: i % 2 === 0 ? '#ffffff' : '#f8fafc' }}>
                  <td style={{ padding: '0.75rem' }}>
                    <Link href={`/problems/${r.id}/`} style={{ color: '#2563eb', textDecoration: 'none', fontWeight: 600 }}>
                      {r.name}
                    </Link>
                  </td>
                  <td style={{ padding: '0.75rem', color: '#475569' }}>{r.algorithm}</td>
                  <td style={{ padding: '0.75rem' }}>
                    <span title={r.status} style={{ background: badge.background, color: badge.color, fontWeight: 600, fontSize: '0.75rem', borderRadius: '999px', padding: '0.15rem 0.5rem' }}>
                      {badge.label}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem', fontWeight: 600, color: '#1e293b' }}>{fmtNum(r.physicalQubits)}</td>
                  <td style={{ padding: '0.75rem', color: '#475569' }}>{r.logicalQubits}</td>
                  <td
                    title={r.tCount === null ? 'The estimator trace did not report a T-gate count for this circuit' : undefined}
                    style={{ padding: '0.75rem', color: r.tCount ? '#dc2626' : '#94a3b8', fontWeight: r.tCount ? 700 : 400 }}
                  >{fmtCount(r.tCount)}</td>
                  <td
                    title={r.cczCount === null ? 'The estimator trace did not report a Toffoli count for this circuit' : undefined}
                    style={{ padding: '0.75rem', color: r.cczCount ? '#b45309' : '#94a3b8', fontWeight: r.cczCount ? 700 : 400 }}
                  >{fmtCount(r.cczCount)}</td>
                  <td
                    title={r.rotationCount === null ? 'The estimator trace did not report a rotation count for this circuit' : undefined}
                    style={{ padding: '0.75rem', color: r.rotationCount === null ? '#94a3b8' : '#475569' }}
                  >{fmtCount(r.rotationCount)}</td>
                  <td style={{ padding: '0.75rem', color: '#475569' }}>{fmtRuntime(r.runtime)}</td>
                </tr>
                );
              })}
            </tbody>
          </table>
        </section>

        <section style={{ marginTop: '2rem', padding: '1.5rem', background: '#fefce8', borderRadius: '10px' }}>
          <h3 style={{ marginTop: 0, color: '#92400e' }}>Key Observations</h3>
          <ul style={{ color: '#78350f', lineHeight: 1.8 }}>
            {smallest && largest && (
              <li><strong>Qubit range:</strong> {fmtNum(smallest.physicalQubits)} ({smallest.name}) to {fmtNum(largest.physicalQubits)} ({largest.name}), a {Math.round(largest.physicalQubits / smallest.physicalQubits)}x spread.</li>
            )}
            {factoryPercents.length > 0 && (
              <li><strong>Magic states set the cost:</strong> every T gate, Toffoli and arbitrary-angle rotation is paid for with magic states (a rotation is synthesized from T states, a Toffoli consumes a CCZ state), so T factories take {Math.min(...factoryPercents)}-{Math.max(...factoryPercents)}% of the physical qubits in these estimates, whatever the explicit T-gate count.</li>
            )}
            <li><strong>Largest non-Clifford counts:</strong>{' '}
              {mostRotations && <>{mostRotations.rotationCount?.toLocaleString()} rotations ({mostRotations.name}); </>}
              {mostToffolis && <>{mostToffolis.cczCount?.toLocaleString()} Toffolis ({mostToffolis.name}); </>}
              {mostT && <>{mostT.tCount?.toLocaleString()} T gates ({mostT.name}).</>}
            </li>
            <li><strong>What was estimated:</strong> the toy instances themselves, compiled for fault tolerance with the Quantum Resource Estimator (qdk.qre) on 50 ns gates at a 10⁻³ error rate with a surface code; these are not utility-scale versions of the problems.</li>
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
