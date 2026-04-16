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
    status: 'Stage C - QPE (upgraded from VQE)',
    description: 'QPE for 2-site Hubbard ground state. 132k physical qubits, 18 logical. Exponential speedup for strongly-correlated systems. Naturally quantum.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/01_hubbard',
  },
  {
    title: 'QAE Risk Analysis',
    status: 'Archived — Quadratic speedup negated by I/O',
    description: 'Quadratic O(1/ε) speedup proven but QEC overhead requires ε < 10⁻⁴. Distribution loading is O(N). Archived per Troyer framework.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/03_qae_risk',
  },
  {
    title: 'Catalysis Simulation',
    status: 'Stage C - QPE (upgraded from VQE)',
    description: 'QPE for H₂ molecular ground state (STO-3G). 132k physical qubits, 18 logical. Exponential speedup for quantum chemistry.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/02_catalysis',
  },
  {
    title: 'Linear Solvers',
    status: 'Archived — I/O limited',
    description: 'HHL exponential core negated by O(N) state prep and O(N) readout. Archived per Troyer framework.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/04_linear_solvers',
  },
  {
    title: 'QAOA MaxCut',
    status: 'Archived — At most quadratic',
    description: 'QAOA has at most quadratic advantage, no proven speedup over GW 0.878-approximation. Archived per Troyer framework.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/05_qaoa_maxcut',
  },
  {
    title: 'High-Frequency Trading',
    status: 'Archived — Quadratic speedup negated by I/O',
    description: 'Quadratic amplitude estimation, same QAE limitation. Archived per Troyer framework.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/06_high_frequency_trading',
  },
  {
    title: 'Drug Discovery',
    status: 'Stage C - QPE (upgraded from VQE)',
    description: 'QPE for molecular binding energy. 130k physical qubits, 18 logical. Exponential speedup for pharmaceutical Hamiltonians.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/07_drug_discovery',
  },
  {
    title: 'Protein Folding',
    status: 'Archived — At most quadratic',
    description: 'QAOA heuristic, at most quadratic advantage. AlphaFold dominates classically. Archived per Troyer framework.',
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
    status: 'Archived — Quadratic + oracle cost',
    description: 'Quadratic O(√N) Grover provably optimal but AES oracle cost (millions of T-gates) dominates. Archived per Troyer framework.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/10_post_quantum_cryptography',
  },
  {
    title: 'Quantum Machine Learning',
    status: 'Archived — I/O limited',
    description: 'Exponential kernel speedup negated by O(N) classical data loading. Archived per Troyer framework.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/11_quantum_machine_learning',
  },
  {
    title: 'Quantum Optimization',
    status: 'Archived — At most quadratic',
    description: 'QAOA heuristic, at most quadratic advantage. Classical schedulers mature. Archived per Troyer framework.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/12_quantum_optimization',
  },
  {
    title: 'Climate Modeling',
    status: 'Archived — I/O limited',
    description: 'HHL exponential core negated by O(N) PDE loading and readout. Classical FEM mature. Archived per Troyer framework.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/13_climate_modeling',
  },
  {
    title: 'Materials Discovery',
    status: 'Stage C - QPE (upgraded from VQE)',
    description: 'QPE for band gap estimation via tight-binding Hamiltonian. 132k physical qubits, 18 logical. Exponential speedup for correlated materials.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/14_materials_discovery',
  },
  {
    title: 'Database Search',
    status: 'Archived — Quadratic + QRAM cost',
    description: 'Quadratic O(√N) Grover provably optimal but QRAM loading O(N) erases search advantage. Archived per Troyer framework.',
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
    status: 'Stage C - QPE (upgraded from VQE)',
    description: 'QPE for deuteron binding energy via EFT Hamiltonian. 132k physical qubits, 18 logical. Exponential speedup for nuclear many-body systems.',
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
    status: 'Archived — At most quadratic',
    description: 'QAOA heuristic, at most quadratic advantage. Classical trajectory optimizers mature. Archived per Troyer framework.',
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
