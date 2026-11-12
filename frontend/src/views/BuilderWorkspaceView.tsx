import React, { useEffect, useState } from 'react';
import { ProjectFullData, ProjectMilestoneData } from '../types/axiom';
import { MermaidDiagram } from '../components/MermaidDiagram';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import {
  AlertTriangle,
  BookOpen,
  Check,
  CheckCircle2,
  Code2,
  FileCode,
  FileText,
  Flame,
  Info,
  Layers,
  Lightbulb,
  Play,
  RotateCcw,
  Save,
  Sparkles,
  Target,
  Terminal,
  X,
} from 'lucide-react';

interface BuilderWorkspaceViewProps {
  project: ProjectFullData | null;
  selectedMilestoneId: number | null;
  onSelectMilestone: (milestoneId: number) => void;
  onUnlockHint: (milestoneId: number, level: number) => Promise<void>;
  onCompleteMilestone: (milestoneId: number) => Promise<void>;
  onSaveArtifact: (artifactId: number, content: string) => Promise<void>;
  onVerifyArtifact: (artifactId: number) => Promise<any>;
  onSubmitReflection: (payload: {
    milestone_id: number;
    concept_id: number | null;
    what_built_or_learned: string;
    why_it_works: string;
    what_failed: string;
    what_surprised: string;
    what_to_change: string;
  }) => Promise<void>;
  onSwitchToScholar: (conceptId: number | null) => void;
  onOpenExperimentLab: () => void;
  onGoToPlanner?: () => void;
  onSynthesizeDayLab?: (conceptId: number) => Promise<void>;
}

