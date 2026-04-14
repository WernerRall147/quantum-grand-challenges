import azureRunHistory from './azureRunHistory.json';
const runnableCorrectnessReport = require('./problemRunnableCorrectnessReport.json');
const stageDReadinessReport = require('./stageDReadinessReport.json');

export const pipelineStages = [
  {
    title: 'Stage A - Problem Framing',
    description:
      'Define the objective, baseline metrics, and evidence plan before any quantum claim is made.',
  },
  {
    title: 'Stage B - Baseline + Scaffold',
    description:
      'Deliver reproducible classical baselines and Q# scaffolds with aligned interfaces and testable outputs.',
  },
  {
    title: 'Stage C - Implemented Kernel',
    description:
      'Ship a working quantum kernel with benchmarked behavior, bounded uncertainty, explicit evidence links, and DiVincenzo readiness coverage.',
  },
  {
    title: 'Stage D - Advantage Claim',
    description:
      'Permit advantage claims only when calibrated, stress-tested, and policy-gated in CI.',
  },
];

export const activeWorkQueue = [
  {
    title: 'Stage C Promotion',
    description:
      'All 20 problems now have real quantum circuits. Next: generate resource estimates, backend assumptions, and calibration evidence to promote from Stage B to Stage C.',
  },
  {
    title: 'Azure Emulator Results',
    description:
      '4 circuits executing on Quantinuum H2-1E emulator (Hubbard VQE, QAOA MaxCut, Grover, QAE). Collect results and validate against classical baselines.',
  },
  {
    title: 'Resource Estimation Coverage',
    description:
      'Expand estimator pipeline to all 20 problems. Currently 9 have estimator summaries; target is 20/20.',
  },
  {
    title: 'Stage D Evidence Hardening',
    description:
      'Lock uncertainty thresholds and complete advantage claim contracts for QAE, QAOA, and Grover (current Stage C leaders).',
  },
];

