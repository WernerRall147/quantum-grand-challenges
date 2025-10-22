import Head from 'next/head';

export default function Home() {
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

  const problemHighlights: ProblemCardProps[] = [
    {
      title: 'QAE Risk Analysis',
      status: '✅ Analytical baseline',
      description: 'Quantum-inspired amplitude estimation for financial tail risk',
    },
    {
      title: 'Hubbard Model',
      status: '✅ Analytical baseline',
      description: 'Two-site Hubbard benchmark with classical + Q# parity',
    },
    {
      title: 'High-Frequency Trading',
      status: '✅ Classical baseline',
      description: 'Knowledge-driven moving-average strategy ready for quantum upgrades',
    },
    {
      title: 'Drug Discovery',
      status: '✅ Classical baseline',
      description: 'Docking energy scaffold with Q# VQE placeholder',
    },
    {
      title: 'Protein Folding',
      status: '✅ Classical baseline',
      description: 'Contact-map scoring with amplitude-encoding Q# stub',
    },
    {
      title: 'Factorization',
      status: '✅ Classical baseline',
      description: 'Pollard Rho analytics paving the way for Shor order finding',
    },
    {
      title: 'Post-Quantum Cryptography',
      status: '✅ Classical baseline',
      description: 'Attack-cost estimator preparing amplitude-amplified sieving studies',
    },
    {
      title: 'Quantum Machine Learning',
      status: '✅ Classical baseline',
      description: 'Kernel ridge benchmark ready for quantum feature maps',
    },
    {
      title: 'Quantum Optimization',
      status: '✅ Classical baseline',
      description: 'Weighted tardiness scheduler poised for QAOA upgrades',
    },
    {
      title: 'Climate Modeling',
      status: '✅ Classical baseline',
      description: 'Diffusion energy balance ready for HHL-style solvers',
    },
    {
      title: 'Materials Discovery',
      status: '✅ Classical baseline',
      description: 'Surrogate cluster expansion primed for quantum spectroscopy',
    },
    {
      title: 'Database Search',
      status: '✅ Classical baseline',
      description: 'Query complexity model poised for amplitude amplification',
    },
    {
      title: 'Error Correction',
      status: '✅ Classical baseline',
      description: 'Repetition-code analytics setting the stage for surface codes',
    },
    {
      title: 'Nuclear Physics',
      status: '✅ Classical baseline',
      description: 'Pionless EFT diagonalization with adiabatic state-prep stub',
    },
    {
      title: 'Photovoltaics',
      status: '✅ Classical baseline',
      description: 'Shockley-Queisser heuristic with exciton preview in Q#',
    },
    {
      title: 'Quantum Chromodynamics',
      status: '✅ Classical baseline',
      description: 'Coarse lattice plaquette baseline with gauge-walk stub',
    },
    {
      title: 'Space Mission Planning',
      status: '✅ Classical baseline',
      description: 'Patched-conic mission baseline with quantum annealing preview',
    },
  ];

  return (
    <>
      <Head>
        <title>Quantum Grand Challenges</title>
        <meta name="description" content="Systematic exploration of 20 quantum computing challenges" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>🌌 Quantum Grand Challenges</h1>
        <p style={{ fontSize: '1.25rem', color: '#666', marginBottom: '2rem' }}>
          Systematic exploration of 20 of the world's most challenging scientific problems using quantum computing
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
            Starting with our most mature scaffolds, here is what the classical data already tells us and where the quantum roadmap is heading.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
            <CaseStudyCard
              title="QAE Risk Tail Probability"
              classicalHeadline="47,500 Monte Carlo samples for 0.1% precision"
              classicalDetails="Log-normal portfolio losses need 47k draws (≈1.28 s Python runtime) to pin down a 4σ tail at 0.0805±0.0012."
              quantumHeadline="Amplitude estimation trims queries to O(1/ε) ≈ 1.5k"
              quantumDetails="The Q# stub is wired for a controlled-rotation oracle; once implemented, the estimator pipeline will chart logical qubits vs. ε."
              linkHref="https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/03_qae_risk"
            />
            <CaseStudyCard
              title="Hubbard Model Charge Gap"
              classicalHeadline="Exact diagonalization: Δc = 5.66 at U/t = 4"
              classicalDetails="The two-site half-filled benchmark shows a growing Mott gap as interaction strength increases, captured in `estimates/classical_baseline.json`."
              quantumHeadline="Phase estimation baseline ready"
              quantumDetails="The Q# entry point mirrors the classical parity check, paving the way for adiabatic state prep + phase estimation with estimator hooks."
              linkHref="https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/01_hubbard"
            />
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

        <div style={{ marginTop: '4rem', padding: '2rem', background: '#f8f9fa', borderRadius: '8px' }}>
          <h2>📊 Current Status</h2>
          <ul style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
            <li><strong>Q# Prototypes:</strong> Placeholders in place for finance, chemistry, error correction, nuclear physics, photovoltaics, QCD, and mission planning</li>
            <li><strong>Classical Baselines:</strong> All twenty challenges now have reproducible baselines with JSON outputs and plots</li>
            <li><strong>Visualization:</strong> Dashboard cards and per-problem plots refreshed after each scaffold</li>
            <li><strong>CI/CD:</strong> Automated testing and static export ready for GitHub Pages</li>
          </ul>
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