export const BuilderWorkspaceView: React.FC<BuilderWorkspaceViewProps> = ({
  project,
  selectedMilestoneId,
  onSelectMilestone,
  onUnlockHint,
  onCompleteMilestone,
  onSaveArtifact,
  onVerifyArtifact,
  onSwitchToScholar,
  onGoToPlanner,
  onSynthesizeDayLab,
}) => {
  const [selectedArtifactId, setSelectedArtifactId] = useState<number | null>(null);
  const [editorContent, setEditorContent] = useState<string>('');
  const [verificationResult, setVerificationResult] = useState<any | null>(null);
  const [busy, setBusy] = useState(false);

  // Left Problem & Guide Tabs: 'problem' | 'guide' | 'hints' | 'break_it'
  const [activeLeftTab, setActiveLeftTab] = useState<'problem' | 'guide' | 'hints' | 'break_it'>('problem');
  // Bottom-Right Tabs: 'tests' | 'output'
  const [activeBottomRightTab, setActiveBottomRightTab] = useState<'tests' | 'output'>('tests');
  const [checkedSteps, setCheckedSteps] = useState<Record<string, boolean>>({});
  const [practiceStarterMode, setPracticeStarterMode] = useState<boolean>(false);

  useEffect(() => {
    if (project && project.artifacts.length > 0) {
      const mId = selectedMilestoneId || project.milestones[0]?.id;
      const matchingArt =
        project.artifacts.find((a) => a.milestone_id === mId) || project.artifacts[0];
      setSelectedArtifactId(matchingArt.id);
      setEditorContent(matchingArt.content);
      setVerificationResult(null);
      setPracticeStarterMode(false);
    }
  }, [project, selectedMilestoneId]);

  if (!project) {
    return (
      <div className="flex min-h-[65vh] flex-col items-center justify-center rounded-2xl border border-slate-800/90 bg-slate-900/50 p-12 text-center font-serif">
        <Code2 className="mb-4 h-14 w-14 text-indigo-400" />
        <h3 className="text-2xl font-extrabold text-white">
          Day-by-Day Hands-On Builder Workspace
        </h3>
        <p className="mt-2 max-w-lg text-lg text-slate-300 leading-relaxed">
          Generate a personalized learning roadmap in Explore &amp; Onboard to unlock your Day-wise Hands-On Coding Labs, automated 3-test-case suite, and interactive Python 3.11 sandbox.
        </p>
        {onGoToPlanner && (
          <button
            type="button"
            onClick={onGoToPlanner}
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 font-sans text-sm font-bold text-white hover:bg-indigo-500 shadow-lg transition-all"
          >
            <Sparkles className="h-4 w-4" /> Open Explore &amp; Onboard →
          </button>
        )}
      </div>
    );
  }

  const selectedMilestone: ProjectMilestoneData =
    project.milestones.find((m) => m.id === selectedMilestoneId) || project.milestones[0];

  const activeArtifact =
    project.artifacts.find((a) => a.id === selectedArtifactId) ||
    project.artifacts.find((a) => a.milestone_id === selectedMilestone.id) ||
    project.artifacts[0];

  const dayNumber = selectedMilestone.sequence_order;

  const hintTiers = selectedMilestone.hints.map((h) => ({
    level: h.level,
    label: `Hint ${h.level}: ${h.title}`,
    content: h.content,
  }));

  // Parse individual test cases from verification stdout
  const rawOutput: string = verificationResult?.output || '';
  const testCase1Passed = rawOutput.includes('[TEST CASE 1 PASS]') || verificationResult?.passed === true;
  const testCase2Passed = rawOutput.includes('[TEST CASE 2 PASS]') || verificationResult?.passed === true;
  const testCase3Passed = rawOutput.includes('[TEST CASE 3 PASS]') || verificationResult?.passed === true;
  const hasRunTests = verificationResult !== null;

  // Build starter template for anti-vibe-coding practice mode
  const buildStarterSkeleton = (fullCode: string): string => {
    const filePath = activeArtifact?.file_path || `src/day_${dayNumber}_lab.py`;
    const mainIdx = fullCode.indexOf("if __name__ == '__main__':");
    const mainHarness = mainIdx !== -1 ? fullCode.slice(mainIdx) : '';
    return (
      `"""\nDay ${dayNumber} Lab: ${selectedMilestone.title}\nFile: ${filePath}\n` +
      `Practice Mode: Implement the functions below from first principles!\n"""\nimport math\n\n` +
      `# TODO Step 1: Validate input preconditions for ${selectedMilestone.title}\n` +
      `# TODO Step 2: Implement the core Day ${dayNumber} logic so all 3 test cases below pass\n\n` +
      mainHarness
    );
  };

  const editorLines = editorContent.split('\n');
  const testDescriptions =
    selectedMilestone.basic_tests && selectedMilestone.basic_tests.length >= 3
      ? selectedMilestone.basic_tests
      : [
          `Verify primary calculation & invariant for ${selectedMilestone.title}`,
          'Verify accurate scaling & multi-element behavior',
          'Verify boundary & edge precondition guard',
        ];

  return (
    <div className="space-y-5 font-sans">
      {/* =====================================================================
          COMPACT TOP DAY-WISE SELECTOR BAR (No Left Sidebar, No Hero Clutter)
         ===================================================================== */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-800/90 bg-[#0b101e] px-5 py-3.5 shadow-lg">
        {/* Horizontal Day Pills */}
        <div className="flex items-center gap-2 overflow-x-auto py-0.5">
          {project.milestones.map((m) => {
            const isSelected = m.id === selectedMilestone.id;
            const isDone = m.status === 'completed';
            return (
              <button
                key={m.id}
                type="button"
                onClick={() => {
                  onSelectMilestone(m.id);
                  const art = project.artifacts.find((a) => a.milestone_id === m.id);
                  if (art) {
                    setSelectedArtifactId(art.id);
                    setEditorContent(art.content);
                  }
                }}
                className={`inline-flex items-center gap-2 rounded-xl border px-3.5 py-2 font-sans text-xs font-bold whitespace-nowrap transition-all ${
                  isSelected
                    ? 'border-indigo-500 bg-indigo-600 text-white shadow-md'
                    : isDone
                    ? 'border-emerald-500/40 bg-emerald-950/30 text-emerald-300 hover:bg-emerald-950/50'
                    : 'border-slate-800 bg-slate-950/80 text-slate-300 hover:border-slate-700 hover:text-white'
                }`}
              >
                {isDone ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                ) : (
                  <span className="font-mono text-[11px]">D{m.sequence_order}</span>
                )}
                <span>
                  Day {m.sequence_order}: {m.title.replace(/^Day\s*\d+\s*Lab:\s*/i, '').slice(0, 32)}
                </span>
              </button>
            );
          })}
        </div>

        {/* Right Quick Actions: Synthesize Lab with qwen3.5:9b + Switch to Day Theory */}
        <div className="flex items-center gap-2.5">
          {onSynthesizeDayLab && selectedMilestone.concept_id && (
            <button
              type="button"
              disabled={busy}
              onClick={async () => {
                setBusy(true);
                await onSynthesizeDayLab(selectedMilestone.concept_id!);
                setBusy(false);
              }}
              className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-3.5 py-2 font-sans text-xs font-extrabold text-white hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 shadow-md"
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>{busy ? 'Synthesizing...' : `Synthesize Day ${dayNumber} Lab (qwen3.5:9b)`}</span>
            </button>
          )}

          <button
            type="button"
            onClick={() => onSwitchToScholar(selectedMilestone.concept_id)}
            className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-500/40 bg-indigo-950/40 px-3.5 py-2 font-sans text-xs font-bold text-indigo-200 hover:bg-indigo-900/60 hover:text-white transition-colors"
          >
            <BookOpen className="h-3.5 w-3.5" />
            <span>Day {dayNumber} Theory &amp; Videos →</span>
          </button>
        </div>
      </div>

      {/* =====================================================================
          FULL-WIDTH 12-COLUMN WORKSPACE:
          LEFT 6 COLS = REAL PROBLEM & STEP-BY-STEP GUIDE
          RIGHT 6 COLS = PYTHON 3.11 IDE + 3 TEST CASES & SANDBOX RUNNER
         ===================================================================== */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 items-start">
        {/* LEFT 6 COLS: PROBLEM STATEMENT, STEP-BY-STEP GUIDE, HINTS & BREAK IT */}
        <div className="lg:col-span-6 rounded-2xl border border-slate-800/90 bg-[#0b101e] overflow-hidden shadow-xl flex flex-col">
          {/* Clean Header Inside Problem Panel */}
          <div className="border-b border-slate-800 bg-slate-950/90 px-6 py-5 space-y-2">
            <div className="flex items-center justify-between gap-2">
              <span className="rounded-lg bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider text-emerald-300">
                DAY {dayNumber} HANDS-ON IMPLEMENTATION LAB
              </span>
              <code className="rounded bg-slate-900 px-2.5 py-1 font-mono text-xs text-indigo-300 border border-slate-800">
                {activeArtifact?.file_path || `src/day_${dayNumber}_lab.py`}
              </code>
            </div>
            <h1 className="font-serif text-2xl sm:text-3xl font-extrabold text-white leading-snug">
              {selectedMilestone.title}
            </h1>
            <MarkdownRenderer
              content={selectedMilestone.mission}
              className="font-serif text-lg text-slate-300 leading-relaxed"
            />
          </div>

          {/* Tab Navigation Bar */}
          <div className="flex items-center border-b border-slate-800 bg-slate-950/60 px-4 pt-2 overflow-x-auto">
            {[
              { id: 'problem' as const, label: '1. Problem & Spec', icon: FileText },
              { id: 'guide' as const, label: '2. Step-by-Step Guide', icon: BookOpen },
              { id: 'hints' as const, label: `3. Progressive Hints (${selectedMilestone.unlocked_hint_level}/5)`, icon: Lightbulb },
              { id: 'break_it' as const, label: '4. Break It Lab', icon: Flame },
            ].map((t) => {
              const Icon = t.icon;
              const isActive = activeLeftTab === t.id;
              return (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setActiveLeftTab(t.id)}
                  className={`inline-flex items-center gap-2 border-b-2 px-4 py-3 font-sans text-xs font-bold whitespace-nowrap transition-all ${
                    isActive
                      ? 'border-indigo-500 text-white'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                  <span>{t.label}</span>
                </button>
              );
            })}
          </div>

          {/* Tab Content Body (Generous Height & A3 Serif Readability) */}
          <div className="p-6 space-y-6 max-h-[640px] overflow-y-auto">
            {/* TAB 1: PROBLEM & SPECIFICATION */}
            {activeLeftTab === 'problem' && (
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 font-serif text-xl font-bold text-white">
                    <Target className="h-5 w-5 text-indigo-400" />
                    <span>What To Build Today (Day {dayNumber})</span>
                  </div>
                  <MarkdownRenderer
                    content={selectedMilestone.why_this_matters}
                    className="font-serif text-[19.5px] leading-[1.85] text-slate-200"
                  />
                </div>

                {/* Step-by-Step Guide Markdown */}
                <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 space-y-3">
                  <MarkdownRenderer
                    content={selectedMilestone.step_by_step_guide}
                    className="font-serif text-[19px] leading-[1.85] text-slate-200"
                  />
                </div>

                {/* Automated Test Case Specification */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2 font-serif text-xl font-bold text-white">
                    <Layers className="h-5 w-5 text-emerald-400" />
                    <span>Required Verification Test Cases (3/3)</span>
                  </div>
                  <div className="space-y-2.5">
                    {testDescriptions.map((desc, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-3 rounded-xl border border-slate-800 bg-slate-950/90 p-4"
                      >
                        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-600/30 border border-indigo-500/50 font-mono text-xs font-extrabold text-indigo-300">
                          {idx + 1}
                        </span>
                        <span className="font-serif text-lg text-slate-200 leading-relaxed">
                          {desc}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Engineering Constraints */}
                <div className="space-y-2.5">
                  <div className="flex items-center gap-2 font-serif text-xl font-bold text-white">
                    <Info className="h-5 w-5 text-amber-400" />
                    <span>Engineering Constraints &amp; Edge Cases</span>
                  </div>
                  <ul className="space-y-2 pl-5 list-disc font-serif text-lg text-slate-300">
                    {(selectedMilestone.edge_cases || []).map((ec, i) => (
                      <li key={i}>{ec}</li>
                    ))}
                    <li>Pure Python 3.11 implementation with zero external black-box dependencies.</li>
                  </ul>
                </div>
              </div>
            )}

            {/* TAB 2: STEP-BY-STEP GUIDE & DRY-RUN TRACE */}
            {activeLeftTab === 'guide' && (
              <div className="space-y-6">
                <div className="rounded-2xl border border-indigo-500/30 bg-indigo-950/20 p-5 space-y-3">
                  <div className="font-mono text-xs font-bold uppercase tracking-wider text-indigo-300">
                    WORKED WALKTHROUGH &amp; IMPLEMENTATION BLUEPRINT
                  </div>
                  <MarkdownRenderer
                    content={selectedMilestone.pseudocode}
                    className="font-serif text-[19.5px] leading-[1.85] text-slate-200"
                  />
                </div>

                {/* Interactive Implementation Checkpoints */}
                <div className="space-y-3">
                  <div className="font-mono text-xs font-bold uppercase tracking-wider text-emerald-400">
                    INTERACTIVE BUILD CHECKPOINTS
                  </div>
                  {[
                    {
                      id: `cp-1-${selectedMilestone.id}`,
                      title: 'Checkpoint 1: Validate Preconditions & Edge Guards',
                      desc: `Reject invalid or empty inputs cleanly with ValueError in ${activeArtifact?.file_path}.`,
                    },
                    {
                      id: `cp-2-${selectedMilestone.id}`,
                      title: `Checkpoint 2: Implement Core Day ${dayNumber} Algorithm`,
                      desc: `Implement the primary domain calculation for ${selectedMilestone.title}.`,
                    },
                    {
                      id: `cp-3-${selectedMilestone.id}`,
                      title: 'Checkpoint 3: Pass All 3 Automated Sandbox Test Cases',
                      desc: 'Click "Run Code" on the right to execute the module and verify [TEST CASE 1-3 PASS].',
                    },
                  ].map((cp) => {
                    const checked = !!checkedSteps[cp.id];
                    return (
                      <div
                        key={cp.id}
                        onClick={() => setCheckedSteps((prev) => ({ ...prev, [cp.id]: !prev[cp.id] }))}
                        className={`cursor-pointer rounded-xl border p-4 transition-all ${
                          checked
                            ? 'border-emerald-500/40 bg-emerald-950/20 text-white'
                            : 'border-slate-800 bg-slate-950/80 text-slate-200 hover:border-slate-700'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={checked}
                            onChange={() => {}}
                            className="mt-1.5 h-4 w-4 rounded border-slate-700 text-emerald-500"
                          />
                          <div>
                            <div className="font-serif text-lg font-bold text-white">{cp.title}</div>
                            <p className="mt-0.5 font-serif text-base text-slate-300">{cp.desc}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {selectedMilestone.architecture_diagram && (
                  <div className="space-y-2">
                    <div className="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                      MODULE DATAFLOW ARCHITECTURE
                    </div>
                    <MermaidDiagram
                      chart={selectedMilestone.architecture_diagram}
                      title={`Day ${dayNumber} Architecture: ${selectedMilestone.title}`}
                    />
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: PROGRESSIVE HINTS (1 TO 5) */}
            {activeLeftTab === 'hints' && (
              <div className="space-y-4">
                <p className="font-serif text-lg text-slate-300">
                  Unlock hints progressively only when needed so you build genuine first-principles engineering intuition:
                </p>
                {hintTiers.map((h) => {
                  const isUnlocked = selectedMilestone.unlocked_hint_level >= h.level;
                  return (
                    <div
                      key={h.level}
                      className={`rounded-xl border p-5 transition-all ${
                        isUnlocked
                          ? 'border-indigo-500/40 bg-indigo-950/20'
                          : 'border-slate-800 bg-slate-950/70'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-lg font-bold text-white">{h.label}</span>
                        {!isUnlocked ? (
                          <button
                            type="button"
                            disabled={busy}
                            onClick={async () => {
                              setBusy(true);
                              await onUnlockHint(selectedMilestone.id, h.level);
                              setBusy(false);
                            }}
                            className="rounded-lg bg-indigo-600 px-3.5 py-1.5 font-sans text-xs font-bold text-white hover:bg-indigo-500"
                          >
                            Unlock Hint {h.level}
                          </button>
                        ) : (
                          <span className="font-mono text-xs font-bold uppercase text-emerald-400">
                            Unlocked
                          </span>
                        )}
                      </div>
                      {isUnlocked && (
                        <pre className="mt-3 whitespace-pre-wrap font-mono text-sm text-slate-200 bg-slate-950 p-4 rounded-xl border border-slate-800 overflow-x-auto leading-relaxed">
                          {h.content}
                        </pre>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* TAB 4: CONTROLLED FAILURE ("BREAK IT") CHALLENGES */}
            {activeLeftTab === 'break_it' && (
              <div className="space-y-4">
                <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-5 space-y-2">
                  <div className="flex items-center gap-2 font-mono text-xs font-extrabold uppercase tracking-wider text-amber-300">
                    <AlertTriangle className="h-4 w-4" /> Controlled Failure (&ldquo;Break It&rdquo;) Exercises
                  </div>
                  <p className="font-serif text-lg text-slate-200 leading-relaxed">
                    Great scientists and engineers test where their system breaks. Mutate the code on the right with these experiments and observe the failure output:
                  </p>
                </div>

                <div className="space-y-3">
                  {selectedMilestone.break_it_challenges.map((ch, i) => (
                    <div key={i} className="rounded-xl border border-slate-800 bg-slate-950 p-4 font-serif text-lg text-slate-200 leading-relaxed">
                      <span className="font-mono font-bold text-amber-400 mr-2">#{i + 1}</span>
                      {ch}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT 6 COLS: FULL-WIDTH PYTHON 3.11 IDE + 3 TEST CASES & SANDBOX RUNNER */}
        <div className="lg:col-span-6 flex flex-col gap-5">
          {/* CODE EDITOR CARD */}
          <div className="rounded-2xl border border-slate-800/90 bg-[#0b101e] overflow-hidden shadow-xl flex flex-col">
            {/* File Tab Bar */}
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 bg-slate-950/90 px-4 py-2.5">
              <div className="flex items-center gap-1.5 overflow-x-auto">
                {project.artifacts.map((art) => {
                  const isSelectedArt = art.id === activeArtifact?.id;
                  return (
                    <button
                      key={art.id}
                      type="button"
                      onClick={() => {
                        setSelectedArtifactId(art.id);
                        setEditorContent(art.content);
                        setPracticeStarterMode(false);
                        if (art.milestone_id) {
                          onSelectMilestone(art.milestone_id);
                        }
                      }}
                      className={`inline-flex items-center gap-2 rounded-lg px-3 py-1.5 font-mono text-xs font-bold transition-all ${
                        isSelectedArt
                          ? 'bg-indigo-600/25 text-indigo-200 border border-indigo-500/40'
                          : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                      }`}
                    >
                      <FileCode className="h-3.5 w-3.5 text-amber-400" />
                      <span>{art.file_path.replace(/^src\//, '')}</span>
                    </button>
                  );
                })}
              </div>

              <div className="flex items-center gap-2">
                {activeArtifact && (
                  <button
                    type="button"
                    onClick={() => {
                      if (!practiceStarterMode) {
                        setEditorContent(buildStarterSkeleton(activeArtifact.content));
                        setPracticeStarterMode(true);
                      } else {
                        setEditorContent(activeArtifact.content);
                        setPracticeStarterMode(false);
                      }
                    }}
                    className={`rounded-lg border px-3 py-1 font-mono text-xs font-bold transition-colors ${
                      practiceStarterMode
                        ? 'border-amber-500/40 bg-amber-950/30 text-amber-300'
                        : 'border-slate-700 bg-slate-900 text-slate-300 hover:text-white'
                    }`}
                  >
                    {practiceStarterMode ? '✨ Show Reference Solution' : '✍️ Practice Mode (TODOs)'}
                  </button>
                )}
                <span className="rounded-lg border border-slate-800 bg-slate-900 px-2.5 py-1 font-mono text-xs text-slate-300">
                  Python 3.11
                </span>
              </div>
            </div>

            {/* Code Editor Body with Line Numbers */}
            <div className="relative flex bg-[#070b14] font-mono text-[14px] leading-[1.7] max-h-[380px] overflow-y-auto">
              <div
                aria-hidden="true"
                className="select-none border-r border-slate-800/70 bg-[#090d18] py-3.5 px-3.5 text-right font-mono text-xs text-slate-600 leading-[1.7]"
              >
                {editorLines.map((_, i) => (
                  <div key={i}>{i + 1}</div>
                ))}
              </div>

              <textarea
                value={editorContent}
                onChange={(e) => setEditorContent(e.target.value)}
                spellCheck={false}
                rows={Math.max(15, editorLines.length)}
                className="w-full resize-none bg-transparent p-3.5 font-mono text-[14px] leading-[1.7] text-emerald-100 focus:outline-none overflow-hidden"
              />
            </div>

            {/* Editor Status Footer */}
            <div className="flex items-center justify-between border-t border-slate-800/80 bg-slate-950/90 px-4 py-2 font-mono text-xs text-slate-400">
              <span>Day {dayNumber} · {activeArtifact?.file_path}</span>
              <span>Ln {editorLines.length}, Col 1 · Isolated Local Python Sandbox</span>
            </div>
          </div>

          {/* TEST CASES (3) & SANDBOX OUTPUT CARD */}
          <div className="rounded-2xl border border-slate-800/90 bg-[#0b101e] overflow-hidden shadow-xl flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/90 px-5 py-3">
              <div className="flex items-center gap-5">
                <button
                  type="button"
                  onClick={() => setActiveBottomRightTab('tests')}
                  className={`inline-flex items-center gap-2 font-sans text-xs font-extrabold uppercase tracking-wider transition-colors ${
                    activeBottomRightTab === 'tests' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <CheckCircle2 className="h-4 w-4 text-indigo-400" />
                  <span>Test Cases (3)</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveBottomRightTab('output')}
                  className={`inline-flex items-center gap-2 font-sans text-xs font-extrabold uppercase tracking-wider transition-colors ${
                    activeBottomRightTab === 'output' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Terminal className="h-4 w-4 text-emerald-400" />
                  <span>Sandbox Output</span>
                </button>
              </div>

              {activeArtifact && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={async () => {
                    setBusy(true);
                    await onSaveArtifact(activeArtifact.id, editorContent);
                    const res = await onVerifyArtifact(activeArtifact.id);
                    setVerificationResult(res);
                    setBusy(false);
                  }}
                  className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2 font-sans text-xs font-extrabold uppercase tracking-wider text-white shadow-md hover:bg-emerald-500 disabled:opacity-50 transition-all"
                >
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>{busy ? 'Executing...' : 'Run Code & Verify'}</span>
                </button>
              )}
            </div>

            <div className="p-5">
              {activeBottomRightTab === 'tests' ? (
                <div className="space-y-3">
                  {[
                    { num: 1, title: testDescriptions[0], passed: testCase1Passed },
                    { num: 2, title: testDescriptions[1], passed: testCase2Passed },
                    { num: 3, title: testDescriptions[2], passed: testCase3Passed },
                  ].map((tc) => (
                    <div
                      key={tc.num}
                      className="flex items-center justify-between gap-4 rounded-xl border border-slate-800/90 bg-slate-950/80 px-4 py-3.5"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span
                          className={`flex h-5 w-5 shrink-0 items-center justify-center rounded border ${
                            !hasRunTests
                              ? 'border-slate-700 bg-slate-900'
                              : tc.passed
                              ? 'border-emerald-500 bg-emerald-500/20 text-emerald-400'
                              : 'border-rose-500 bg-rose-500/20 text-rose-400'
                          }`}
                        >
                          {hasRunTests && tc.passed && <Check className="h-3.5 w-3.5" />}
                          {hasRunTests && !tc.passed && <X className="h-3.5 w-3.5" />}
                        </span>
                        <span className="font-mono text-xs font-bold text-indigo-300 shrink-0">
                          Test {tc.num}
                        </span>
                        <span className="truncate font-serif text-base text-slate-200">
                          {tc.title}
                        </span>
                      </div>

                      <span
                        className={`rounded-md px-2.5 py-1 font-mono text-xs font-bold shrink-0 ${
                          !hasRunTests
                            ? 'bg-slate-800 text-slate-400'
                            : tc.passed
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        }`}
                      >
                        {!hasRunTests ? 'Pending' : tc.passed ? 'Passed' : 'Failed'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-sm">
                  {verificationResult ? (
                    <pre className="whitespace-pre-wrap text-slate-200 leading-relaxed max-h-48 overflow-y-auto">
                      {verificationResult.output}
                    </pre>
                  ) : (
                    <div className="py-6 text-center text-slate-500">
                      Click &ldquo;Run Code &amp; Verify&rdquo; to execute `{activeArtifact?.file_path}` in the isolated Python 3.11 sandbox.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* BOTTOM ACTION BAR: [Reset] [Save] ... [Submit Lab] */}
          <div className="flex items-center justify-between rounded-2xl border border-slate-800/90 bg-[#0b101e] px-5 py-3.5 shadow-xl">
            <div className="flex items-center gap-3">
              {activeArtifact && (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      setEditorContent(activeArtifact.content);
                      setPracticeStarterMode(false);
                    }}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 font-sans text-xs font-semibold text-slate-200 hover:bg-slate-800 transition-colors"
                  >
                    <RotateCcw className="h-3.5 w-3.5 text-slate-400" />
                    <span>Reset</span>
                  </button>
                  <button
                    type="button"
                    disabled={busy}
                    onClick={async () => {
                      setBusy(true);
                      await onSaveArtifact(activeArtifact.id, editorContent);
                      setBusy(false);
                    }}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 font-sans text-xs font-semibold text-slate-200 hover:bg-slate-800 transition-colors"
                  >
                    <Save className="h-3.5 w-3.5 text-indigo-400" />
                    <span>Save</span>
                  </button>
                </>
              )}
            </div>

            <button
              type="button"
              disabled={busy}
              onClick={async () => {
                setBusy(true);
                if (activeArtifact) {
                  await onSaveArtifact(activeArtifact.id, editorContent);
                  const res = await onVerifyArtifact(activeArtifact.id);
                  setVerificationResult(res);
                }
                await onCompleteMilestone(selectedMilestone.id);
                setBusy(false);
              }}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-2.5 font-sans text-xs sm:text-sm font-extrabold text-white shadow-lg shadow-indigo-950/60 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 transition-all"
            >
              <Check className="h-4 w-4" />
              <span>
                {selectedMilestone.status === 'completed'
                  ? `Day ${dayNumber} Lab Completed`
                  : `Submit Lab (Complete Day ${dayNumber})`}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
