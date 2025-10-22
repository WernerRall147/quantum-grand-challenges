import Head from 'next/head';

export default function Home() {
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
