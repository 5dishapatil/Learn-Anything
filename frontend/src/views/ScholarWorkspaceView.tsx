import React, { useState } from 'react';
import {
  ConceptItem,
  ConceptWorkspaceData,
} from '../types/axiom';
import { MermaidDiagram } from '../components/MermaidDiagram';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import {
  ArrowRight,
  BookOpen,
  Brain,
  CheckCircle2,
  Code2,
  ExternalLink,
  FileDown,
  Layers,
  Lightbulb,
  PanelLeftClose,
  PanelLeftOpen,
  Play,
  Sparkles,
  Target,
  Video,
} from 'lucide-react';

interface ScholarWorkspaceViewProps {
  concepts: ConceptItem[];
  workspace: ConceptWorkspaceData | null;
  onSelectConcept: (conceptId: number) => void;
  onChangeDepth: (depth: string, format: string, useLiveLlm: boolean) => Promise<void>;
  onSubmitFeynman: (userExplanation: string, revisedExplanation?: string, uncertainties?: string) => Promise<void>;
  onReviewFlashcard: (flashcardId: number, outcome: 'again' | 'hard' | 'good' | 'easy') => Promise<void>;
  onAttemptRecall: (questionId: number, response: string) => Promise<void>;
  onSubmitThinkDeeper: (questionId: number, reasoning: string) => Promise<void>;
  onSwitchToBuilder: (conceptId: number, milestoneId: number | null) => void;
  onExportObsidian: (exportType: 'concept' | 'think_deeper', entityId: number) => void;
}

const FEYNMAN_STAGES = [
  {
    stage: 1,
    title: 'Stage 1: Problem & Jargon Deconstruction',
    focus: 'Strip away buzzwords and state the raw physical or computational constraint.',
    promptHint: 'State in plain words what fundamental problem today’s topic solves and what fails without it.',
  },
  {
    stage: 2,
    title: 'Stage 2: Plain-Language Causal Mechanism',
    focus: 'Explain step-by-step how inputs transform into outputs as if teaching a sharp peer.',
    promptHint: 'Walk through the exact causal chain from input to output without hiding behind undefined terms.',
  },
  {
    stage: 3,
    title: 'Stage 3: Hidden Assumption & Gap Audit',
    focus: 'Expose unspoken assumptions, boundary conditions, and invariant requirements.',
    promptHint: 'Identify which mathematical or engineering assumptions must hold for this mechanism to work.',
  },
  {
    stage: 4,
    title: 'Stage 4: Socratic Counterfactual Inquiry',
    focus: 'Test your mental model against edge cases and scale limits.',
    promptHint: 'Explain what happens when a key parameter or assumption is violated or pushed to extremes.',
  },
  {
    stage: 5,
    title: 'Stage 5: Refined First-Principles Synthesis',
    focus: 'Repair identified gaps and connect the intuitive model to the formal equations.',
    promptHint: 'Synthesize both the intuitive physical picture and the governing mathematical relationship.',
  },
  {
    stage: 6,
    title: 'Stage 6: Formal & Engineering Precision Mastery',
    focus: 'Lock in complete theoretical and implementation mastery ready for production code.',
    promptHint: 'State the complete formal specification, complexity/trade-offs, and verification invariants.',
  },
];

