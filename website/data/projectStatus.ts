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
    title: '01 Hubbard Model',
    description:
      'VQE ansatz validated on Quantinuum H2 simulator. Resource estimates generated. Next: classical optimizer loop and Stage C promotion.',
  },
  {
    title: '04 Linear Solvers',
    description:
      'HHL circuit complete with resource estimates. Next: solution fidelity validation and Stage C promotion.',
  },
  {
    title: '15 Database Search',
    description:
      'Grover 4-qubit circuit submitted to Quantinuum emulator. Resource estimates generated. Awaiting full simulation results.',
  },
  {
    title: '09 Factorization',
    description:
      'Next implementation target: Shor QPE + modular multiply for N=15 using existing QFT utilities.',
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
    status: 'Stage B complete',
    description:
      'Classical Arrhenius baseline and plots are validated; next milestone is Stage C chemistry kernel',
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
    status: 'Stage B complete',
    description: 'Knowledge-driven moving-average strategy is ready for Stage C quantum upgrades',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/06_high_frequency_trading',
  },
  {
    title: 'Drug Discovery',
    status: 'Stage B complete',
    description: 'Docking energy scaffold with Q# VQE placeholder awaiting Stage C implementation',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/07_drug_discovery',
  },
  {
    title: 'Protein Folding',
    status: 'Stage B complete',
    description: 'Contact-map scoring with amplitude-encoding Q# stub prepared for Stage C',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/08_protein_folding',
  },
  {
    title: 'Factorization',
    status: 'Stage B complete',
    description: 'Pollard Rho analytics are in place and paving the way for Stage C Shor-style work',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/09_factorization',
  },
  {
    title: 'Post-Quantum Cryptography',
    status: 'Stage B complete',
    description: 'Attack-cost estimator is ready for Stage C amplitude-amplified sieving studies',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/10_post_quantum_cryptography',
  },
  {
    title: 'Quantum Machine Learning',
    status: 'Stage B complete',
    description: 'Kernel ridge benchmark is ready for Stage C quantum feature map experiments',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/11_quantum_machine_learning',
  },
  {
    title: 'Quantum Optimization',
    status: 'Stage B complete',
    description: 'Weighted tardiness scheduler is poised for Stage C QAOA upgrades',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/12_quantum_optimization',
  },
  {
    title: 'Climate Modeling',
    status: 'Stage B complete',
    description: 'Diffusion energy balance is ready for Stage C HHL-style solver kernels',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/13_climate_modeling',
  },
  {
    title: 'Materials Discovery',
    status: 'Stage B complete',
    description: 'Surrogate cluster expansion is primed for Stage C quantum spectroscopy work',
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
    status: 'Stage B complete',
    description: 'Repetition-code analytics are setting up Stage C and future surface-code progression',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/16_error_correction',
  },
  {
    title: 'Nuclear Physics',
    status: 'Stage B complete',
    description: 'Pionless EFT diagonalization with adiabatic state-prep stub is awaiting Stage C',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/17_nuclear_physics',
  },
  {
    title: 'Photovoltaics',
    status: 'Stage B complete',
    description: 'Shockley-Queisser heuristic with exciton preview in Q# is poised for Stage C',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/18_photovoltaics',
  },
  {
    title: 'Quantum Chromodynamics',
    status: 'Stage B complete',
    description: 'Coarse lattice plaquette baseline with gauge-walk stub is ready for Stage C expansion',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/19_quantum_chromodynamics',
  },
  {
    title: 'Space Mission Planning',
    status: 'Stage B complete',
    description: 'Patched-conic mission baseline with quantum annealing preview is prepared for Stage C',
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
