export const pipelineStages = [
  {
    title: 'Baseline & Validation',
    description:
      'Run classical solvers (Monte Carlo, exact diagonalization, schedulers) to generate reference JSON outputs and plots.',
  },
  {
    title: 'Quantum Kernel Draft',
    description:
      'Stand up Q# stubs with the same interfaces so resource estimators and tests can drop in once the full circuits land.',
  },
  {
    title: 'Resource Estimation',
    description:
      'Feed shared instances into the Azure Quantum Resource Estimator to chart logical qubits, T counts, and runtime bands.',
  },
  {
    title: 'Integration & Publishing',
    description:
      'Automate plots, reports, and dashboard updates through GitHub Actions and the Next.js site you are reading now.',
  },
];

export const activeWorkQueue = [
  {
    title: '02 Catalysis Simulation',
    description:
      'Prioritize VQE-to-PEA chemistry kernel upgrade on top of the validated Arrhenius baseline and plotting stack.',
  },
  {
    title: '04 Linear Solvers',
    description:
      'Promote the HHL scaffold to a full sparse-system pipeline with condition-number-aware benchmarking.',
  },
  {
    title: '05 QAOA MaxCut',
    description:
      'Move from analytical placeholder to parameterized QAOA layers with approximation-ratio sweeps.',
  },
  {
    title: '06 High-Frequency Trading',
    description:
      'Bridge moving-average baseline into quantum kernel experiments for short-horizon signal search.',
  },
];

export const problemHighlights = [
  {
    title: 'Hubbard Model',
    status: '✅ COMPLETE - VQE + HHL',
    description:
      'Two validated quantum kernels with documented resource estimates and baseline agreement',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/01_hubbard',
  },
  {
    title: 'QAE Risk Analysis',
    status: '⚠️ Implemented - Calibration Pending',
    description: 'Canonical QAE structure is implemented; probability calibration is in progress',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/03_qae_risk',
  },
  {
    title: 'Catalysis Simulation',
    status: '🟢 Ready for quantum kernel',
    description:
      'Classical Arrhenius baseline and plots are validated; quantum chemistry circuit work is next',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/02_catalysis',
  },
  {
    title: 'Linear Solvers',
    status: '🟢 Ready for quantum kernel',
    description:
      'Condition-analysis baseline is reproducible and prepared for HHL circuit expansion',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/04_linear_solvers',
  },
  {
    title: 'QAOA MaxCut',
    status: '🟢 Ready for quantum kernel',
    description: 'Graph-cut classical baseline is stable and awaiting full QAOA parameterized layers',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/05_qaoa_maxcut',
  },
  {
    title: 'High-Frequency Trading',
    status: '🟢 Ready for quantum kernel',
    description: 'Knowledge-driven moving-average strategy ready for quantum upgrades',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/06_high_frequency_trading',
  },
  {
    title: 'Drug Discovery',
    status: '🟢 Ready for quantum kernel',
    description: 'Docking energy scaffold with Q# VQE placeholder',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/07_drug_discovery',
  },
  {
    title: 'Protein Folding',
    status: '🟢 Ready for quantum kernel',
    description: 'Contact-map scoring with amplitude-encoding Q# stub',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/08_protein_folding',
  },
  {
    title: 'Factorization',
    status: '🟢 Ready for quantum kernel',
    description: 'Pollard Rho analytics paving the way for Shor order finding',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/09_factorization',
  },
  {
    title: 'Post-Quantum Cryptography',
    status: '🟢 Ready for quantum kernel',
    description: 'Attack-cost estimator preparing amplitude-amplified sieving studies',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/10_post_quantum_cryptography',
  },
  {
    title: 'Quantum Machine Learning',
    status: '🟢 Ready for quantum kernel',
    description: 'Kernel ridge benchmark ready for quantum feature maps',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/11_quantum_machine_learning',
  },
  {
    title: 'Quantum Optimization',
    status: '🟢 Ready for quantum kernel',
    description: 'Weighted tardiness scheduler poised for QAOA upgrades',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/12_quantum_optimization',
  },
  {
    title: 'Climate Modeling',
    status: '🟢 Ready for quantum kernel',
    description: 'Diffusion energy balance ready for HHL-style solvers',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/13_climate_modeling',
  },
  {
    title: 'Materials Discovery',
    status: '🟢 Ready for quantum kernel',
    description: 'Surrogate cluster expansion primed for quantum spectroscopy',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/14_materials_discovery',
  },
  {
    title: 'Database Search',
    status: '✅ COMPLETE - Grover Implementation',
    description: 'Quadratic speedup O(√N) validated with 71-100% success rates',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/15_database_search',
  },
  {
    title: 'Error Correction',
    status: '🟢 Ready for quantum kernel',
    description: 'Repetition-code analytics setting the stage for surface codes',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/16_error_correction',
  },
  {
    title: 'Nuclear Physics',
    status: '🟢 Ready for quantum kernel',
    description: 'Pionless EFT diagonalization with adiabatic state-prep stub',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/17_nuclear_physics',
  },
  {
    title: 'Photovoltaics',
    status: '🟢 Ready for quantum kernel',
    description: 'Shockley-Queisser heuristic with exciton preview in Q#',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/18_photovoltaics',
  },
  {
    title: 'Quantum Chromodynamics',
    status: '🟢 Ready for quantum kernel',
    description: 'Coarse lattice plaquette baseline with gauge-walk stub',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/19_quantum_chromodynamics',
  },
  {
    title: 'Space Mission Planning',
    status: '🟢 Ready for quantum kernel',
    description: 'Patched-conic mission baseline with quantum annealing preview',
    href: 'https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/20_space_mission_planning',
  },
];
