import Head from 'next/head';

export default function Home() {
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
          <ProblemCard 
            title="QAE Risk Analysis"
            status="✅ Complete"
            description="Quantum Amplitude Estimation for financial tail risk probability"
          />
          <ProblemCard 
            title="Hubbard Model"
            status="🔄 In Progress"
            description="Strongly-correlated electron systems for superconductivity"
          />
          <ProblemCard 
            title="15+ More Challenges"
            status="⏳ Planned"
            description="Catalysis, drug discovery, cryptography, climate modeling, and more"
          />
        </div>

        <div style={{ marginTop: '4rem', padding: '2rem', background: '#f8f9fa', borderRadius: '8px' }}>
          <h2>📊 Current Status</h2>
          <ul style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
            <li><strong>Q# Implementation:</strong> Building and running</li>
            <li><strong>Classical Baselines:</strong> Monte Carlo analysis complete</li>
            <li><strong>Visualization:</strong> Interactive plots generated</li>
            <li><strong>CI/CD:</strong> Automated testing and deployment</li>
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