export const problemHighlights = [
  {
    title: 'Hubbard Model',
    status: 'Stage C - Calibrated',
    description:
      'VQE 2-qubit ansatz with 20-run calibration ensemble (E=0.877 \u00b1 0.054, 95% CI). 177k physical qubits, 12 logical. Azure Quantum validated on Quantinuum H2.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/01_hubbard',
  },
  {
    title: 'QAE Risk Analysis',
    status: 'Stage D - Theoretical advantage claim',
    description: 'QAE achieves O(1/\u03b5) vs MC O(1/\u03b5\u00b2) \u2014 quadratic speedup. 293k physical qubits, 40 logical, 15 T-gates. 20-run calibration + advantage claim contract filed.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/03_qae_risk',
  },
  {
    title: 'Catalysis Simulation',
    status: 'Stage C - Calibrated',
    description:
      'VQE H\u2082 ground state with 20-run ensemble (E=-1.190 \u00b1 0.022, 95% CI). 177k physical qubits, 12 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/02_catalysis',
  },
  {
    title: 'Linear Solvers',
    status: 'Stage C - Calibrated',
    description:
      'HHL algorithm (6 qubits) with 20-run calibration ensemble. 140k physical qubits, 18 logical, 12 T-gates. Resource estimates for surface_code and gate_ns_e3.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/04_linear_solvers',
  },
  {
    title: 'QAOA MaxCut',
    status: 'Stage D - Theoretical advantage claim',
    description: 'QAOA depth-1 on triangle graph. Advantage claim: theoretical (no proven constant-depth advantage for MaxCut). 132k physical qubits. Fairness review: GW 0.878-approx is polynomial-time competitor.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/05_qaoa_maxcut',
  },
  {
    title: 'High-Frequency Trading',
    status: 'Stage C - Calibrated',
    description: 'Quantum VaR with 20-run ensemble (P=0.645 \u00b1 0.020, 95% CI). 61k physical qubits, 12 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/06_high_frequency_trading',
  },
  {
    title: 'Drug Discovery',
    status: 'Stage C - Calibrated',
    description: 'VQE binding energy with 20-run ensemble (E=-0.863 \u00b1 0.014, 95% CI). 177k physical qubits, 12 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/07_drug_discovery',
  },
  {
    title: 'Protein Folding',
    status: 'Stage C - Calibrated',
    description: 'QAOA lattice folding with 20-run calibration ensemble. 118k physical qubits, 9 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/08_protein_folding',
  },
  {
    title: 'Factorization',
    status: 'Stage C - Calibrated',
    description:
      "Shor's algorithm (8 qubits) with 20-run calibration ensemble. Period=7.0 \u00b1 1.96 (95% CI). 77k physical qubits, 25 logical, 6 T-gates.",
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/09_factorization',
  },
  {
    title: 'Post-Quantum Cryptography',
    status: 'Stage D - Projected advantage claim',
    description: 'Grover key search O(\u221aN) provably optimal. 80% H2-1E, 83% Rigetti cross-platform. 33k physical qubits. Practical threat mitigated by NIST key-doubling.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/10_post_quantum_cryptography',
  },
  {
    title: 'Quantum Machine Learning',
    status: 'Stage C - Calibrated',
    description: 'Swap test kernel with 20-run ensemble (overlap=0.908 \u00b1 0.021, 95% CI). 153k physical qubits, 18 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/11_quantum_machine_learning',
  },
  {
    title: 'Quantum Optimization',
    status: 'Stage C - Calibrated',
    description: 'QAOA scheduling with 20-run calibration ensemble. 132k physical qubits, 12 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/12_quantum_optimization',
  },
  {
    title: 'Climate Modeling',
    status: 'Stage C - Calibrated',
    description: 'HHL diffusion PDE with 20-run ensemble (sol=0.025 \u00b1 0.009, 95% CI). 130k physical qubits, 18 logical, 3 T-gates.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/13_climate_modeling',
  },
  {
    title: 'Materials Discovery',
    status: 'Stage C - Calibrated',
    description: 'VQE band gap with 20-run calibration ensemble across 3 material types. 401k physical qubits, 12 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/14_materials_discovery',
  },
  {
    title: 'Database Search',
    status: 'Stage D - Projected advantage claim',
    description: 'Grover O(\u221aN) provably optimal (BBBV). Advantage claim: projected (quadratic speedup, practical at N>10\u2076). 120k physical qubits, 18 logical. Azure validated on Quantinuum H2.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/15_database_search',
  },
  {
    title: 'Error Correction',
    status: 'Stage C - Calibrated',
    description: '3-qubit repetition code with 20-run calibration ensemble. 100% correction rate. 1.8k physical qubits.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/16_error_correction',
  },
  {
    title: 'Nuclear Physics',
    status: 'Stage C - Calibrated',
    description: 'VQE deuteron binding with 20-run ensemble (E=-1.823 \u00b1 0.024, 95% CI). 177k physical qubits, 12 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/17_nuclear_physics',
  },
  {
    title: 'Photovoltaics',
    status: 'Stage C - Calibrated',
    description: 'Quantum walk exciton transport with 20-run calibration ensemble. 138k physical qubits, 12 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/18_photovoltaics',
  },
  {
    title: 'Quantum Chromodynamics',
    status: 'Stage C - Calibrated',
    description: 'Trotter lattice gauge with 20-run ensemble (Wilson=0.47 \u00b1 0.066, 95% CI). 131k physical qubits, 9 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/19_quantum_chromodynamics',
  },
  {
    title: 'Space Mission Planning',
    status: 'Stage C - Calibrated',
    description: 'QAOA trajectory optimization with 20-run calibration ensemble. 157k physical qubits, 12 logical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/20_space_mission_planning',
  },
];

export const qaoaAzureSmokeAudit = {
  status: 'passed',
  mode: 'execute',
  generatedUtc: '2026-03-04T16:42:19Z',
  manifestPath: 'estimates/azure_job_manifest_small_d3.json',
  submitStep: 'executed',
  collectStep: 'attempted',
};

const successfulRuns = Array.isArray(azureRunHistory.runs)
  ? azureRunHistory.runs.filter((entry) => entry && entry.status === 'succeeded')
  : [];

const runsBySystemMap = successfulRuns.reduce((acc, entry) => {
  const key = String(entry.target_id || 'unknown');
  acc[key] = (acc[key] || 0) + 1;
  return acc;
}, {} as Record<string, number>);

function providerFamilyFromTarget(targetId: string): string {
  const normalized = targetId.toLowerCase();
  if (normalized.startsWith('rigetti.')) {
    return 'Rigetti';
  }
  if (normalized.startsWith('quantinuum.')) {
    return 'Quantinuum';
  }
  if (normalized.startsWith('ionq.')) {
    return 'IonQ';
  }
  if (normalized.startsWith('microsoft.')) {
    return 'Microsoft';
  }
  return 'Other';
}

const runsByFamilyMap = successfulRuns.reduce((acc, entry) => {
  const family = providerFamilyFromTarget(String(entry.target_id || 'unknown'));
  acc[family] = (acc[family] || 0) + 1;
  return acc;
}, {} as Record<string, number>);

