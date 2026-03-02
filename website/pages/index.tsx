import Head from 'next/head';
import Image from 'next/image';
import { activeWorkQueue, pipelineStages, problemHighlights } from '../data/projectStatus';

export default function Home() {
  const basePath = process.env.NODE_ENV === 'production' ? '/quantum-grand-challenges' : '';
  const withBasePath = (path: string) => `${basePath}${path}`;

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
            Stage C implementations now anchor the portfolio while Stage B tracks continue progressing under policy-gated evidence requirements.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
            <CaseStudyCard
              title="QAE Risk Analysis (Stage C Complete)"
              classicalHeadline="Monte Carlo: 18.98% ± 0.39% (10k samples)"
              classicalDetails="Classical baseline achieves 0% error vs theoretical for tail risk P(Loss > 2.5) on log-normal(0,1) distribution."
              quantumHeadline="Canonical QAE: 594k qubits, 6.4s, 965k T-states"
              quantumDetails="QAE kernel and Stage C evidence artifacts are published, including calibration and runtime mapping outputs."
              linkHref="https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/03_qae_risk"
            />
            <CaseStudyCard
              title="Database Search (Stage C Complete)"
              classicalHeadline="Search baselines: 16, 32, and 4096-item instances"
              classicalDetails="Classical search and verification harnesses provide reproducible reference outputs for Grover comparisons."
              quantumHeadline="Canonical Grover: quadratic search behavior"
              quantumDetails="Multi-target oracle and measurement validation support the Stage C evidence bundle for database search."
              linkHref="https://github.com/WernerRall147/quantum-grand-challenges/tree/main/problems/15_database_search"
            />
            <CaseStudyCard
              title="Hubbard Model (Stage B Complete)"
              classicalHeadline="Exact diagonalization: Δc = 5.66 at U/t = 4"
              classicalDetails="Two-site half-filled Hubbard model with classical baseline achieving perfect accuracy for ground state energy and Mott gap."
              quantumHeadline="VQE: 79k qubits, 114μs | HHL: 18.7k qubits, 52ms"
              quantumDetails="Reproducible baselines and scaffolded quantum flows are complete; next target is Stage C evidence gating."
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
            <li><strong>✅ Stage Coverage:</strong> 20/20 problems include objective maturity gates and advantage-claim contracts</li>
            <li><strong>✅ Current KPI Snapshot:</strong> 18 problems at Stage B and 2 problems at Stage C</li>
            <li><strong>✅ Stage C Tracks:</strong> QAE Risk Analysis and Database Search are policy-enforced at Stage C</li>
            <li><strong>🟢 Stage B Tracks:</strong> Eighteen additional problems are baseline-complete and queued for Stage C promotion</li>
            <li><strong>✅ Governance Automation:</strong> CI enforces maturity policy and publishes markdown/JSON KPI artifacts</li>
            <li><strong>✅ 6 Publication-Quality Visualizations:</strong> Qubit requirements, runtime, T-states, scaling, advantage map, timeline</li>
            <li><strong>✅ Resource Estimates:</strong> Azure Quantum analysis across 3 architectures (gate_ns_e3, gate_ns_e4, maj_ns_e4)</li>
            <li><strong>✅ Classical Baselines:</strong> All twenty challenges have reproducible baselines with JSON outputs and plots</li>
            <li><strong>✅ CI/CD:</strong> Automated testing and static export ready for GitHub Pages</li>
          </ul>
          <div style={{ marginTop: '1.5rem', padding: '1.5rem', background: 'white', borderRadius: '8px', border: '2px solid #10b981' }}>
            <h3 style={{ marginTop: 0, color: '#10b981' }}>🎉 Latest Achievement: Stage-Gated Portfolio Rollout</h3>
            <p style={{ color: '#666', marginBottom: 0 }}>
              Maturity gates, contract coverage, KPI reporting, and CI policy enforcement are now active across all 20 challenge tracks.
              This creates a single evidence standard for promoting Stage B scaffolds to Stage C implementations and future Stage D claims.
            </p>
          </div>
        </div>

        <section style={{ marginTop: '3rem', padding: '2rem', background: '#eef6ff', borderRadius: '12px' }}>
          <h2 style={{ marginTop: 0 }}>🚧 Active Work Queue</h2>
          <p style={{ color: '#4b5c79' }}>
            Current promotion queue for moving Stage B tracks into Stage C with benchmarked kernel evidence.
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
              href={problem.href}
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
  href: string;
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

function statusBadgeStyle(status: string): { text: string; bg: string; fg: string } {
  const normalized = status.toLowerCase();
  if (normalized.includes('stage d')) {
    return { text: 'Stage D', bg: '#ede9fe', fg: '#5b21b6' };
  }
  if (normalized.includes('stage c')) {
    return { text: 'Stage C', bg: '#dcfce7', fg: '#166534' };
  }
  if (normalized.includes('stage b')) {
    return { text: 'Stage B', bg: '#dbeafe', fg: '#1e40af' };
  }
  if (normalized.includes('complete')) {
    return { text: 'Complete', bg: '#dcfce7', fg: '#166534' };
  }
  if (normalized.includes('implemented') || normalized.includes('pending')) {
    return { text: 'Implemented', bg: '#fef3c7', fg: '#92400e' };
  }
  return { text: 'Stage A', bg: '#fef3c7', fg: '#92400e' };
}

function ProblemCard({ title, status, description, href }: ProblemCardProps) {
  const badge = statusBadgeStyle(status);
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
      <div style={{ margin: '0.5rem 0' }}>
        <span style={{ background: badge.bg, color: badge.fg, fontWeight: 700, fontSize: '0.8rem', borderRadius: '999px', padding: '0.2rem 0.65rem' }}>
          {badge.text}
        </span>
      </div>
      <p style={{ color: '#0070f3', fontWeight: '600', margin: '0.5rem 0' }}>{status}</p>
      <p style={{ color: '#666', margin: 0 }}>{description}</p>
      <a href={href} style={{ display: 'inline-block', marginTop: '0.75rem', color: '#0ea5e9', textDecoration: 'none', fontWeight: 600 }}>
        Open problem folder →
      </a>
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
      <Image
        src={imageSrc}
        alt={title}
        width={1200}
        height={675}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 600px"
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