export const ScholarWorkspaceView: React.FC<ScholarWorkspaceViewProps> = ({
  concepts,
  workspace,
  onSelectConcept,
  onChangeDepth,
  onSubmitFeynman,
  onReviewFlashcard,
  onAttemptRecall,
  onSubmitThinkDeeper,
  onSwitchToBuilder,
  onExportObsidian,
}) => {
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true);
  const [activeEmbeddedVideoUrl, setActiveEmbeddedVideoUrl] = useState<string | null>(null);

  // Interactive Reconstruction & End-of-Day Consolidation State
  const [feynmanDraft, setFeynmanDraft] = useState('');
  const [feynmanRevision, setFeynmanRevision] = useState('');
  const [feynmanUncertainties, setFeynmanUncertainties] = useState('');
  const [flippedCards, setFlippedCards] = useState<Record<number, boolean>>({});
  const [recallAnswers, setRecallAnswers] = useState<Record<number, string>>({});
  const [thinkAnswers, setThinkAnswers] = useState<Record<number, string>>({});
  const [busy, setBusy] = useState(false);

  if (!workspace) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center rounded-2xl border border-slate-800/80 bg-slate-900/40 p-12 text-center">
        <BookOpen className="mb-4 h-12 w-12 text-slate-600" />
        <h3 className="font-serif text-2xl font-bold text-slate-200">Scholar Road Sanctuary</h3>
        <p className="mt-2 max-w-md font-serif text-lg text-slate-400">
          Generate or select a learning roadmap in Explore &amp; Onboard to open your Day-by-Day First-Principles Masterclass.
        </p>
      </div>
    );
  }

  const { concept, lesson, feynman_history, recall_questions, flashcards, think_deeper_questions } = workspace;
  const latestFeynman = feynman_history.length > 0 ? feynman_history[feynman_history.length - 1] : null;

  const currentDayIdx = Math.max(0, concepts.findIndex((c) => c.id === concept.id));
  const currentDayNum = currentDayIdx + 1;
  const nextConcept = currentDayIdx + 1 < concepts.length ? concepts[currentDayIdx + 1] : null;
  const assignedFeynmanStage = FEYNMAN_STAGES[currentDayIdx % FEYNMAN_STAGES.length];

  // Global locked typography: Text Serif + A3 size
  const fontClass = 'font-serif';
  const sizeClasses = 'text-[20.5px] leading-[1.9]';

  // Extract verified specific YouTube videos and reading citations attached to this Day's lesson sections
  const allCitations = (lesson?.sections || []).flatMap((s) => s.citations || []);
  const seenUrls = new Set<string>();
  const uniqueCitations = allCitations.filter((c) => {
    const key = c.url || c.title;
    if (!key || seenUrls.has(key)) return false;
    seenUrls.add(key);
    return true;
  });

  const videoCitations = uniqueCitations.filter(
    (c) => c.epistemic_status === 'WATCH (VIDEO)' && c.url && c.url.includes('watch?v=')
  );
  const readingCitations = uniqueCitations.filter(
    (c) => c.epistemic_status !== 'WATCH (VIDEO)' && c.url
  );

  const epistemicBadge = (label: string) => {
    if (label === 'CORE') {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    }
    if (label === 'APPROXIMATE') {
      return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    }
    return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
  };

  return (
    <div className="relative -mx-4 -my-6 flex min-h-[calc(100vh-5rem)] flex-col bg-slate-950 sm:-mx-8 font-sans">
      {/* Top Scholar Chrome Bar (No T-Serif / A3 buttons, No Right Drawer button) */}
      <header className="sticky top-0 z-30 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 bg-slate-950/95 px-6 py-3.5 backdrop-blur-md">
        <div className="flex items-center gap-3.5">
          <button
            type="button"
            onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
            title={leftSidebarOpen ? 'Hide Day-by-Day Roadmap' : 'Show Day-by-Day Roadmap'}
            className="rounded-lg border border-slate-800 p-2 text-slate-400 hover:bg-slate-900 hover:text-slate-200"
          >
            {leftSidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
          </button>

          <div className="flex items-center gap-2.5">
            <span className="rounded-full bg-indigo-500/15 border border-indigo-500/30 px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider text-indigo-300">
              DAY {String(currentDayNum).padStart(2, '0')} OF {concepts.length}
            </span>
            <span className="hidden text-sm text-slate-500 sm:inline">·</span>
            <h1 className="max-w-xl truncate font-serif text-lg font-bold text-white">
              {concept.title}
            </h1>
          </div>
        </div>

        {/* Depth & Action Controls */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {lesson && (
            <div className="flex items-center rounded-xl border border-slate-800 bg-slate-900/80 p-1 font-sans text-xs font-semibold">
              {(['concise', 'detailed', 'research'] as const).map((d) => (
                <button
                  key={d}
                  type="button"
                  disabled={busy}
                  onClick={async () => {
                    setBusy(true);
                    await onChangeDepth(d, lesson.learning_format, true);
                    setBusy(false);
                  }}
                  className={`rounded-lg px-3 py-1.5 capitalize transition-colors ${
                    lesson.current_depth === d
                      ? 'bg-indigo-600 font-bold text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          )}

          <button
            type="button"
            onClick={() => onExportObsidian('concept', concept.id)}
            title="Export this Day's note to Obsidian"
            className="hidden items-center gap-1.5 rounded-xl border border-slate-800 px-3 py-1.5 font-sans text-xs font-semibold text-slate-200 hover:bg-slate-900 md:inline-flex"
          >
            <FileDown className="h-3.5 w-3.5 text-indigo-400" />
            <span>Export Note</span>
          </button>

          <button
            type="button"
            onClick={() => onSwitchToBuilder(concept.id, concept.builder_milestone_id)}
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-1.5 font-sans text-xs font-bold text-white shadow-sm hover:bg-emerald-500 transition-colors"
          >
            <Code2 className="h-4 w-4" />
            <span>Open Day {currentDayNum} Coding Lab</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </header>

      {/* Main Body: Left Day-by-Day Planner + Full-Width Center Reader */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar: Day-by-Day Curriculum Planner */}
        {leftSidebarOpen && (
          <aside className="w-80 shrink-0 border-r border-slate-800/80 bg-[#0b101e] p-4 overflow-y-auto">
            <div className="mb-4 flex items-center justify-between">
              <span className="font-mono text-xs font-extrabold uppercase tracking-wider text-indigo-400">
                Day-by-Day Curriculum
              </span>
              <span className="font-mono text-xs text-slate-400">
                Day {currentDayNum} / {concepts.length}
              </span>
            </div>

            <nav className="space-y-2.5">
              {concepts.map((c, idx) => {
                const isCurrent = c.id === concept.id;
                const isMastered = c.mastery_status === 'synthesized' || c.mastery_score >= 0.8;
                const dayNum = idx + 1;
                const stageNum = (idx % 6) + 1;
                return (
                  <div
                    key={c.id}
                    className={`rounded-xl border p-3.5 transition-all ${
                      isCurrent
                        ? 'border-indigo-500/50 bg-indigo-950/40 text-white shadow-md'
                        : 'border-slate-800/60 bg-slate-950/40 text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() => {
                        setActiveEmbeddedVideoUrl(null);
                        onSelectConcept(c.id);
                      }}
                      className="flex w-full items-start gap-3 text-left"
                    >
                      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-indigo-500/40 bg-indigo-950/60 font-mono text-xs font-bold text-indigo-300">
                        {isMastered ? (
                          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                        ) : (
                          `D${dayNum}`
                        )}
                      </div>
                      <div className="flex-1 overflow-hidden">
                        <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                          Day {String(dayNum).padStart(2, '0')} · Feynman Stage {stageNum}
                        </div>
                        <div className="font-serif text-[15px] font-bold leading-snug text-slate-100 mt-0.5">
                          {c.title}
                        </div>
                      </div>
                    </button>

                    <div className="mt-2.5 flex items-center justify-between border-t border-slate-800/70 pt-2">
                      <span className="font-mono text-[10px] uppercase text-slate-400">
                        {Math.round((c.mastery_score || 0.2) * 100)}% Mastery
                      </span>
                      <button
                        type="button"
                        onClick={() => onSwitchToBuilder(c.id, c.builder_milestone_id)}
                        className="inline-flex items-center gap-1 rounded-md bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5 font-mono text-[10px] font-bold text-emerald-300 hover:bg-emerald-500/25"
                      >
                        <Code2 className="h-3 w-3" /> Day {dayNum} Lab →
                      </button>
                    </div>
                  </div>
                );
              })}
            </nav>
          </aside>
        )}

        {/* Center Main Workspace: Structured into WHAT TO DO -> HOW TO DO IT -> WHAT WE'VE LEARNT SO FAR */}
        <main className="flex-1 overflow-y-auto px-6 py-8 sm:px-10 md:px-14">
          <article className="mx-auto max-w-[82ch] space-y-12 font-serif text-[19px] leading-[1.85]">
            {/* =====================================================================
                HEADER & LIVE QWEN3.5:9B DEEP SYNTHESIS TRIGGER
               ===================================================================== */}
            <div className="space-y-4 border-b border-slate-800/80 pb-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-lg bg-indigo-600 px-3.5 py-1 font-mono text-xs font-extrabold uppercase tracking-wider text-white">
                    DAY {String(currentDayNum).padStart(2, '0')} MASTERCLASS
                  </span>
                  <span className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-1 font-mono text-xs font-bold text-amber-300">
                    {assignedFeynmanStage.title.toUpperCase()}
                  </span>
                  <span className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-1 font-mono text-xs uppercase text-slate-300">
                    {concept.difficulty_level}
                  </span>
                </div>

                {lesson && (
                  <button
                    type="button"
                    disabled={busy}
                    onClick={async () => {
                      setBusy(true);
                      await onChangeDepth('research', lesson.learning_format, true);
                      setBusy(false);
                    }}
                    className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-2 font-sans text-xs font-extrabold text-white shadow-lg hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 transition-all"
                  >
                    <Sparkles className="h-3.5 w-3.5" />
                    {busy
                      ? 'Synthesizing with qwen3.5:9b...'
                      : '⚡ Deep-Synthesize Day Content & Code with qwen3.5:9b'}
                  </button>
                )}
              </div>

              <h1 className="font-serif text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
                Day {currentDayNum}: {concept.title}
              </h1>

              {/* 3-Pillar Progression Overview Strip */}
              <div className="grid grid-cols-1 gap-3 pt-2 sm:grid-cols-3">
                <a
                  href="#part-what-to-do"
                  className="rounded-xl border border-indigo-500/40 bg-indigo-950/25 p-3.5 hover:border-indigo-400 transition-colors"
                >
                  <div className="font-mono text-xs font-extrabold uppercase tracking-wider text-indigo-400">
                    PART I · WHAT TO DO TODAY
                  </div>
                  <div className="mt-1 font-serif text-base font-bold text-white">
                    Mission, Specific Video Lectures &amp; Papers
                  </div>
                </a>
                <a
                  href="#part-how-to-do-it"
                  className="rounded-xl border border-emerald-500/40 bg-emerald-950/20 p-3.5 hover:border-emerald-400 transition-colors"
                >
                  <div className="font-mono text-xs font-extrabold uppercase tracking-wider text-emerald-400">
                    PART II · HOW TO DO IT
                  </div>
                  <div className="mt-1 font-serif text-base font-bold text-white">
                    Derivations, Worked Walkthrough &amp; Feynman Cycle
                  </div>
                </a>
                <a
                  href="#part-what-we-learnt"
                  className="rounded-xl border border-purple-500/40 bg-purple-950/20 p-3.5 hover:border-purple-400 transition-colors"
                >
                  <div className="font-mono text-xs font-extrabold uppercase tracking-wider text-purple-400">
                    PART III · WHAT WE&apos;VE LEARNT SO FAR
                  </div>
                  <div className="mt-1 font-serif text-base font-bold text-white">
                    End-of-Day Active Recall &amp; Think Deeper
                  </div>
                </a>
              </div>
            </div>

            {/* =====================================================================
                PART I: WHAT TO DO TODAY (Mission + Specific Verified YouTube Videos + Papers)
               ===================================================================== */}
            <section id="part-what-to-do" className="space-y-6">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 font-mono text-sm font-extrabold text-white">
                  I
                </span>
                <div>
                  <div className="font-mono text-xs font-bold uppercase tracking-wider text-indigo-400">
                    PART I · WHAT TO DO TODAY
                  </div>
                  <h2 className="font-serif text-2xl font-bold text-white">
                    Day {currentDayNum} Mission &amp; Specific Curated Video Lectures
                  </h2>
                </div>
              </div>

              {/* Core Day Summary Callout */}
              <div className="border-l-4 border-indigo-500 bg-indigo-950/20 rounded-r-2xl p-5 text-slate-200">
                <div className="font-mono text-xs font-bold uppercase tracking-wider text-indigo-300 mb-2">
                  DAY {currentDayNum} OBJECTIVE &amp; FIRST-PRINCIPLES SCOPE
                </div>
                <MarkdownRenderer
                  content={concept.summary}
                  className={`${fontClass} ${sizeClasses} text-slate-100`}
                />
              </div>

              {/* Specific Verified YouTube Video Lectures */}
              <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 space-y-5 shadow-lg">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <span className="font-mono text-xs font-bold uppercase tracking-wider text-emerald-400">
                      📺 SPECIFIC VERIFIED YOUTUBE LECTURES FOR DAY {currentDayNum}
                    </span>
                    <h3 className="font-serif text-xl font-bold text-white mt-0.5">
                      Watch Specific Lectures Relevant to {concept.title}
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => onSwitchToBuilder(concept.id, concept.builder_milestone_id)}
                    className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 font-sans text-xs font-extrabold text-white hover:bg-emerald-500 shadow-sm"
                  >
                    <Code2 className="h-4 w-4" /> Step-by-Step Day {currentDayNum} Coding Lab →
                  </button>
                </div>

                {/* Inline Embedded YouTube Video Player when user clicks Watch Inline */}
                {activeEmbeddedVideoUrl && (
                  <div className="overflow-hidden rounded-2xl border border-indigo-500/50 bg-black shadow-2xl">
                    <div className="flex items-center justify-between bg-slate-900 px-4 py-2.5 border-b border-slate-800">
                      <span className="font-mono text-xs font-bold text-indigo-300">
                        ▶ Playing Specific Day {currentDayNum} Lecture Inline
                      </span>
                      <button
                        type="button"
                        onClick={() => setActiveEmbeddedVideoUrl(null)}
                        className="rounded-lg bg-slate-800 px-2.5 py-1 font-sans text-xs font-semibold text-slate-300 hover:text-white"
                      >
                        Close Player ✕
                      </button>
                    </div>
                    <div className="aspect-video w-full">
                      <iframe
                        src={activeEmbeddedVideoUrl}
                        title={`Day ${currentDayNum} Lecture Player`}
                        className="h-full w-full"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      />
                    </div>
                  </div>
                )}

                {videoCitations.length > 0 ? (
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                    {videoCitations.map((vid, idx) => (
                      <div
                        key={idx}
                        className="flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-950/90 overflow-hidden hover:border-indigo-500/60 transition-all shadow-md"
                      >
                        <div>
                          {vid.thumbnail_url ? (
                            <div className="relative h-36 w-full bg-slate-900 overflow-hidden">
                              <img
                                src={vid.thumbnail_url}
                                alt={vid.title}
                                className="h-full w-full object-cover opacity-90"
                              />
                              {vid.duration && (
                                <span className="absolute bottom-2 right-2 rounded bg-black/85 px-2 py-0.5 font-mono text-[11px] font-bold text-white">
                                  {vid.duration}
                                </span>
                              )}
                            </div>
                          ) : (
                            <div className="flex h-28 w-full items-center justify-center bg-indigo-950/40 text-indigo-400">
                              <Video className="h-8 w-8" />
                            </div>
                          )}

                          <div className="p-4">
                            <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                              {vid.channel || 'Verified Lecture'} {vid.duration ? `· ${vid.duration}` : ''}
                            </div>
                            <h4 className="mt-1 font-serif text-base font-bold leading-snug text-white line-clamp-2">
                              {vid.title}
                            </h4>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 border-t border-slate-800/80 bg-slate-900/50 px-4 py-3">
                          {vid.embed_url && (
                            <button
                              type="button"
                              onClick={() =>
                                setActiveEmbeddedVideoUrl(
                                  activeEmbeddedVideoUrl === vid.embed_url ? null : vid.embed_url!
                                )
                              }
                              className="inline-flex items-center gap-1 rounded-lg bg-indigo-600 px-2.5 py-1.5 font-sans text-xs font-bold text-white hover:bg-indigo-500"
                            >
                              <Play className="h-3 w-3 fill-current" /> Watch Here
                            </button>
                          )}
                          <a
                            href={vid.url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1.5 font-sans text-xs font-semibold text-slate-200 hover:border-indigo-400 hover:text-white ml-auto"
                          >
                            <span>Direct Link</span>
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 font-serif text-base text-slate-300">
                    Click <strong>⚡ Deep-Synthesize Day Content &amp; Code with qwen3.5:9b</strong> above to fetch live specific YouTube video lectures for <em>{concept.title}</em>.
                  </div>
                )}

                {/* Specific Articles & Research Papers */}
                {readingCitations.length > 0 && (
                  <div className="pt-3 border-t border-slate-800/80 space-y-2.5">
                    <div className="font-mono text-xs font-bold uppercase tracking-wider text-amber-400">
                      📖 SPECIFIC TECHNICAL ARTICLES &amp; ARXIV PAPERS TO READ TODAY
                    </div>
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                      {readingCitations.map((doc, idx) => (
                        <a
                          key={idx}
                          href={doc.url}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-950/80 p-3.5 hover:border-emerald-500/50 transition-all"
                        >
                          <div className="min-w-0">
                            <span className="font-mono text-[10px] font-bold uppercase text-emerald-400">
                              {doc.epistemic_status} · {doc.year}
                            </span>
                            <div className="truncate font-serif text-base font-bold text-white mt-0.5">
                              {doc.title}
                            </div>
                          </div>
                          <ExternalLink className="h-4 w-4 shrink-0 text-slate-400" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </section>

            {/* =====================================================================
                PART II: HOW TO DO IT (First-Principles Theory, Math, Worked Examples & Inline Feynman Cycle)
               ===================================================================== */}
            {lesson && (
              <section id="part-how-to-do-it" className="space-y-10">
                <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 font-mono text-sm font-extrabold text-white">
                    II
                  </span>
                  <div>
                    <div className="font-mono text-xs font-bold uppercase tracking-wider text-emerald-400">
                      PART II · HOW TO DO IT
                    </div>
                    <h2 className="font-serif text-2xl font-bold text-white">
                      First-Principles Derivation, Worked Walkthrough &amp; Day {currentDayNum} Feynman Cycle
                    </h2>
                  </div>
                </div>

                {/* 1. The Fundamental Problem & Why It Exists */}
                <div className="space-y-4">
                  <h3 className="font-serif text-2xl font-bold tracking-tight text-slate-100">
                    1. The Fundamental Problem &amp; Why It Exists
                  </h3>
                  <MarkdownRenderer
                    content={lesson.problem_statement}
                    className={`${fontClass} ${sizeClasses} text-slate-200`}
                  />
                  <MarkdownRenderer
                    content={lesson.why_it_exists}
                    className={`${fontClass} ${sizeClasses} text-slate-300`}
                  />
                </div>

                {/* 2. First-Principles Intuition & Real-World Analogy */}
                <div className="space-y-4 border-t border-slate-800/80 pt-8">
                  <h3 className="font-serif text-2xl font-bold tracking-tight text-slate-100">
                    2. First-Principles Intuition &amp; Mechanism
                  </h3>
                  <MarkdownRenderer
                    content={lesson.first_principles_intuition}
                    className={`${fontClass} ${sizeClasses} text-slate-200`}
                  />
                  {lesson.real_world_analogies && (
                    <div className="my-5 rounded-2xl border border-amber-500/30 bg-amber-950/15 p-6">
                      <div className="flex items-center gap-2 font-mono text-xs font-bold uppercase tracking-wider text-amber-400 mb-2">
                        <Lightbulb className="h-4 w-4" /> Physical Intuition &amp; Analogy
                      </div>
                      <MarkdownRenderer
                        content={lesson.real_world_analogies}
                        className={`${fontClass} ${sizeClasses} text-slate-200`}
                      />
                    </div>
                  )}
                </div>

                {/* 3. Mathematical Formulation & Governing Equations */}
                {lesson.mathematical_derivations && (
                  <div className="space-y-4 border-t border-slate-800/80 pt-8">
                    <h3 className="font-serif text-2xl font-bold tracking-tight text-slate-100">
                      3. Mathematical Formulation, Derivations &amp; Governing Invariants
                    </h3>
                    <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-inner">
                      <MarkdownRenderer
                        content={lesson.mathematical_derivations}
                        className={`${fontClass} ${sizeClasses} text-slate-100`}
                      />
                    </div>
                  </div>
                )}

                {/* 4. Step-by-Step Worked Example & Reference Implementation */}
                {(lesson.worked_examples || lesson.code_examples) && (
                  <div className="space-y-4 border-t border-slate-800/80 pt-8">
                    <h3 className="font-serif text-2xl font-bold tracking-tight text-slate-100">
                      4. Step-by-Step Worked Example &amp; Reference Code
                    </h3>
                    {lesson.worked_examples && (
                      <MarkdownRenderer
                        content={lesson.worked_examples}
                        className={`${fontClass} ${sizeClasses} text-slate-200`}
                      />
                    )}
                    {lesson.code_examples && (
                      <div className="my-4">
                        <MarkdownRenderer
                          content={lesson.code_examples}
                          className={`${fontClass} ${sizeClasses}`}
                        />
                      </div>
                    )}
                  </div>
                )}

                {/* 5. Deep Multi-Stage Sections */}
                {lesson.sections && lesson.sections.length > 0 && (
                  <div className="space-y-8 border-t border-slate-800/80 pt-8">
                    {lesson.sections.map((sec) => {
                      const content =
                        lesson.current_depth === 'concise'
                          ? sec.concise_content
                          : lesson.current_depth === 'research'
                          ? sec.research_content
                          : sec.detailed_content;

                      return (
                        <div key={sec.id} className="rounded-2xl border border-slate-800/90 bg-slate-900/40 p-6 space-y-4">
                          <div className="flex items-center justify-between gap-2">
                            <h4 className="font-serif text-xl font-bold text-white">
                              {sec.title}
                            </h4>
                            <span
                              className={`rounded-full border px-3 py-0.5 font-mono text-xs font-bold ${epistemicBadge(
                                sec.epistemic_label
                              )}`}
                            >
                              {sec.epistemic_label}
                            </span>
                          </div>
                          <MarkdownRenderer
                            content={content}
                            className={`${fontClass} ${sizeClasses} text-slate-200`}
                          />
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* 6. Systems Architecture Diagram & Trade-offs */}
                {lesson.mermaid_diagram && (
                  <div className="space-y-4 border-t border-slate-800/80 pt-8">
                    <h3 className="font-serif text-2xl font-bold text-slate-100">
                      Systems Architecture &amp; Execution Flow
                    </h3>
                    <MermaidDiagram chart={lesson.mermaid_diagram} title={`Day ${currentDayNum} Architecture: ${concept.title}`} />
                  </div>
                )}

                {(lesson.engineering_tradeoffs || lesson.common_misconceptions) && (
                  <div className="grid grid-cols-1 gap-6 border-t border-slate-800/80 pt-8 md:grid-cols-2">
                    {lesson.engineering_tradeoffs && (
                      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
                        <h4 className="font-serif text-xl font-bold text-amber-400 mb-3">
                          Engineering Trade-offs &amp; Production Constraints
                        </h4>
                        <MarkdownRenderer
                          content={lesson.engineering_tradeoffs}
                          className={`${fontClass} ${sizeClasses} text-slate-200`}
                        />
                      </div>
                    )}
                    {lesson.common_misconceptions && (
                      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
                        <h4 className="font-serif text-xl font-bold text-rose-400 mb-3">
                          Common Misconceptions to Avoid
                        </h4>
                        <MarkdownRenderer
                          content={lesson.common_misconceptions}
                          className={`${fontClass} ${sizeClasses} text-slate-200`}
                        />
                      </div>
                    )}
                  </div>
                )}

                {/* 7. INLINE DAY-WISE FEYNMAN LEARNING ENGINE (Applied Directly to Day k's Structure) */}
                <div className="rounded-2xl border-2 border-indigo-500/40 bg-indigo-950/20 p-6 sm:p-8 space-y-6 shadow-xl">
                  <div className="flex flex-wrap items-center justify-between gap-4 border-b border-indigo-500/30 pb-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white">
                        <Brain className="h-5 w-5" />
                      </div>
                      <div>
                        <span className="font-mono text-xs font-extrabold uppercase tracking-wider text-indigo-300">
                          DAY {currentDayNum} FEYNMAN RECONSTRUCTION CYCLE · INLINE ACTIVE SYNTHESIS
                        </span>
                        <h3 className="font-serif text-2xl font-bold text-white">
                          {assignedFeynmanStage.title}
                        </h3>
                      </div>
                    </div>
                    <span className="rounded-xl border border-indigo-500/40 bg-indigo-900/50 px-3.5 py-1.5 font-mono text-xs font-bold text-indigo-200">
                      Current Stage Reached: {latestFeynman?.stage_reached ?? assignedFeynmanStage.stage} / 6
                    </span>
                  </div>

                  {/* 6-Stage Progression Bar Highlighting Today's Feynman Stage */}
                  <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-6">
                    {FEYNMAN_STAGES.map((st) => {
                      const isTodayStage = st.stage === assignedFeynmanStage.stage;
                      const isCompletedStage = (latestFeynman?.stage_reached ?? 0) >= st.stage;
                      return (
                        <div
                          key={st.stage}
                          className={`rounded-xl border p-2.5 text-left transition-all ${
                            isTodayStage
                              ? 'border-indigo-400 bg-indigo-600/30 text-white shadow-md'
                              : isCompletedStage
                              ? 'border-emerald-500/40 bg-emerald-950/25 text-emerald-200'
                              : 'border-slate-800 bg-slate-900/60 text-slate-400'
                          }`}
                        >
                          <div className="font-mono text-[11px] font-extrabold uppercase">
                            Stage {st.stage} {isTodayStage ? '· TODAY' : ''}
                          </div>
                          <div className="mt-0.5 font-serif text-xs font-semibold leading-snug line-clamp-2">
                            {st.title.replace(/^Stage \d+:\s*/, '')}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <p className={`${fontClass} text-lg text-indigo-100 leading-relaxed`}>
                    <strong>Today&apos;s Feynman Task:</strong> {assignedFeynmanStage.focus}{' '}
                    {assignedFeynmanStage.promptHint}
                  </p>

                  <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                    <div className="space-y-2">
                      <label className="block font-serif text-lg font-bold text-white">
                        1. Your First-Principles Explanation of {concept.title}:
                      </label>
                      <textarea
                        rows={5}
                        value={feynmanDraft}
                        onChange={(e) => setFeynmanDraft(e.target.value)}
                        placeholder={assignedFeynmanStage.promptHint}
                        className="w-full rounded-xl border border-slate-700 bg-slate-950 p-4 font-serif text-lg text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none leading-relaxed"
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="block font-serif text-lg font-bold text-white">
                        2. Refined Synthesis / Repairing Gaps (Optional Stage 5–6 Upgrade):
                      </label>
                      <textarea
                        rows={5}
                        value={feynmanRevision}
                        onChange={(e) => setFeynmanRevision(e.target.value)}
                        placeholder="After reviewing Socratic feedback below, refine your explanation and connect it to the mathematical formulation..."
                        className="w-full rounded-xl border border-slate-700 bg-slate-950 p-4 font-serif text-lg text-slate-100 placeholder:text-slate-500 focus:border-emerald-500 focus:outline-none leading-relaxed"
                      />
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <input
                      type="text"
                      value={feynmanUncertainties}
                      onChange={(e) => setFeynmanUncertainties(e.target.value)}
                      placeholder="Any remaining uncertainties or questions on today's topic? (Optional)"
                      className="flex-1 min-w-[260px] rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 font-serif text-base text-slate-200 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
                    />
                    <button
                      type="button"
                      disabled={!feynmanDraft.trim() || busy}
                      onClick={async () => {
                        setBusy(true);
                        await onSubmitFeynman(
                          feynmanDraft,
                          feynmanRevision.trim() ? feynmanRevision : undefined,
                          feynmanUncertainties
                        );
                        setBusy(false);
                      }}
                      className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3.5 font-sans text-sm font-extrabold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition-colors"
                    >
                      <Brain className="h-4 w-4" />
                      {busy ? 'Evaluating with qwen3.5:9b...' : 'Analyze Gaps & Advance Feynman Stage'}
                    </button>
                  </div>

                  {/* Socratic Feedback & Gap Analysis History */}
                  {feynman_history.length > 0 && (
                    <div className="space-y-4 border-t border-indigo-500/30 pt-5">
                      <div className="font-mono text-xs font-bold uppercase tracking-wider text-indigo-300">
                        SOCRATIC GAP ANALYSIS &amp; EVIDENCE-BASED FEEDBACK HISTORY
                      </div>
                      {feynman_history.slice(-2).map((h) => {
                        const fb = h.feedback;
                        return (
                          <div key={h.id} className="rounded-xl border border-slate-800 bg-slate-950/90 p-5 space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="font-serif text-lg font-bold text-white">
                                Revision v{h.version_number} (Stage {h.stage_reached} / 6)
                              </span>
                              <span className="rounded-lg bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 font-mono text-xs font-bold text-emerald-300">
                                Clarity Score: {Math.round((fb?.clarity_score ?? 0.75) * 100)}%
                              </span>
                            </div>

                            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                              {fb?.logical_gaps && fb.logical_gaps.length > 0 && (
                                <div className="rounded-xl bg-rose-950/25 p-4 text-rose-200 border border-rose-900/40">
                                  <strong className="block font-mono text-xs uppercase tracking-wider text-rose-400 mb-1.5">
                                    Identified Logical Gaps:
                                  </strong>
                                  <ul className="list-disc pl-5 space-y-1 font-serif text-base">
                                    {fb.logical_gaps.map((gap: string, i: number) => (
                                      <li key={i}>{gap}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {fb?.guided_questions && fb.guided_questions.length > 0 && (
                                <div className="rounded-xl bg-indigo-950/30 p-4 text-indigo-200 border border-indigo-900/40">
                                  <strong className="block font-mono text-xs uppercase tracking-wider text-indigo-400 mb-1.5">
                                    Socratic Guided Questions:
                                  </strong>
                                  <ul className="list-disc pl-5 space-y-1 font-serif text-base">
                                    {fb.guided_questions.map((q: string, i: number) => (
                                      <li key={i}>{q}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* =====================================================================
                PART III: WHAT WE'VE LEARNT SO FAR (End-of-Day Active Recall, Flashcards & Think Deeper)
               ===================================================================== */}
            <section id="part-what-we-learnt" className="space-y-10 border-t-2 border-slate-800 pt-10">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-600 font-mono text-sm font-extrabold text-white">
                  III
                </span>
                <div>
                  <div className="font-mono text-xs font-bold uppercase tracking-wider text-purple-400">
                    PART III · WHAT WE&apos;VE LEARNT SO FAR (END-OF-DAY CONSOLIDATION)
                  </div>
                  <h2 className="font-serif text-2xl font-bold text-white">
                    Day {currentDayNum} Active Recall Verification &amp; Think Deeper Socratic Challenges
                  </h2>
                </div>
              </div>

              {/* 3A. END-OF-DAY ACTIVE RECALL QUESTIONS & SM-2 FLASHCARDS */}
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 sm:p-8 space-y-6 shadow-lg">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div className="flex items-center gap-3">
                    <Layers className="h-6 w-6 text-indigo-400" />
                    <div>
                      <span className="font-mono text-xs font-bold uppercase tracking-wider text-indigo-400">
                        ACTIVE RECALL &amp; SM-2 SPACED REPETITION
                      </span>
                      <h3 className="font-serif text-xl font-bold text-white">
                        Test Your Retrieval Without Looking Back at the Text
                      </h3>
                    </div>
                  </div>
                  <span className="font-mono text-xs text-slate-400">
                    {recall_questions.length} Recall Prompts · {flashcards.length} Flashcards
                  </span>
                </div>

                {/* Open-Response Recall Questions */}
                {recall_questions.length > 0 && (
                  <div className="space-y-4">
                    {recall_questions.map((rq, idx) => {
                      const latestAttempt =
                        rq.attempts && rq.attempts.length > 0 ? rq.attempts[rq.attempts.length - 1] : null;
                      return (
                        <div key={rq.id} className="rounded-xl border border-slate-800 bg-slate-950/80 p-5 space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-xs font-bold uppercase text-indigo-400">
                              Recall Question {idx + 1} · {rq.difficulty}
                            </span>
                            {latestAttempt && (
                              <span className="rounded bg-emerald-500/15 px-2.5 py-0.5 font-mono text-xs font-bold text-emerald-300">
                                Score: {Math.round((latestAttempt.evidence_score || 0.8) * 100)}%
                              </span>
                            )}
                          </div>
                          <p className={`${fontClass} ${sizeClasses} font-semibold text-white`}>
                            {rq.prompt}
                          </p>
                          <div className="flex flex-col sm:flex-row gap-3">
                            <input
                              type="text"
                              value={recallAnswers[rq.id] || ''}
                              onChange={(e) => setRecallAnswers({ ...recallAnswers, [rq.id]: e.target.value })}
                              placeholder="Write your concise first-principles answer from memory..."
                              className="flex-1 rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 font-serif text-lg text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
                            />
                            <button
                              type="button"
                              disabled={!recallAnswers[rq.id]?.trim() || busy}
                              onClick={async () => {
                                setBusy(true);
                                await onAttemptRecall(rq.id, recallAnswers[rq.id]);
                                setBusy(false);
                              }}
                              className="rounded-xl bg-indigo-600 px-5 py-3 font-sans text-xs font-extrabold uppercase tracking-wider text-white hover:bg-indigo-500 disabled:opacity-40 shrink-0"
                            >
                              Verify Answer
                            </button>
                          </div>
                          {latestAttempt && (
                            <div className="rounded-xl border border-indigo-500/30 bg-indigo-950/25 p-4 font-serif text-base text-slate-200 space-y-1">
                              <div>
                                <strong className="text-emerald-300">Evaluation:</strong> {latestAttempt.ai_feedback}
                              </div>
                              <div className="text-slate-300">
                                <strong className="text-indigo-300">Reference Answer:</strong> {rq.reference_answer}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* SM-2 Flashcards Grid */}
                {flashcards.length > 0 && (
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2 pt-2">
                    {flashcards.map((fc) => {
                      const isFlipped = flippedCards[fc.id];
                      return (
                        <div
                          key={fc.id}
                          onClick={() => setFlippedCards({ ...flippedCards, [fc.id]: !isFlipped })}
                          className="cursor-pointer rounded-2xl border border-slate-800 bg-slate-950/90 p-5 transition-all hover:border-indigo-500/50 flex flex-col justify-between space-y-4"
                        >
                          <div>
                            <div className="flex items-center justify-between font-mono text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                              <span>{isFlipped ? 'BACK: ANSWER & INVARIANT' : 'FRONT: FLASHCARD (CLICK TO FLIP)'}</span>
                              {fc.schedule && (
                                <span className="text-indigo-400">Interval: {fc.schedule.interval_days}d</span>
                              )}
                            </div>
                            <p className="font-serif text-lg font-medium text-slate-100 leading-relaxed">
                              {isFlipped ? fc.back : fc.front}
                            </p>
                          </div>

                          {isFlipped && (
                            <div
                              className="flex gap-2 border-t border-slate-800 pt-3"
                              onClick={(e) => e.stopPropagation()}
                            >
                              {(['again', 'hard', 'good', 'easy'] as const).map((outcome) => (
                                <button
                                  key={outcome}
                                  type="button"
                                  onClick={() => onReviewFlashcard(fc.id, outcome)}
                                  className="flex-1 rounded-lg border border-slate-700 bg-slate-900 py-2 text-center font-sans text-xs font-bold capitalize text-slate-200 hover:bg-indigo-600 hover:text-white transition-colors"
                                >
                                  {outcome}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* 3B. END-OF-DAY THINK DEEPER SOCRATIC CHALLENGES */}
              <div className="rounded-2xl border border-purple-500/40 bg-purple-950/15 p-6 sm:p-8 space-y-6 shadow-lg">
                <div className="flex items-center justify-between border-b border-purple-500/30 pb-4">
                  <div className="flex items-center gap-3">
                    <Sparkles className="h-6 w-6 text-purple-400" />
                    <div>
                      <span className="font-mono text-xs font-bold uppercase tracking-wider text-purple-300">
                        THINK DEEPER · COUNTERFACTUAL &amp; SYSTEMS TRADE-OFF CHALLENGES
                      </span>
                      <h3 className="font-serif text-xl font-bold text-white">
                        Push Beyond Textbooks: Question Assumptions &amp; Failure Modes
                      </h3>
                    </div>
                  </div>
                  <span className="font-mono text-xs text-purple-300">
                    {think_deeper_questions.length} Socratic Challenges
                  </span>
                </div>

                <div className="space-y-5">
                  {think_deeper_questions.map((q, idx) => {
                    const hasAnswered = q.responses && q.responses.length > 0;
                    return (
                      <div key={q.id} className="rounded-2xl border border-slate-800 bg-slate-950/90 p-6 space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="rounded-md bg-purple-500/15 border border-purple-500/30 px-3 py-1 font-mono text-xs font-bold uppercase text-purple-300">
                            Challenge {idx + 1} · {q.question_category}
                          </span>
                          {hasAnswered && (
                            <span className="flex items-center gap-1.5 font-mono text-xs font-bold text-emerald-400">
                              <CheckCircle2 className="h-4 w-4" /> Socratic Critique Unlocked
                            </span>
                          )}
                        </div>

                        <MarkdownRenderer
                          content={q.prompt}
                          className={`${fontClass} ${sizeClasses} font-bold text-white`}
                        />

                        {q.why_this_question_matters && (
                          <p className="font-serif text-base italic text-slate-400">
                            Why this matters: {q.why_this_question_matters}
                          </p>
                        )}

                        <textarea
                          rows={3}
                          value={thinkAnswers[q.id] || ''}
                          onChange={(e) => setThinkAnswers({ ...thinkAnswers, [q.id]: e.target.value })}
                          placeholder="Formulate your first-principles hypothesis and trade-off analysis before unlocking the model research discussion..."
                          className="w-full rounded-xl border border-slate-700 bg-slate-900 p-4 font-serif text-lg text-slate-100 placeholder:text-slate-500 focus:border-purple-500 focus:outline-none leading-relaxed"
                        />

                        <div className="flex justify-end">
                          <button
                            type="button"
                            disabled={!thinkAnswers[q.id]?.trim() || busy}
                            onClick={async () => {
                              setBusy(true);
                              await onSubmitThinkDeeper(q.id, thinkAnswers[q.id]);
                              setBusy(false);
                            }}
                            className="inline-flex items-center gap-2 rounded-xl bg-purple-600 px-6 py-3 font-sans text-xs font-extrabold uppercase tracking-wider text-white hover:bg-purple-500 disabled:opacity-40 transition-colors"
                          >
                            <Sparkles className="h-4 w-4" />
                            {busy ? 'Evaluating with qwen3.5:9b...' : 'Submit Reasoning for Socratic Critique'}
                          </button>
                        </div>

                        {hasAnswered && q.responses && q.responses.length > 0 && (
                          <div className="mt-4 rounded-xl border border-purple-500/30 bg-purple-950/20 p-5 space-y-3">
                            <div className="font-mono text-xs font-bold uppercase tracking-wider text-purple-300">
                              Socratic Critique &amp; Research Synthesis:
                            </div>
                            <MarkdownRenderer
                              content={q.responses[q.responses.length - 1].reasoning_analysis}
                              className={`${fontClass} text-lg text-slate-200`}
                            />
                            {q.model_research_discussion && (
                              <div className="border-t border-purple-500/20 pt-3">
                                <strong className="font-mono text-xs uppercase tracking-wider text-emerald-300 block mb-1">
                                  Unlocked First-Principles Research Discussion:
                                </strong>
                                <MarkdownRenderer
                                  content={q.model_research_discussion}
                                  className={`${fontClass} text-lg text-slate-200`}
                                />
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* 3C. DAY COMPLETION & NEXT ACTION FOOTER */}
              <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-emerald-500/40 bg-emerald-950/20 p-6 shadow-lg">
                <div className="flex items-center gap-3">
                  <Target className="h-7 w-7 text-emerald-400 shrink-0" />
                  <div>
                    <div className="font-mono text-xs font-bold uppercase tracking-wider text-emerald-400">
                      COMPLETED DAY {currentDayNum} THEORY, FEYNMAN &amp; RECALL?
                    </div>
                    <div className="font-serif text-xl font-bold text-white">
                      Now build and verify Day {currentDayNum}&apos;s implementation in the Builder Road Lab
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    onClick={() => onSwitchToBuilder(concept.id, concept.builder_milestone_id)}
                    className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-3 font-sans text-xs font-extrabold uppercase tracking-wider text-white hover:bg-emerald-500 shadow-lg transition-all"
                  >
                    <Code2 className="h-4 w-4" /> Launch Day {currentDayNum} Builder Lab →
                  </button>

                  {nextConcept && (
                    <button
                      type="button"
                      onClick={() => {
                        setActiveEmbeddedVideoUrl(null);
                        onSelectConcept(nextConcept.id);
                      }}
                      className="inline-flex items-center gap-2 rounded-xl border border-indigo-500/40 bg-indigo-950/40 px-5 py-3 font-sans text-xs font-extrabold uppercase tracking-wider text-indigo-200 hover:bg-indigo-900/60 hover:text-white transition-all"
                    >
                      <span>Advance to Day {currentDayNum + 1}</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            </section>
          </article>
        </main>
      </div>
    </div>
  );
};
