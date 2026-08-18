import Head from 'next/head';
import Link from 'next/link';
import MermaidDiagram from '../components/MermaidDiagram';

// Deliberately describes service roles, not deployed resource names, endpoints
// or identifiers. See the note rendered at the foot of the page.

const REQUEST_FLOW = `flowchart TD
  U["Browser<br/>static site"] -->|"HTTPS, problem description"| API["Evaluator API<br/>container"]

  API --> RET["Retrieval<br/>hybrid keyword + vector search"]
  RET --> EMB["Embedding model"]
  RET --> IDX[("Algorithm knowledge index")]

  API --> ROUTER["Deterministic router<br/>decides the verdict"]
  ROUTER --> FILT["Utility-scale filters<br/>+ hardware readiness"]

  API --> LLM["Model router<br/>writes the explanation"]
  LLM -.->|"may disagree, recorded<br/>as dissent, never overrides"| ROUTER

  API --> COST["Cost model<br/>live retail prices + pinned fallback"]
  API --> GEN["Code generation<br/>quantum kernel or infrastructure"]

  ROUTER --> RESP["Response<br/>verdict, evidence, references"]
  LLM --> RESP
  COST --> RESP
  GEN --> RESP
  RESP --> U

  style ROUTER fill:#1e3a8a,stroke:#60a5fa,color:#fff
  style RESP fill:#14532d,stroke:#4ade80,color:#fff
  style LLM fill:#4c1d95,stroke:#a78bfa,color:#fff`;

const TRUST_BOUNDARY = `flowchart LR
  subgraph PUB["Public"]
    B["Browser"]
  end
  subgraph PLAT["Managed platform, identity-bound"]
    A["Evaluator API"]
    S[("Search index")]
    M["Model endpoints"]
  end
  B -->|"anonymous, read-only<br/>no write path to the index"| A
  A -->|"managed identity"| S
  A -->|"managed identity"| M

  style PUB fill:#fef3c7,stroke:#d97706
  style PLAT fill:#eff6ff,stroke:#2563eb`;

const LAYERS = [
  {
    name: 'Retrieval',
    role: 'Finds the closest known algorithms to the problem description, using keyword and vector search together.',
    note: 'Supplies evidence. It does not decide anything. A close match is not proof that a problem is quantum.',
    colour: '#0369a1',
    bg: '#f0f9ff',
    border: '#bae6fd',
  },
  {
    name: 'Deterministic router',
    role: 'Applies fixed rules to the retrieved evidence and the problem text, and produces the verdict and the recommended platform.',
    note: 'This is the part that decides. Same input, same output, every time. It is plain code with unit tests, not a model.',
    colour: '#1d4ed8',
    bg: '#eff6ff',
    border: '#bfdbfe',
  },
  {
    name: 'Utility-scale filters',
    role: 'Checks proven speedup, I/O cost, error-correction overhead, whether the problem is naturally quantum, and whether the crossover is reachable.',
    note: 'A problem has to survive all five to be treated as a quantum candidate.',
    colour: '#a16207',
    bg: '#fefce8',
    border: '#fde68a',
  },
  {
    name: 'Language model',
    role: 'Writes the human-readable assessment and cites the retrieved references.',
    note: 'It explains the verdict, it does not set it. When the model reaches a different conclusion, the disagreement is recorded rather than silently applied.',
    colour: '#6d28d9',
    bg: '#f5f3ff',
    border: '#ddd6fe',
  },
  {
    name: 'Cost model',
    role: 'Prices a reference run on quantum, AI/ML and HPC using live retail rates, falling back to pinned rates when the pricing service is unreachable.',
    note: 'Per-unit rates across three different billing models. Context, not a verdict.',
    colour: '#b45309',
    bg: '#fff7ed',
    border: '#fed7aa',
  },
  {
    name: 'Code generation',
    role: 'Emits a quantum kernel for quantum verdicts, or infrastructure-as-code for classical ones, plus a resource estimate.',
    note: 'Optional. Off by default because it roughly triples the response time.',
    colour: '#0f766e',
    bg: '#f0fdfa',
    border: '#99f6e4',
  },
];