const runsByDayMap = successfulRuns.reduce((acc, entry) => {
  const recordedUtc = String(entry.recorded_utc || '');
  const day = recordedUtc.length >= 10 ? recordedUtc.slice(0, 10) : 'unknown';
  acc[day] = (acc[day] || 0) + 1;
  return acc;
}, {} as Record<string, number>);

export const azureExecutionStats = {
  totalSuccessfulRuns: successfulRuns.length,
  systems: Object.entries(runsBySystemMap)
    .map(([targetId, runs]) => ({ targetId, runs }))
    .sort((a, b) => b.runs - a.runs),
};

export const azureProviderFamilyStats = Object.entries(runsByFamilyMap)
  .map(([providerFamily, runs]) => ({ providerFamily, runs }))
  .sort((a, b) => b.runs - a.runs);

export const azureRunTrend = Object.entries(runsByDayMap)
  .filter(([date]) => date !== 'unknown')
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([date, runs]) => ({ date, runs }));

export const recentAzureRuns = successfulRuns
  .slice()
  .sort((a, b) => String(b.recorded_utc || '').localeCompare(String(a.recorded_utc || '')))
  .slice(0, 6)
  .map((entry) => ({
    problemId: String(entry.problem_id || ''),
    instanceId: String(entry.instance_id || ''),
    depth: Number(entry.depth || 0),
    targetId: String(entry.target_id || 'unknown'),
    recordedUtc: String(entry.recorded_utc || ''),
  }));

const runnableSummary = runnableCorrectnessReport.summary || { total: 0, passed: 0, failed: 0 };
const runnableProblems = Array.isArray(runnableCorrectnessReport.problems) ? runnableCorrectnessReport.problems : [];

export const runnableCorrectnessStats = {
  generatedUtc: String(runnableCorrectnessReport.generated_utc || ''),
  total: Number(runnableSummary.total || 0),
  passed: Number(runnableSummary.passed || 0),
  failed: Number(runnableSummary.failed || 0),
  passRatePercent:
    Number(runnableSummary.total || 0) > 0
      ? Math.round((Number(runnableSummary.passed || 0) / Number(runnableSummary.total || 0)) * 100)
      : 0,
  qsharpIncluded: Boolean(runnableCorrectnessReport.environment?.qsharp_included),
};

export const runnableCorrectnessFailures = runnableProblems
  .filter((entry) => entry && entry.runnable_and_correct_signal === false)
  .map((entry) => ({
    problemId: String(entry.problem_id || ''),
    problemName: String(entry.problem_name || ''),
    reason:
      String(entry.classical?.stderr_tail || '').trim() ||
      String(entry.qsharp?.stderr_tail || '').trim() ||
      'Unknown failure',
  }))
  .slice(0, 6);

const stageDSummary = stageDReadinessReport.summary || {
  candidate_count: 0,
  fully_ready: 0,
  avg_readiness_percent: 0,
  open_checklist_items: 0,
  artifact_issue_count: 0,
};

const stageDCandidates = Array.isArray(stageDReadinessReport.candidates) ? stageDReadinessReport.candidates : [];

export const stageDReadinessStats = {
  generatedUtc: String(stageDReadinessReport.generated_utc || ''),
  candidateCount: Number(stageDSummary.candidate_count || 0),
  fullyReady: Number(stageDSummary.fully_ready || 0),
  avgReadinessPercent: Number(stageDSummary.avg_readiness_percent || 0),
  openChecklistItems: Number(stageDSummary.open_checklist_items || 0),
  artifactIssueCount: Number(stageDSummary.artifact_issue_count || 0),
};

export const stageDReadinessCandidates = stageDCandidates.map((entry) => ({
  problemId: String(entry.problem_id || ''),
  claim: String(entry.current_claim || ''),
  score: Number(entry.readiness?.score || 0),
  maxScore: Number(entry.readiness?.max_score || 0),
  readinessPercent: Number(entry.readiness?.percent || 0),
  openChecklist: Number(entry.checklist?.open || 0),
  artifactIssues: Number(entry.artifact_issue_count || 0),
}));

export const stageDExpansionQueue = [
  {
    problemId: '01_hubbard',
    rationale: 'VQE circuit validated on Azure Quantum with resource estimates. Nearest Stage C to Stage D candidate after classical optimizer integration.',
  },
  {
    problemId: '04_linear_solvers',
    rationale: 'Full HHL circuit with resource estimates is ready for Stage C promotion and subsequent Stage D evidence hardening.',
  },
  {
    problemId: '15_database_search',
    rationale: 'Grover circuit submitted to Azure emulator with resource estimates. Stage D advantage claim pending oracle cost accounting.',
  },
];
