import { useState, useEffect, useRef } from 'react';

// Renders a Mermaid diagram client-side. Falls back to the diagram source on
// any render error so the architecture is always visible.
export default function MermaidDiagram({ chart, theme = 'dark' }: { chart: string; theme?: 'dark' | 'default' }) {
  const ref = useRef<HTMLDivElement>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({ startOnLoad: false, theme, securityLevel: 'loose' });
        const id = 'mmd-' + Math.random().toString(36).slice(2);
        const { svg } = await mermaid.render(id, chart);
        if (!cancelled && ref.current) ref.current.innerHTML = svg;
      } catch {
        if (!cancelled) setFailed(true);
      }
    })();
    return () => { cancelled = true; };
  }, [chart, theme]);
  if (failed) {
    return (
      <pre style={{ margin: 0, color: '#7dd3fc', fontSize: '0.8rem', overflow: 'auto', padding: '0.75rem', background: '#020617', borderRadius: '6px' }}>
        {chart}
      </pre>
    );
  }
  return <div ref={ref} style={{ overflow: 'auto', textAlign: 'center' }} />;
}
