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
    status: 'Stage B complete + Azure validated',
    description:
      'VQE ansatz (2-qubit) submitted to Quantinuum H2 simulator and emulator. Resource estimates now available for surface_code and gate_ns_e3 targets.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/01_hubbard',
  },
  {
    title: 'QAE Risk Analysis',
    status: 'Stage C complete',
    description: 'Log-normal PDF corrected and QAE recalibrated. Theoretical tail probability now matches classical baseline exactly (16.1%). Emulator jobs queued on Quantinuum H2-1E.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/03_qae_risk',
  },
  {
    title: 'Catalysis Simulation',
    status: 'Quantum circuit implemented',
    description:
      'VQE for H2 molecular energy with 2-qubit Pauli decomposition. Estimates H2 ground state energy via variational optimization.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/02_catalysis',
  },
  {
    title: 'Linear Solvers',
    status: 'Stage B complete + estimates',
    description:
      'Full HHL circuit implemented (6 qubits). Resource estimates generated for surface_code and gate_ns_e3 targets. Ready for Stage C promotion.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/04_linear_solvers',
  },
  {
    title: 'QAOA MaxCut',
    status: 'Stage C complete',
    description: 'Depth/noise sweeps, uncertainty reports, estimator routing, and env-gated Azure job-manifest validation are complete; next target is Azure submit/collect hardening and portability adapters',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/05_qaoa_maxcut',
  },
  {
    title: 'High-Frequency Trading',
    status: 'Quantum circuit implemented',
    description: 'Quantum VaR estimation via amplitude encoding and oracle marking for loss state detection',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/06_high_frequency_trading',
  },
  {
    title: 'Drug Discovery',
    status: 'Quantum circuit implemented',
    description: 'VQE molecular binding energy estimation with 2-qubit Pauli Hamiltonian decomposition',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/07_drug_discovery',
  },
  {
    title: 'Protein Folding',
    status: 'Quantum circuit implemented',
    description: 'QAOA lattice conformation search optimizing pairwise contact energies',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/08_protein_folding',
  },
  {
    title: 'Factorization',
    status: 'Quantum circuit implemented',
    description: 'Full Shor period-finding with QPE + controlled modular multiply. Factors 15 = 3 x 5.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/09_factorization',
  },
  {
    title: 'Post-Quantum Cryptography',
    status: 'Quantum circuit implemented',
    description: 'Grover key search attack simulation. 80-92% success on 3-5 qubit keyspaces.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/10_post_quantum_cryptography',
  },
  {
    title: 'Quantum Machine Learning',
    status: 'Quantum circuit implemented',
    description: 'Swap test kernel estimation (5 qubits). Quantum kernel matrix matches classical.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/11_quantum_machine_learning',
  },
  {
    title: 'Quantum Optimization',
    status: 'Quantum circuit implemented',
    description: 'QAOA for weighted job scheduling. Found exact optimal with approximation ratio 1.0.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/12_quantum_optimization',
  },
  {
    title: 'Climate Modeling',
    status: 'Quantum circuit implemented',
    description: 'HHL algorithm for thermal diffusion PDE with QPE and eigenvalue inversion',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/13_climate_modeling',
  },
  {
    title: 'Materials Discovery',
    status: 'Quantum circuit implemented',
    description: 'VQE band gap estimation for tight-binding models across 3 material types',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/14_materials_discovery',
  },
  {
    title: 'Database Search',
    status: 'Stage C complete + Azure validated',
    description: 'Grover 4-qubit circuit submitted to Quantinuum H2 simulator and emulator. Resource estimates now generated for two architectures.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/15_database_search',
  },
  {
    title: 'Error Correction',
    status: 'Quantum circuit implemented',
    description: '3-qubit bit-flip repetition code with syndrome extraction. 100% correction rate.',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/16_error_correction',
  },
  {
    title: 'Nuclear Physics',
    status: 'Quantum circuit implemented',
    description: 'VQE for deuteron binding energy with pionless EFT Hamiltonian',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/17_nuclear_physics',
  },
  {
    title: 'Photovoltaics',
    status: 'Quantum circuit implemented',
    description: 'Discrete quantum walk for exciton transport in organic photovoltaic networks',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/18_photovoltaics',
  },
  {
    title: 'Quantum Chromodynamics',
    status: 'Quantum circuit implemented',
    description: 'Trotter simulation of 1D lattice gauge theory showing confinement transition',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/19_quantum_chromodynamics',
  },
  {
    title: 'Space Mission Planning',
    status: 'Quantum circuit implemented',
    description: 'QAOA trajectory optimization for multi-leg missions. Found exact optimal.',
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
