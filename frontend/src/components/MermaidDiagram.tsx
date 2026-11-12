import React, { useEffect, useId, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'strict',
  fontFamily: 'Inter, system-ui, sans-serif',
});

interface MermaidDiagramProps {
  chart: string;
  title?: string;
}

export const MermaidDiagram: React.FC<MermaidDiagramProps> = ({ chart, title }) => {
  const rawId = useId().replace(/[^a-zA-Z0-9]/g, '');
  const [svgContent, setSvgContent] = useState<string>('');
  const [renderFailed, setRenderFailed] = useState<boolean>(false);

  useEffect(() => {
    let active = true;
    async function renderChart() {
      if (!chart || !chart.trim()) return;
      try {
        setRenderFailed(false);
        const { svg } = await mermaid.render(`mermaid_${rawId}_${Date.now()}`, chart.trim());
        if (active) {
          setSvgContent(svg);
        }
      } catch {
        if (active) {
          setRenderFailed(true);
        }
      }
    }
    renderChart();
    return () => {
      active = false;
    };
  }, [chart, rawId]);

  const parsedNodes = chart
    .split('\n')
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith('flowchart') && !l.startsWith('graph'));

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
      {title && (
        <div className="mb-3 flex items-center justify-between border-b border-slate-800/80 pb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">{title}</span>
          <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[11px] text-slate-400">
            Architecture / Flow Diagram
          </span>
        </div>
      )}
      {svgContent && !renderFailed ? (
        <div
          className="overflow-x-auto py-2 [&_svg]:mx-auto [&_svg]:max-w-full"
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      ) : (
        <div className="space-y-2 py-2">
          <div className="flex flex-wrap items-center gap-2">
            {parsedNodes.map((line, idx) => (
              <div
                key={idx}
                className="rounded-lg border border-indigo-500/30 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200"
              >
                {line}
              </div>
            ))}
          </div>
          <pre className="mt-2 overflow-x-auto rounded bg-slate-950/90 p-2.5 font-mono text-xs text-slate-400">
            {chart}
          </pre>
        </div>
      )}
    </div>
  );
};
