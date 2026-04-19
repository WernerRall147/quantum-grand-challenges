import Head from 'next/head';
import Link from 'next/link';
import { useState } from 'react';
import { problemHighlights } from '../data/projectStatus';

export default function Home() {
  const basePath = process.env.NODE_ENV === 'production' ? '/quantum-grand-challenges' : '';
  const withBasePath = (path: string) => `${basePath}${path}`;
  const [showArchived, setShowArchived] = useState(false);

  const active = problemHighlights.filter((p) => !p.status.toLowerCase().includes('archived'));
  const archived = problemHighlights.filter((p) => p.status.toLowerCase().includes('archived'));

  return (
    <>
      <Head>
        <title>Quantum Grand Challenges</title>
        <meta name="description" content="Systematic exploration of the world's most challenging scientific problems using quantum computing, AI and HPC" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href={withBasePath('/favicon.ico')} />
      </Head>
      <main style={{ maxWidth: '1100px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif', color: '#1a1a2e' }}>

        {/* Hero */}
        <header style={{ textAlign: 'center', padding: '3rem 0 2rem' }}>
          <h1 style={{ fontSize: '2.8rem', marginBottom: '0.75rem', letterSpacing: '-0.02em' }}>
            Quantum Grand Challenges
          </h1>
          <p style={{ fontSize: '1.2rem', color: '#555', maxWidth: '700px', margin: '0 auto 2rem', lineHeight: 1.6 }}>
            Systematic exploration of the world&apos;s most challenging scientific problems using quantum computing, AI and HPC
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/evaluate/" style={{ padding: '0.8rem 2rem', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, fontSize: '1.05rem' }}>
              Evaluate Your Problem &rarr;
            </Link>
            <Link href="/compare/" style={{ padding: '0.8rem 2rem', background: '#1e293b', color: 'white', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, fontSize: '1.05rem' }}>
              Compare All Problems
            </Link>
          </div>
        </header>

        {/* Troyer Filters */}
        <section style={{ padding: '1.5rem 2rem', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
          <h2 style={{ marginTop: 0, fontSize: '1.4rem' }}>Troyer Utility-Scale Filters</h2>
          <p style={{ color: '#64748b', margin: '0.25rem 0 1rem', fontSize: '0.95rem' }}>
            Every problem is evaluated against Dr. Matthias Troyer&apos;s 5 filters. Only problems that pass <strong>all five</strong> are classified as active candidates for quantum advantage.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
            {[
              { id: 'F1', q: 'Proven speedup?', kill: 'VQE/QAOA fail' },
              { id: 'F2', q: 'I/O survives?', kill: 'O(N) loading erases gain' },
              { id: 'F3', q: 'QEC survives?', kill: 'Overhead kills quadratic' },
              { id: 'F4', q: 'Naturally quantum?', kill: 'Feynman criterion' },
              { id: 'F5', q: 'Crossover feasible?', kill: 'Realistic problem size' },
            ].map((f) => (
              <div key={f.id} style={{ background: 'white', borderRadius: '8px', padding: '0.75rem 1rem', border: '1px solid #e2e8f0' }}>
                <strong style={{ color: '#334155' }}>{f.id}</strong>
                <div style={{ fontSize: '0.9rem', color: '#475569', marginTop: '0.25rem' }}>{f.q}</div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.15rem' }}>{f.kill}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Active Problems */}
        <section style={{ marginTop: '2.5rem' }}>
          <h2 style={{ fontSize: '1.4rem' }}>
            Active Problems
            <span style={{ fontSize: '0.9rem', fontWeight: 400, color: '#64748b', marginLeft: '0.5rem' }}>
              {active.length} pass all Troyer filters
            </span>
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
            {active.map((p) => (
              <ProblemCard key={p.title} {...p} />
            ))}
          </div>
        </section>

        {/* Archived Problems */}
        <section style={{ marginTop: '2.5rem' }}>
          <button
            type="button"
            onClick={() => setShowArchived(!showArchived)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer', padding: 0,
              fontSize: '1.4rem', fontWeight: 700, color: '#1a1a2e', display: 'flex', alignItems: 'center', gap: '0.5rem',
            }}
          >
            Archived Problems
            <span style={{ fontSize: '0.9rem', fontWeight: 400, color: '#94a3b8' }}>
              {archived.length} &mdash; Troyer filter failures
            </span>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', marginLeft: '0.25rem' }}>
              {showArchived ? '▼' : '▶'}
            </span>
          </button>
          {showArchived && (
            <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '0.75rem' }}>
              {archived.map((p) => (
                <div key={p.title} style={{ padding: '1rem', border: '1px solid #e5e7eb', borderRadius: '8px', background: '#fafafa' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ color: '#374151' }}>{p.title}</strong>
                    <span style={{ background: '#f1f5f9', color: '#64748b', fontSize: '0.7rem', fontWeight: 600, borderRadius: '999px', padding: '0.15rem 0.5rem' }}>Archived</span>
                  </div>
                  <p style={{ color: '#6b7280', fontSize: '0.85rem', margin: '0.4rem 0 0' }}>{p.description}</p>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Key Numbers */}
        <section style={{ marginTop: '2.5rem', padding: '1.5rem 2rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '12px', color: 'white' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1.5rem', textAlign: 'center' }}>
            {[
              { val: '9', label: 'Active problems' },
              { val: '120+', label: 'Azure Quantum runs' },
              { val: '160', label: 'Resource estimates' },
              { val: '47', label: 'Algorithms indexed' },
              { val: '5', label: 'Troyer filters' },
            ].map((s) => (
              <div key={s.label}>
                <div style={{ fontSize: '2rem', fontWeight: 700 }}>{s.val}</div>
                <div style={{ fontSize: '0.85rem', color: '#e0e7ff' }}>{s.label}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Research */}
        <section style={{ marginTop: '2.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          <div style={{ padding: '1.5rem', border: '1px solid #d1fae5', borderRadius: '10px', background: '#f0fdf4' }}>
            <h3 style={{ marginTop: 0, color: '#166534' }}>Methodology Paper</h3>
            <p style={{ color: '#374151', fontSize: '0.9rem' }}>
              Covers the maturity gate model, Troyer utility-scale filters, 9 algorithm families, automated CI validation, and Azure Quantum integration.
            </p>
            <a href="https://github.com/WernerRall147/quantum-grand-challenges/blob/main/docs/paper/methodology-paper.md" style={{ color: '#166534', fontWeight: 600, textDecoration: 'none' }}>
              Read Paper &rarr;
            </a>
          </div>
          <div style={{ padding: '1.5rem', border: '1px solid #d1fae5', borderRadius: '10px', background: '#f0fdf4' }}>
            <h3 style={{ marginTop: 0, color: '#166534' }}>Cite This Work</h3>
            <pre style={{ background: '#dcfce7', padding: '0.75rem', borderRadius: '6px', fontSize: '0.75rem', overflow: 'auto', margin: '0.5rem 0 0' }}>{`@software{rall2026quantum,
  author = {Rall, Werner},
  title = {Quantum Grand Challenges},
  year = {2026},
  doi = {10.5281/zenodo.19222021}
}`}</pre>
          </div>
        </section>

        {/* Quick Start */}
        <section style={{ marginTop: '2.5rem' }}>
          <h2 style={{ fontSize: '1.4rem' }}>Quick Start</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
            <CommandBlock title="Setup" commands={[
              'git clone https://github.com/WernerRall147/quantum-grand-challenges.git',
              'cd quantum-grand-challenges',
              'pip install qsharp numpy scipy matplotlib',
            ]} />
            <CommandBlock title="Run a Problem" commands={[
              'cd problems/01_hubbard',
              'make classical   # baseline',
              'make build       # Q# compilation',
              'make run         # execute',
            ]} />
            <CommandBlock title="Evaluate" commands={[
              'pip install azure-cosmos azure-search-documents',
              'python agents/orchestrator/evaluate.py \\',
              '  "Simulate ground state of a 50-atom catalyst"',
            ]} />
          </div>
        </section>

        {/* Footer */}
        <footer style={{ marginTop: '4rem', padding: '1.5rem 0', borderTop: '1px solid #e2e8f0', textAlign: 'center', color: '#94a3b8', fontSize: '0.9rem' }}>
          <p style={{ margin: '0 0 0.5rem' }}>
            Built with Q#, Python, and Next.js &middot; AGPL-3.0 &middot;{' '}
            <a href="https://doi.org/10.5281/zenodo.19222021" style={{ color: '#667eea', textDecoration: 'none' }}>DOI: 10.5281/zenodo.19222021</a>
          </p>
          <a href="https://github.com/WernerRall147/quantum-grand-challenges" style={{ color: '#667eea', textDecoration: 'none' }}>
            View on GitHub &rarr;
          </a>
        </footer>
      </main>
    </>
  );
}

function ProblemCard({ title, status, description, href }: { title: string; status: string; description: string; href: string }) {
  const match = href.match(/problems\/(\d{2}_[a-z_]+)/);
  const detailHref = match ? `/problems/${match[1]}/` : href;
  const algo = status.match(/- (\w[\w\s/]+)/)?.[1]?.trim() || '';

  return (
    <Link href={detailHref} style={{ textDecoration: 'none', color: 'inherit' }}>
      <div style={{
        padding: '1.25rem', border: '1px solid #e2e8f0', borderRadius: '10px', background: 'white',
        transition: 'box-shadow 0.2s', cursor: 'pointer', height: '100%',
      }}
      onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)'}
      onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{title}</h3>
          {algo && (
            <span style={{ background: '#ede9fe', color: '#5b21b6', fontSize: '0.7rem', fontWeight: 700, borderRadius: '999px', padding: '0.15rem 0.55rem', whiteSpace: 'nowrap' }}>
              {algo}
            </span>
          )}
        </div>
        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: '0.5rem 0 0', lineHeight: 1.5 }}>{description}</p>
      </div>
    </Link>
  );
}

function CommandBlock({ title, commands }: { title: string; commands: string[] }) {
  return (
    <div style={{ background: '#0f172a', color: '#e2e8f0', borderRadius: '8px', padding: '1.25rem', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace' }}>
      <h3 style={{ marginTop: 0, marginBottom: '0.75rem', fontSize: '1rem', color: '#38bdf8' }}>{title}</h3>
      <code style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem', lineHeight: 1.6 }}>{commands.join('\n')}</code>
    </div>
  );
}
