import Head from 'next/head';

export default function Home() {
  const basePath = process.env.NODE_ENV === 'production' ? '/quantum-grand-challenges' : '';
  const withBasePath = (path: string) => `${basePath}${path}`;

  const pipelineStages: TimelineItem[] = [
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

  const activeWorkQueue: TimelineItem[] = [
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

  const problemHighlights: ProblemCardProps[] = [
    {
      title: 'Hubbard Model',
      status: '✅ COMPLETE - VQE + HHL',
      description: 'Two validated quantum kernels with documented resource estimates and baseline agreement',
    },
    {
      title: 'QAE Risk Analysis',
      status: '⚠️ Implemented - Calibration Pending',
      description: 'Canonical QAE structure is implemented; probability calibration is in progress',
    },
    {
      title: 'Catalysis Simulation',
      status: '🟢 Ready for quantum kernel',
      description: 'Classical Arrhenius baseline and plots are validated; quantum chemistry circuit work is next',
    },
    {
      title: 'Linear Solvers',
      status: '🟢 Ready for quantum kernel',
      description: 'Condition-analysis baseline is reproducible and prepared for HHL circuit expansion',
    },
    {
      title: 'QAOA MaxCut',
      status: '🟢 Ready for quantum kernel',
      description: 'Graph-cut classical baseline is stable and awaiting full QAOA parameterized layers',
    },
    {
      title: 'High-Frequency Trading',
      status: '🟢 Ready for quantum kernel',
      description: 'Knowledge-driven moving-average strategy ready for quantum upgrades',
    },
    {
      title: 'Drug Discovery',
      status: '🟢 Ready for quantum kernel',
      description: 'Docking energy scaffold with Q# VQE placeholder',
    },
    {
      title: 'Protein Folding',
      status: '🟢 Ready for quantum kernel',
      description: 'Contact-map scoring with amplitude-encoding Q# stub',
    },
    {
      title: 'Factorization',
      status: '🟢 Ready for quantum kernel',
      description: 'Pollard Rho analytics paving the way for Shor order finding',
    },
    {
      title: 'Post-Quantum Cryptography',
      status: '🟢 Ready for quantum kernel',
      description: 'Attack-cost estimator preparing amplitude-amplified sieving studies',
    },
    {
      title: 'Quantum Machine Learning',
      status: '🟢 Ready for quantum kernel',
      description: 'Kernel ridge benchmark ready for quantum feature maps',
    },
    {
      title: 'Quantum Optimization',
      status: '🟢 Ready for quantum kernel',
      description: 'Weighted tardiness scheduler poised for QAOA upgrades',
    },
    {
      title: 'Climate Modeling',
      status: '🟢 Ready for quantum kernel',
      description: 'Diffusion energy balance ready for HHL-style solvers',
    },
    {
      title: 'Materials Discovery',
      status: '🟢 Ready for quantum kernel',
      description: 'Surrogate cluster expansion primed for quantum spectroscopy',
    },
    {
      title: 'Database Search',
      status: '✅ COMPLETE - Grover Implementation',
      description: 'Quadratic speedup O(√N) validated with 71-100% success rates',
    },
    {
      title: 'Error Correction',
      status: '🟢 Ready for quantum kernel',
      description: 'Repetition-code analytics setting the stage for surface codes',
    },
    {
      title: 'Nuclear Physics',
      status: '🟢 Ready for quantum kernel',
      description: 'Pionless EFT diagonalization with adiabatic state-prep stub',
    },
    {
      title: 'Photovoltaics',
      status: '🟢 Ready for quantum kernel',
      description: 'Shockley-Queisser heuristic with exciton preview in Q#',
    },
    {
      title: 'Quantum Chromodynamics',
      status: '🟢 Ready for quantum kernel',
      description: 'Coarse lattice plaquette baseline with gauge-walk stub',
    },
    {
      title: 'Space Mission Planning',
      status: '🟢 Ready for quantum kernel',
      description: 'Patched-conic mission baseline with quantum annealing preview',
    },
  ];

  return (
    <>
      <Head>
        <title>Quantum Grand Challenges</title>
        <meta name="description" content="Systematic exploration of 20 quantum computing challenges" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href={withBasePath('/favicon.ico')} />
      </Head>
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>🌌 Quantum Grand Challenges</h1>
        <p style={{ fontSize: '1.25rem', color: '#666', marginBottom: '2rem' }}>
          Systematic exploration of 20 of the world&apos;s most challenging scientific problems using quantum computing
        </p>

        <section style={{ padding: '2rem', background: '#f0f4ff', borderRadius: '12px' }}>
          <h2 style={{ marginTop: 0 }}>🎯 What Success Looks Like</h2>
          <p style={{ color: '#4b5c79' }}>
            Every challenge follows the same reproducible pipeline, from Python baselines to fault-tolerant quantum resource forecasts.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
            {pipelineStages.map((stage) => (
              <TimelineCard key={stage.title} title={stage.title} description={stage.description} />
            ))}
          </div>
        </section>

        <section style={{ marginTop: '3rem' }}>
          <h2>📚 Featured Case Studies</h2>
          <p style={{ color: '#666' }}>
            Three major quantum algorithms fully implemented with comprehensive resource estimates and cross-algorithm comparison.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
            <CaseStudyCard
              title="QAE Risk Analysis (Implemented, Calibration Pending)"
              classicalHeadline="Monte Carlo: 18.98% ± 0.39% (10k samples)"
              classicalDetails="Classical baseline achieves 0% error vs theoretical for tail risk P(Loss > 2.5) on log-normal(0,1) distribution."
              quantumHeadline="Canonical QAE: 594k qubits, 6.4s, 965k T-states"
              quantumDetails="Canonical Grover/QPE/amplitude encoding structure is implemented. Calibration remains in progress to align estimates with theoretical probability."
              linkHref="https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/03_qae_risk"
            />
            <CaseStudyCard
              title="Hubbard Model (VQE + HHL COMPLETE)"
              classicalHeadline="Exact diagonalization: Δc = 5.66 at U/t = 4"
              classicalDetails="Two-site half-filled Hubbard model with classical baseline achieving perfect accuracy for ground state energy and Mott gap."
              quantumHeadline="VQE: 79k qubits, 114μs | HHL: 18.7k qubits, 52ms"
              quantumDetails="VQE achieves 8/8 convergence with minimal T-gates (18). HHL is most qubit-efficient algorithm. Both fully documented with resource estimates."
              linkHref="https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/01_hubbard"
            />
          </div>
        </section>

        <section style={{ marginTop: '3rem', padding: '2rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '12px', color: 'white' }}>
          <h2 style={{ marginTop: 0, color: 'white' }}>🎯 Algorithm Comparison Dashboard</h2>
          <p style={{ fontSize: '1.1rem', marginBottom: '2rem', color: '#f0f0ff' }}>
            Comprehensive resource analysis across VQE, HHL, and QAE showing physical qubits, runtime, T-states, and quantum advantage assessment.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
            <AlgorithmSummary
              name="VQE (Hubbard)"
              qubits="79k"
              runtime="114 μs"
              tStates="1.6k"
              advantage="Error-resilient optimization"
              color="#2E86AB"
            />
            <AlgorithmSummary
              name="HHL (Linear Solver)"
              qubits="18.7k"
              runtime="52 ms"
              tStates="185k"
              advantage="Most qubit-efficient"
              color="#A23B72"
            />
            <AlgorithmSummary
              name="QAE (Risk Analysis)"
              qubits="594k"
              runtime="6.4 s"
              tStates="965k"
              advantage="Quadratic speedup O(1/ε)"
              color="#F18F01"
            />
          </div>
        </section>

        <section style={{ marginTop: '3rem' }}>
          <h2>📊 Visualization Gallery</h2>
          <p style={{ color: '#666' }}>
            Publication-quality comparisons showing resource requirements, scaling predictions, and quantum advantage assessment.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '2rem', marginTop: '1.5rem' }}>
            <VisualizationCard
              title="Physical Qubit Requirements"
              description="HHL is most efficient (18.7k), QAE requires 31.8× more qubits (594k). T-state factories dominate 93-97% of all qubits."
              imageSrc={withBasePath('/images/qubit_comparison.png')}
            />
            <VisualizationCard
              title="Runtime Comparison"
              description="VQE is fastest (114μs), HHL takes 52ms, QAE requires 6.4s. Shows 3 orders of magnitude range across algorithms."
              imageSrc={withBasePath('/images/runtime_comparison.png')}
            />
            <VisualizationCard
              title="T-State Analysis"
              description="QAE needs 965k T-states (5.2× more than HHL). Rotation gates dominate costs at 20 T-states per rotation."
              imageSrc={withBasePath('/images/tstate_comparison.png')}
            />
            <VisualizationCard
              title="Quantum Advantage Map"
              description="Heatmap assessment: HHL wins near-term viability (2027-2029), VQE wins runtime, QAE wins advantage potential."
              imageSrc={withBasePath('/images/quantum_advantage_map.png')}
            />
            <VisualizationCard
              title="Scaling Predictions"
              description="VQE scales linearly, HHL logarithmically, QAE exponentially. Shows practical limits for each algorithm."
              imageSrc={withBasePath('/images/scaling_analysis.png')}
            />
            <VisualizationCard
              title="Technology Timeline"
              description="HHL ready by 2027-2029 (50k qubits), VQE by 2028-2030 (100k qubits), QAE by 2033-2035 (1M qubits)."
              imageSrc={withBasePath('/images/technology_timeline.png')}
            />
          </div>
        </section>

        <div style={{ marginTop: '4rem', padding: '2rem', background: '#f8f9fa', borderRadius: '8px' }}>
          <h2>📊 Current Status</h2>
          <ul style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
            <li><strong>✅ Three Fully Validated Quantum Algorithms:</strong> VQE, HHL, and Grover have validated end-to-end flows</li>
            <li><strong>⚠️ QAE Status:</strong> Canonical implementation is complete, with calibration work still in progress</li>
            <li><strong>🟢 Seventeen Additional Tracks:</strong> Classical baselines and Q# scaffolds are in place and queued for kernel expansion</li>
            <li><strong>✅ 21,000+ words of documentation:</strong> Comprehensive technical summaries and cross-algorithm comparisons</li>
            <li><strong>✅ 6 Publication-Quality Visualizations:</strong> Qubit requirements, runtime, T-states, scaling, advantage map, timeline</li>
            <li><strong>✅ Resource Estimates:</strong> Azure Quantum analysis across 3 architectures (gate_ns_e3, gate_ns_e4, maj_ns_e4)</li>
            <li><strong>✅ Classical Baselines:</strong> All twenty challenges have reproducible baselines with JSON outputs and plots</li>
            <li><strong>✅ CI/CD:</strong> Automated testing and static export ready for GitHub Pages</li>
          </ul>
          <div style={{ marginTop: '1.5rem', padding: '1.5rem', background: 'white', borderRadius: '8px', border: '2px solid #10b981' }}>
            <h3 style={{ marginTop: 0, color: '#10b981' }}>🎉 Latest Achievement: Grover&apos;s Quantum Search</h3>
            <p style={{ color: '#666', marginBottom: 0 }}>
              Complete canonical Grover&apos;s algorithm with multi-target oracle support. Demonstrated quadratic speedup O(√N) 
              with 42.7x faster than classical on 4096-item search. Perfect 100% success rate on large-scale searches. 
              Validated with 250+ measurement shots across three problem sizes (16, 32, 4096 items). Foundation for 
              cryptanalysis, database search, and amplitude amplification applications.
            </p>
          </div>
        </div>

        <section style={{ marginTop: '3rem', padding: '2rem', background: '#eef6ff', borderRadius: '12px' }}>
          <h2 style={{ marginTop: 0 }}>🚧 Active Work Queue</h2>
          <p style={{ color: '#4b5c79' }}>
            Current development focus for the next wave of quantum-kernel upgrades beyond QAE and Grover.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', marginTop: '1.25rem' }}>
            {activeWorkQueue.map((item) => (
              <TimelineCard key={item.title} title={item.title} description={item.description} />
            ))}
          </div>
        </section>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginTop: '3rem' }}>
          {problemHighlights.map((problem) => (
            <ProblemCard
              key={problem.title}
              title={problem.title}
              status={problem.status}
              description={problem.description}
            />
          ))}
        </div>

        <section style={{ marginTop: '3rem', padding: '2rem', borderRadius: '8px', border: '1px dashed #b0c4de' }}>
          <h2>🧪 Reproduce It Yourself</h2>
          <p style={{ color: '#666' }}>Spin up a Codespace or local clone and run the same pipelines that feed this dashboard.</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
            <CommandBlock
              title="Setup"
              commands={[
                'git clone https://github.com/WernerRall147/quantum-grand-challenges.git',
                'cd quantum-grand-challenges',
                'dotnet --list-runtimes | findstr 6.0',
              ]}
            />
            <CommandBlock
              title="Run QAE Risk"
              commands={[
                'cd problems/03_qae_risk',
                'make classical',
                'make analyze',
              ]}
            />
            <CommandBlock
              title="Run Hubbard Benchmark"
              commands={[
                'cd problems/01_hubbard',
                'make classical',
                'make build',
              ]}
            />
          </div>
        </section>

        <footer style={{ marginTop: '4rem', padding: '2rem 0', borderTop: '1px solid #ddd', textAlign: 'center', color: '#666' }}>
          <p>Built with Q#, Python, and Next.js | MIT License</p>
          <p style={{ marginTop: '0.5rem' }}>
            <a href="https://github.com/WernerRall147/quantum-grand-challenges" style={{ color: '#0070f3', textDecoration: 'none' }}>
              View on GitHub →
            </a>
          </p>
        </footer>
      </main>
    </>
  );
}