export default function Architecture() {
  return (
    <>
      <Head>
        <title>Architecture | Quantum Grand Challenges</title>
        <meta name="description" content="How the Quantum Advantage Evaluator is put together: retrieval, a deterministic router, utility-scale filters, and a language model that explains rather than decides." />
      </Head>

      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        <Link href="/" style={{ color: '#0070f3', textDecoration: 'none', fontSize: '0.9rem' }}>
          &larr; Back to Dashboard
        </Link>

        <h1 style={{ fontSize: '2.5rem', marginTop: '1rem', marginBottom: '0.5rem' }}>Architecture</h1>
        <p style={{ color: '#666', fontSize: '1.1rem', marginBottom: '2rem', maxWidth: '70ch' }}>
          How the evaluator is put together, and which part is actually responsible for the answer.
          The short version: retrieval gathers evidence, deterministic code decides, and the language
          model explains. Those three jobs are kept separate on purpose.
        </p>

        <section style={{ padding: '1.25rem 1.5rem', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '10px', marginBottom: '2rem' }}>
          <h2 style={{ marginTop: 0, fontSize: '1.15rem', color: '#1e3a8a' }}>The one design decision that matters</h2>
          <p style={{ margin: 0, color: '#1e40af', fontSize: '0.95rem', lineHeight: 1.6 }}>
            The verdict comes from deterministic code, not from the model. The model writes the prose
            around it. If the model reaches a different conclusion it is recorded as dissent and shown,
            but it does not change the answer. This is the difference between a tool you can audit and
            a tool that sounds confident.
          </p>
        </section>

        <section style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.4rem' }}>Request flow</h2>
          <p style={{ color: '#64748b', fontSize: '0.95rem', margin: '0.25rem 0 1rem' }}>
            One evaluation, start to finish.
          </p>
          <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '10px', padding: '1.25rem' }}>
            <MermaidDiagram chart={REQUEST_FLOW} />
          </div>
        </section>

        <section style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.4rem' }}>What each layer is for</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
            {LAYERS.map((l) => (
              <div key={l.name} style={{ padding: '1.1rem 1.25rem', background: l.bg, border: `1px solid ${l.border}`, borderRadius: '10px' }}>
                <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.05rem', color: l.colour }}>{l.name}</h3>
                <p style={{ margin: '0 0 0.6rem', fontSize: '0.9rem', color: '#334155', lineHeight: 1.55 }}>{l.role}</p>
                <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748b', lineHeight: 1.5, fontStyle: 'italic' }}>{l.note}</p>
              </div>
            ))}
          </div>
        </section>

        <section style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.4rem' }}>Trust boundary</h2>
          <p style={{ color: '#64748b', fontSize: '0.95rem', margin: '0.25rem 0 1rem', maxWidth: '70ch' }}>
            The browser can ask questions. It cannot write to the knowledge index. Everything behind the
            API authenticates with a managed identity rather than a key, and there is no ingestion path
            reachable from the public web. That matters because the index is what the router reasons over:
            anyone who could add documents to it could change the verdicts.
          </p>
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem' }}>
            <MermaidDiagram chart={TRUST_BOUNDARY} theme="default" />
          </div>
        </section>

        <section style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.4rem' }}>Operational shape</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
            {[
              { k: 'Front end', v: 'Static export, served from a CDN. No server-side rendering, no secrets in the bundle.' },
              { k: 'API', v: 'Single container, kept warm so the first request of the day is not the slow one.' },
              { k: 'Typical evaluation', v: 'Tens of seconds. Retrieval and the model dominate; the router itself is instant.' },
              { k: 'Monitoring', v: 'A scheduled probe runs a real evaluation and checks the verdict, then opens and closes an issue automatically.' },
            ].map((o) => (
              <div key={o.k} style={{ padding: '1rem 1.15rem', background: 'white', border: '1px solid #e2e8f0', borderRadius: '10px' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b' }}>{o.k}</div>
                <div style={{ fontSize: '0.88rem', color: '#334155', marginTop: '0.35rem', lineHeight: 1.5 }}>{o.v}</div>
              </div>
            ))}
          </div>
        </section>

        <section style={{ padding: '1.25rem 1.5rem', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px' }}>
          <h2 style={{ marginTop: 0, fontSize: '1.05rem', color: '#334155' }}>A note on what is shown here</h2>
          <p style={{ margin: 0, color: '#64748b', fontSize: '0.88rem', lineHeight: 1.6, maxWidth: '75ch' }}>
            This page names service roles, not deployed resources. Instance names, hostnames, deployment
            names, index names, subscription and tenant identifiers are all left out on purpose. Knowing
            the shape of the system should not tell you where to knock.
          </p>
        </section>

        <div style={{ marginTop: '2.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <Link href="/evaluate/" style={{ padding: '0.7rem 1.5rem', background: '#667eea', color: 'white', borderRadius: '8px', textDecoration: 'none', fontWeight: 600 }}>
            Try the evaluator &rarr;
          </Link>
          <Link href="/costs/" style={{ padding: '0.7rem 1.5rem', background: '#f1f5f9', color: '#334155', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, border: '1px solid #e2e8f0' }}>
            How costs are modelled
          </Link>
        </div>
      </div>
    </>
  );
}
