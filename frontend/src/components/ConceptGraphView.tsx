import React from 'react';
import { ConceptItem } from '../types/axiom';
import { ArrowRight, BookOpen, Code2, Sparkles } from 'lucide-react';

interface ConceptGraphViewProps {
  concepts: ConceptItem[];
  selectedConceptId: number | null;
  onSelectConcept: (concept: ConceptItem) => void;
  onJumpToBuilder?: (concept: ConceptItem) => void;
}

export const ConceptGraphView: React.FC<ConceptGraphViewProps> = ({
  concepts,
  selectedConceptId,
  onSelectConcept,
  onJumpToBuilder,
}) => {
  const prereqBadge = (level: string) => {
    const l = level.toLowerCase();
    if (l === 'essential')
      return 'bg-rose-500/15 text-rose-300 border-rose-500/30';
    if (l === 'recommended')
      return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
    return 'bg-sky-500/15 text-sky-300 border-sky-500/30';
  };

  const masteryBadge = (status: string) => {
    if (status === 'synthesized')
      return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    if (status === 'practicing' || status === 'exploring')
      return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40';
    return 'bg-slate-800 text-slate-400 border-slate-700';
  };

  return (
    <div className="space-y-4">
      {/* Visual SVG Knowledge Constellation & Dependency Graph */}
      <div className="relative overflow-x-auto rounded-2xl border border-slate-800 bg-slate-950/90 p-5">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-indigo-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Interactive Concept & Prerequisite Constellation
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-rose-400" /> Essential Prerequisite
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-amber-400" /> Recommended
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-sky-400" /> Optional / Frontier
            </span>
          </div>
        </div>

        <svg className="h-60 w-full min-w-[760px]" viewBox="0 0 960 260">
          <defs>
            <marker
              id="arrow-dep"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#6366f1" />
            </marker>
          </defs>

          {/* Draw Dependency Edges */}
          {concepts.map((c, idx) => {
            if (idx >= concepts.length - 1) return null;
            const next = concepts[idx + 1];
            const x1 = 95 + idx * (780 / Math.max(1, concepts.length - 1));
            const y1 = idx % 2 === 0 ? 85 : 175;
            const x2 = 95 + (idx + 1) * (780 / Math.max(1, concepts.length - 1));
            const y2 = (idx + 1) % 2 === 0 ? 85 : 175;
            return (
              <g key={`edge-${c.id}-${next.id}`}>
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="#4f46e5"
                  strokeWidth="2"
                  strokeDasharray={c.prerequisite_level === 'optional' ? '5,5' : undefined}
                  markerEnd="url(#arrow-dep)"
                  opacity="0.65"
                />
              </g>
            );
          })}

          {/* Draw Concept Constellation Nodes */}
          {concepts.map((c, idx) => {
            const cx = 95 + idx * (780 / Math.max(1, concepts.length - 1));
            const cy = idx % 2 === 0 ? 85 : 175;
            const isSelected = c.id === selectedConceptId;
            const ringColor =
              c.prerequisite_level === 'essential'
                ? '#fb7185'
                : c.prerequisite_level === 'recommended'
                ? '#fbbf24'
                : '#38bdf8';

            return (
              <g
                key={c.id}
                className="cursor-pointer transition-transform hover:scale-105"
                onClick={() => onSelectConcept(c)}
              >
                {isSelected && (
                  <circle cx={cx} cy={cy} r={34} fill="none" stroke="#818cf8" strokeWidth="2" opacity="0.6" />
                )}
                <circle
                  cx={cx}
                  cy={cy}
                  r={25}
                  fill={isSelected ? '#312e81' : '#0f172a'}
                  stroke={ringColor}
                  strokeWidth={isSelected ? '3' : '2'}
                />
                <text
                  x={cx}
                  y={cy + 4}
                  textAnchor="middle"
                  fill="#f8fafc"
                  fontSize="11"
                  fontWeight="600"
                >
                  C{idx + 1}
                </text>
                <text
                  x={cx}
                  y={cy + 44}
                  textAnchor="middle"
                  fill={isSelected ? '#c7d2fe' : '#94a3b8'}
                  fontSize="11"
                  fontWeight={isSelected ? '600' : '500'}
                >
                  {c.title.length > 24 ? `${c.title.slice(0, 22)}…` : c.title}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Navigable Concept Cards */}
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
        {concepts.map((c, idx) => {
          const isSelected = c.id === selectedConceptId;
          return (
            <div
              key={c.id}
              onClick={() => onSelectConcept(c)}
              className={`group cursor-pointer rounded-xl border p-4 transition-all ${
                isSelected
                  ? 'border-indigo-500 bg-indigo-950/25 shadow-lg shadow-indigo-950/30'
                  : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
              }`}
            >
              <div className="mb-2 flex items-center justify-between gap-2">
                <span className="font-mono text-xs text-slate-400">
                  NODE 0{idx + 1} · {c.category.toUpperCase()}
                </span>
                <span
                  className={`rounded-full border px-2 py-0.5 text-[11px] font-medium capitalize ${prereqBadge(
                    c.prerequisite_level
                  )}`}
                >
                  {c.prerequisite_level}
                </span>
              </div>
              <h4 className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300">{c.title}</h4>
              <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-400">{c.summary}</p>
              <div className="mt-3 flex items-center justify-between border-t border-slate-800/80 pt-2.5">
                <span
                  className={`rounded border px-2 py-0.5 text-[10px] font-medium uppercase ${masteryBadge(
                    c.mastery_status
                  )}`}
                >
                  {c.mastery_status} ({Math.round(c.mastery_score * 100)}%)
                </span>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectConcept(c);
                    }}
                    className="inline-flex items-center gap-1 text-xs font-medium text-indigo-400 hover:text-indigo-300"
                  >
                    <BookOpen className="h-3.5 w-3.5" /> Scholar
                  </button>
                  {onJumpToBuilder && c.builder_milestone_id && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onJumpToBuilder(c);
                      }}
                      className="inline-flex items-center gap-1 text-xs font-medium text-emerald-400 hover:text-emerald-300"
                    >
                      <Code2 className="h-3.5 w-3.5" /> Builder <ArrowRight className="h-3 w-3" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
