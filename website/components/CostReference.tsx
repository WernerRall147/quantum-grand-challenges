export interface CostAnalysis {
  quantum_estimate?: {
    platform?: string;
    provider?: string;
    estimated_cost_usd?: number | null;
    shots?: number;
    feasible_today?: boolean;
  };
  ai_ml_estimate?: {
    platform?: string;
    sku?: string;
    instance_size?: string;
    estimated_cost_usd?: number | null;
    compute_hours?: number;
    usd_per_hour?: number;
    family?: string;
  };
  hpc_estimate?: {
    platform?: string;
    sku?: string;
    estimated_cost_usd?: number | null;
    compute_hours?: number;
    usd_per_hour?: number;
    family?: string;
  };
  comparison?: { ratio?: number | null; verdict?: string };
  feasibility?: {
    feasible_today?: boolean;
    estimated_physical_qubits?: number;
    hardware_qubits?: number;
    note?: string;
  };
  cheapest_runnable?: string | null;
  caveat?: string;
}

export function hasCostFigures(ca: CostAnalysis | undefined | null): boolean {
  return !!ca && !!(ca.quantum_estimate || ca.ai_ml_estimate || ca.hpc_estimate);
}

export const fmtUsd = (x: number | null | undefined) =>
  typeof x === 'number' ? `$${x.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : 'n/a';

export default function CostReference({ ca }: { ca: CostAnalysis }) {
  const v = ca.comparison?.verdict || '';
  const verdictBg =
    v === 'QUANTUM_STRONGLY_PREFERRED' ? '#dcfce7' :
    v === 'QUANTUM_SLIGHTLY_CHEAPER'   ? '#ecfccb' :
    v === 'HPC_SLIGHTLY_CHEAPER'       ? '#fef9c3' :
    v === 'HPC_PREFERRED_ON_COST'      ? '#ffedd5' :
    v === 'HPC_STRONGLY_PREFERRED'     ? '#fee2e2' :
                                         '#f1f5f9';
  const verdictFg =
    v === 'QUANTUM_STRONGLY_PREFERRED' ? '#15803d' :
    v === 'QUANTUM_SLIGHTLY_CHEAPER'   ? '#65a30d' :
    v === 'HPC_SLIGHTLY_CHEAPER'       ? '#a16207' :
    v === 'HPC_PREFERRED_ON_COST'      ? '#c2410c' :
    v === 'HPC_STRONGLY_PREFERRED'     ? '#b91c1c' :
                                         '#475569';
  const fmt = fmtUsd;
  const cheapest = ca.cheapest_runnable;

  return (
    <div style={{ marginBottom: '1.5rem', padding: '1.25rem', background: '#fff', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
      <h3 style={{ marginTop: 0, color: '#0f172a' }}>Cost reference: per-run rates by platform</h3>
      <p style={{ color: '#475569', fontSize: '0.85rem', margin: '0 0 0.75rem' }}>
        Per-unit Azure list rates for a reference run on each platform - not the cost to solve your whole problem, and not directly comparable across billing models (quantum is billed per shot; AI/ML and HPC per compute-hour). Use them for order-of-magnitude intuition; feasibility and the speedup class decide the recommendation.
      </p>
      {/* Feasibility-gated headline so the three figures are not misread as like-for-like */}
      {(ca.feasibility?.feasible_today === false || cheapest) && (() => {
        const label: Record<string, string> = { quantum: 'Quantum', ai_ml: 'Azure AI/ML', hpc: 'Azure HPC' };
        const cheapCost =
          cheapest === 'quantum' ? ca.quantum_estimate?.estimated_cost_usd :
          cheapest === 'ai_ml' ? ca.ai_ml_estimate?.estimated_cost_usd :
          cheapest === 'hpc' ? ca.hpc_estimate?.estimated_cost_usd : undefined;
        return (
          <div style={{ margin: '0 0 0.85rem', padding: '0.65rem 0.9rem', borderRadius: '8px', background: '#f0f9ff', border: '1px solid #bae6fd', fontSize: '0.85rem', color: '#0c4a6e' }}>
            {ca.feasibility?.feasible_today === false && (
              <span>⚛️ Quantum hardware is not ready for this problem yet - it needs ~{(ca.feasibility.estimated_physical_qubits || 0).toLocaleString()} qubits, and the largest device today exposes {ca.feasibility.hardware_qubits}. </span>
            )}
            {cheapest && (
              <strong>Runnable today: {label[cheapest] || cheapest}{typeof cheapCost === 'number' ? ` (~${fmt(cheapCost)} for a reference run)` : ''}.</strong>
            )}
          </div>
        );
      })()}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem' }}>
        {ca.quantum_estimate && (
          <div style={{ padding: '0.85rem 1rem', borderRadius: '8px', background: '#eff6ff', border: `1px solid ${cheapest === 'quantum' ? '#2563eb' : '#bfdbfe'}` }}>
            <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#1d4ed8', letterSpacing: '0.05em' }}>Quantum</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#1e3a8a', marginTop: '0.25rem' }}>
              {fmt(ca.quantum_estimate.estimated_cost_usd)}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#475569', marginTop: '0.25rem' }}>
              {ca.quantum_estimate.provider || ca.quantum_estimate.platform}
              {typeof ca.quantum_estimate.shots === 'number' && ` · ${ca.quantum_estimate.shots.toLocaleString()} shots`}
            </div>
            {ca.quantum_estimate.feasible_today === false && (
              <div style={{ marginTop: '0.4rem', fontSize: '0.7rem', fontWeight: 600, color: '#9a3412', background: '#ffedd5', borderRadius: '4px', padding: '0.15rem 0.4rem', display: 'inline-block' }}>
                Hardware not yet available
              </div>
            )}
          </div>
        )}
        {ca.ai_ml_estimate && (
          <div style={{ padding: '0.85rem 1rem', borderRadius: '8px', background: '#f5f3ff', border: `1px solid ${cheapest === 'ai_ml' ? '#7c3aed' : '#ddd6fe'}` }}>
            <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#6d28d9', letterSpacing: '0.05em' }}>Azure AI / ML</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#4c1d95', marginTop: '0.25rem' }}>
              {fmt(ca.ai_ml_estimate.estimated_cost_usd)}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#475569', marginTop: '0.25rem' }}>
              {ca.ai_ml_estimate.family || ca.ai_ml_estimate.sku}
              {ca.ai_ml_estimate.instance_size && ` · ${ca.ai_ml_estimate.instance_size}`}
              {typeof ca.ai_ml_estimate.compute_hours === 'number' && ` · ${ca.ai_ml_estimate.compute_hours.toFixed(2)} hr`}
              {typeof ca.ai_ml_estimate.usd_per_hour === 'number' && ` @ $${ca.ai_ml_estimate.usd_per_hour}/hr`}
            </div>
          </div>
        )}
        {ca.hpc_estimate && (
          <div style={{ padding: '0.85rem 1rem', borderRadius: '8px', background: '#fef3c7', border: `1px solid ${cheapest === 'hpc' ? '#d97706' : '#fde68a'}` }}>
            <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#a16207', letterSpacing: '0.05em' }}>Azure HPC / GPU</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#78350f', marginTop: '0.25rem' }}>
              {fmt(ca.hpc_estimate.estimated_cost_usd)}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#475569', marginTop: '0.25rem' }}>
              {ca.hpc_estimate.sku || ca.hpc_estimate.platform}
              {typeof ca.hpc_estimate.compute_hours === 'number' && ` · ${ca.hpc_estimate.compute_hours.toFixed(2)} hr`}
              {typeof ca.hpc_estimate.usd_per_hour === 'number' && ` @ $${ca.hpc_estimate.usd_per_hour}/hr`}
            </div>
          </div>
        )}
        {ca.comparison && (
          <div style={{ padding: '0.85rem 1rem', borderRadius: '8px', background: verdictBg, border: `1px solid ${verdictFg}33` }}>
            <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: verdictFg, letterSpacing: '0.05em' }}>Per-unit cost only</div>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: verdictFg, marginTop: '0.25rem' }}>
              {(ca.comparison.verdict || 'INSUFFICIENT_DATA').replace(/_/g, ' ')}
            </div>
            {typeof ca.comparison.ratio === 'number' && (
              <div style={{ fontSize: '0.78rem', color: '#475569', marginTop: '0.25rem' }}>
                {ca.comparison.ratio.toLocaleString(undefined, { maximumFractionDigits: 0 })}x rate gap (1 quantum job vs 1 HPC compute-hr)
              </div>
            )}
            <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '0.4rem', fontStyle: 'italic' }}>
              Not the cost to solve the problem. Cost alone does not determine advantage.
            </div>
          </div>
        )}
      </div>
      {ca.feasibility && ca.feasibility.feasible_today === false && ca.feasibility.note && (
        <p style={{ marginTop: '0.75rem', marginBottom: 0, fontSize: '0.78rem', color: '#9a3412' }}>
          {ca.feasibility.note}
        </p>
      )}
      {ca.caveat && (
        <p style={{ marginTop: '0.5rem', marginBottom: 0, fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic' }}>
          {ca.caveat}
        </p>
      )}
    </div>
  );
}