interface ProblemCardProps {
  title: string;
  status: string;
  description: string;
}

interface TimelineItem {
  title: string;
  description: string;
}

interface CaseStudyProps {
  title: string;
  classicalHeadline: string;
  classicalDetails: string;
  quantumHeadline: string;
  quantumDetails: string;
  linkHref: string;
}

interface CommandBlockProps {
  title: string;
  commands: string[];
}

interface AlgorithmSummaryProps {
  name: string;
  qubits: string;
  runtime: string;
  tStates: string;
  advantage: string;
  color: string;
}

interface VisualizationCardProps {
  title: string;
  description: string;
  imageSrc: string;
}

function ProblemCard({ title, status, description }: ProblemCardProps) {
  return (
    <div style={{ 
      padding: '1.5rem', 
      border: '1px solid #e0e0e0', 
      borderRadius: '8px',
      background: 'white',
      transition: 'box-shadow 0.2s',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'}
    onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
    >
      <h3 style={{ marginTop: 0, fontSize: '1.5rem' }}>{title}</h3>
      <p style={{ color: '#0070f3', fontWeight: '600', margin: '0.5rem 0' }}>{status}</p>
      <p style={{ color: '#666', margin: 0 }}>{description}</p>
    </div>
  );
}

function TimelineCard({ title, description }: TimelineItem) {
  return (
    <div style={{ background: 'white', borderRadius: '10px', padding: '1.25rem', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
      <h3 style={{ marginTop: 0, fontSize: '1.2rem', color: '#1f3d7a' }}>{title}</h3>
      <p style={{ color: '#52627b', marginBottom: 0 }}>{description}</p>
    </div>
  );
}

function CaseStudyCard({ title, classicalHeadline, classicalDetails, quantumHeadline, quantumDetails, linkHref }: CaseStudyProps) {
  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: '10px', padding: '1.5rem', background: 'white' }}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      <p style={{ color: '#15803d', fontWeight: 600, marginBottom: '0.5rem' }}>{classicalHeadline}</p>
      <p style={{ color: '#525252', marginTop: 0 }}>{classicalDetails}</p>
      <p style={{ color: '#1d4ed8', fontWeight: 600, marginBottom: '0.5rem' }}>{quantumHeadline}</p>
      <p style={{ color: '#525252', marginTop: 0 }}>{quantumDetails}</p>
      <a href={linkHref} style={{ display: 'inline-block', marginTop: '0.75rem', color: '#0ea5e9', textDecoration: 'none', fontWeight: 600 }}>
        Explore the repository →
      </a>
    </div>
  );
}

function CommandBlock({ title, commands }: CommandBlockProps) {
  return (
    <div style={{ background: '#0f172a', color: '#e2e8f0', borderRadius: '8px', padding: '1.25rem', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace' }}>
      <h3 style={{ marginTop: 0, marginBottom: '0.75rem', fontSize: '1.1rem', color: '#38bdf8' }}>{title}</h3>
      <code style={{ whiteSpace: 'pre-line', fontSize: '0.95rem' }}>{commands.join('\n')}</code>
    </div>
  );
}

function AlgorithmSummary({ name, qubits, runtime, tStates, advantage, color }: AlgorithmSummaryProps) {
  return (
    <div style={{ 
      background: 'rgba(255,255,255,0.15)', 
      borderRadius: '10px', 
      padding: '1.5rem',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255,255,255,0.2)'
    }}>
      <h3 style={{ marginTop: 0, color, fontSize: '1.3rem' }}>{name}</h3>
      <div style={{ marginTop: '1rem', display: 'grid', gap: '0.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#f0f0ff' }}>Physical Qubits:</span>
          <strong style={{ color: 'white' }}>{qubits}</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#f0f0ff' }}>Runtime:</span>
          <strong style={{ color: 'white' }}>{runtime}</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#f0f0ff' }}>T-States:</span>
          <strong style={{ color: 'white' }}>{tStates}</strong>
        </div>
      </div>
      <div style={{ 
        marginTop: '1rem', 
        paddingTop: '1rem', 
        borderTop: '1px solid rgba(255,255,255,0.2)',
        color: '#fff',
        fontStyle: 'italic',
        fontSize: '0.95rem'
      }}>
        {advantage}
      </div>
    </div>
  );
}

function VisualizationCard({ title, description, imageSrc }: VisualizationCardProps) {
  return (
    <div style={{ 
      border: '1px solid #e5e7eb', 
      borderRadius: '12px', 
      overflow: 'hidden',
      background: 'white',
      transition: 'transform 0.2s, box-shadow 0.2s',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-4px)';
      e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.15)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = 'none';
    }}
    >
      <img 
        src={imageSrc} 
        alt={title} 
        style={{ 
          width: '100%', 
          height: 'auto',
          display: 'block',
          borderBottom: '1px solid #e5e7eb'
        }} 
      />
      <div style={{ padding: '1.5rem' }}>
        <h3 style={{ marginTop: 0, fontSize: '1.3rem', color: '#1f2937' }}>{title}</h3>
        <p style={{ color: '#6b7280', margin: 0, lineHeight: '1.6' }}>{description}</p>
      </div>
    </div>
  );
}
