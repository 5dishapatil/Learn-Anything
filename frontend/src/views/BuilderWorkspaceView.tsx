import React, { useEffect, useState } from 'react';
import { ProjectFullData, ProjectMilestoneData, LearningDayData } from '../types/axiom';
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
  Music,
  Languages,
  PenTool,
  Play,
  RotateCcw,
  Save,
  Sparkles,
  Target,
  Terminal,
  X,
  Compass,
} from 'lucide-react';

export interface BuilderWorkspaceViewProps {
  project: ProjectFullData | null;
  selectedMilestoneId: number | null;
  journeyDays?: LearningDayData[];
  currentDayNumber?: number;
  totalDurationDays?: number;
  onSelectDay?: (dayNumber: number) => void;
  onSelectMilestone: (milestoneId: number) => void;
  onUnlockHint: (milestoneId: number, level: number) => Promise<void>;
  onCompleteMilestone: (milestoneId: number) => Promise<void>;
  onSaveArtifact: (artifactId: number, content: string) => Promise<void>;
  onVerifyArtifact: (artifactId: number) => Promise<any>;
  onVerifyDayLab?: (dayNumber: number, submission: string, isCode?: boolean) => Promise<any>;
  onCompleteDay?: (dayNumber: number) => Promise<void>;
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
  onSwitchToScholarDay?: (dayNumber: number) => void;
  onOpenExperimentLab: () => void;
  onGoToPlanner?: () => void;
  onSynthesizeDayLab?: (conceptId: number) => Promise<void>;
}

export const BuilderWorkspaceView: React.FC<BuilderWorkspaceViewProps> = ({
  project,
  selectedMilestoneId,
  journeyDays = [],
  currentDayNumber = 1,
  totalDurationDays,
  onSelectDay,
  onSelectMilestone,
  onUnlockHint,
  onCompleteMilestone,
  onSaveArtifact,
  onVerifyArtifact,
  onVerifyDayLab,
  onCompleteDay,
  onSwitchToScholar,
  onSwitchToScholarDay,
  onGoToPlanner,
  onSynthesizeDayLab,
}) => {
  const [selectedArtifactId, setSelectedArtifactId] = useState<number | null>(null);
  const [editorContent, setEditorContent] = useState<string>('');
  const [nonCodeSubmission, setNonCodeSubmission] = useState<string>('');
  const [verificationResult, setVerificationResult] = useState<any | null>(null);
  const [rubricScores, setRubricScores] = useState<Record<string, number>>({});
  const [busy, setBusy] = useState(false);

  // Left Problem & Guide Tabs: 'problem' | 'guide' | 'hints' | 'break_it'
  const [activeLeftTab, setActiveLeftTab] = useState<'problem' | 'guide' | 'hints' | 'break_it'>('problem');
  // Bottom-Right Tabs: 'tests' | 'output'
  const [activeBottomRightTab, setActiveBottomRightTab] = useState<'tests' | 'output'>('tests');
  const [checkedSteps, setCheckedSteps] = useState<Record<string, boolean>>({});
  const [practiceStarterMode, setPracticeStarterMode] = useState<boolean>(false);

  const hasDays = journeyDays && journeyDays.length > 0;
  const effectiveDayNumber = currentDayNumber || 1;
  const activeDay = hasDays
    ? journeyDays.find((d) => d.day_number === effectiveDayNumber) || journeyDays[0]
    : null;

  useEffect(() => {
    if (activeDay) {
      if (activeDay.builder_starter_code) {
        setEditorContent(activeDay.builder_starter_code);
      } else if (project && project.artifacts.length > 0) {
        const mId = selectedMilestoneId || project.milestones[0]?.id;
        const matchingArt =
          project.artifacts.find((a) => a.milestone_id === mId) || project.artifacts[0];
        setSelectedArtifactId(matchingArt.id);
        setEditorContent(matchingArt.content);
      }
      setVerificationResult(null);
      setPracticeStarterMode(false);
      setNonCodeSubmission('');
    } else if (project && project.artifacts.length > 0) {
      const mId = selectedMilestoneId || project.milestones[0]?.id;
      const matchingArt =
        project.artifacts.find((a) => a.milestone_id === mId) || project.artifacts[0];
      setSelectedArtifactId(matchingArt.id);
      setEditorContent(matchingArt.content);
      setVerificationResult(null);
      setPracticeStarterMode(false);
    }
  }, [project, selectedMilestoneId, activeDay?.day_number]);

  if (!project && !hasDays) {
    return (
      <div className="flex min-h-[65vh] flex-col items-center justify-center rounded-2xl border border-slate-800/90 bg-slate-900/50 p-12 text-center font-serif">
        <Code2 className="mb-4 h-14 w-14 text-indigo-400" />
        <h3 className="text-2xl font-extrabold text-white">
          Day-by-Day Hands-On Builder Workspace
        </h3>
        <p className="mt-2 max-w-lg text-lg text-slate-300 leading-relaxed">
          Generate a personalized learning roadmap in Explore &amp; Onboard to unlock your Day-wise Hands-On Practice Labs, automated verification suite, and isolated sandbox runner.
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
    project?.milestones.find((m) => m.sequence_order === effectiveDayNumber) ||
    project?.milestones.find((m) => m.id === selectedMilestoneId) ||
    project?.milestones[0] || {
      id: 1,
      sequence_order: effectiveDayNumber,
      title: activeDay?.builder_lab_title || activeDay?.title || `Day ${effectiveDayNumber} Practice Lab`,
      mission: activeDay?.builder_lab_mission || `Complete the hands-on engineering lab for Day ${effectiveDayNumber}.`,
      why_this_matters: activeDay?.why_this_day || 'Bridges foundational concepts into practical implementation.',
      prerequisites: [],
      architecture_design: '',
      architecture_diagram: '',
      pseudocode: activeDay?.builder_starter_code || '# Implement core logic step-by-step',
      interface_definitions: '',
      tradeoff_comparisons: '',
      step_by_step_guide: activeDay?.builder_content_markdown || 'Follow the step-by-step implementation guide.',
      code_explanation: '',
      basic_tests: (activeDay?.builder_test_cases || []).map((t) => t.name),
      edge_cases: ['Handle empty or zero inputs', 'Verify boundary limits'],
      hints: [
        { level: 1, title: 'Input Validation', content: 'Ensure all input arguments meet preconditions.' },
        { level: 2, title: 'Core Calculation', content: 'Apply the mathematical formulation directly.' },
      ],
      break_it_challenges: ['Pass invalid types or empty collections', 'Simulate rapid boundary transitions'],
      status: activeDay?.builder_completed ? 'completed' : 'in_progress',
      unlocked_hint_level: 1,
      concept_id: activeDay?.scholar_concept_id || null,
      failure_scenarios: [],
      debugging_steps: [],
      experimentation_prompts: [],
      deliverable_description: '',
      reflection_prompts: [],
      think_deeper_questions: [],
      tasks: [],
    } as unknown as ProjectMilestoneData;

  const activeArtifact =
    project?.artifacts.find((a) => a.id === selectedArtifactId) ||
    project?.artifacts.find((a) => a.milestone_id === selectedMilestone.id) ||
    project?.artifacts[0];

  const dayNumber = hasDays ? effectiveDayNumber : selectedMilestone.sequence_order;
  const totalDays = hasDays ? journeyDays.length : totalDurationDays || project?.milestones.length || 1;

  const activityType = activeDay?.builder_activity_type || 'code_lab';
  const isCodeActivity =
    activityType === 'code_lab' ||
    activityType === 'simulation' ||
    activityType.includes('code') ||
    activityType.includes('algorithm');

  const hintTiers = selectedMilestone.hints.map((h) => ({
    level: h.level,
    label: `Hint ${h.level}: ${h.title}`,
    content: h.content,
  }));

  // Parse discrete test cases from verification response or stdout
  const discreteTestResults: Array<{ title: string; passed: boolean; detail?: string }> =
    verificationResult?.test_case_results || [];

  const rawOutput: string = verificationResult?.stdout || verificationResult?.output || '';
  const hasDiscreteResults = discreteTestResults.length > 0;

  const testDescriptions =
    discreteTestResults.length > 0
      ? discreteTestResults.map((t) => t.title)
      : activeDay?.builder_test_cases && activeDay.builder_test_cases.length > 0
      ? activeDay.builder_test_cases.map((t) => t.name)
      : selectedMilestone.basic_tests && selectedMilestone.basic_tests.length >= 3
      ? selectedMilestone.basic_tests
      : [
          `Verify primary calculation & invariant for ${selectedMilestone.title}`,
          'Verify accurate scaling & multi-element behavior',
          'Verify boundary & edge precondition guard',
        ];

  const testCase1Passed = hasDiscreteResults
    ? discreteTestResults[0]?.passed
    : rawOutput.includes('[TEST CASE 1 PASS]') || verificationResult?.passed === true;
  const testCase2Passed = hasDiscreteResults
    ? discreteTestResults[1]?.passed
    : rawOutput.includes('[TEST CASE 2 PASS]') || verificationResult?.passed === true;
  const testCase3Passed = hasDiscreteResults
    ? discreteTestResults[2]?.passed
    : rawOutput.includes('[TEST CASE 3 PASS]') || verificationResult?.passed === true;
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
      `# TODO Step 2: Implement the core Day ${dayNumber} logic so all test cases pass\n\n` +
      mainHarness
    );
  };

  const editorLines = editorContent.split('\n');

  const getActivityIcon = (type: string) => {
    if (type.includes('music') || type.includes('piano')) return Music;
    if (type.includes('dialogue') || type.includes('language')) return Languages;
    if (type.includes('source') || type.includes('proof')) return PenTool;
    return Code2;
  };
  const ActivityIcon = getActivityIcon(activityType);

  const handleRunVerify = async () => {
    setBusy(true);
    try {
      if (onVerifyDayLab) {
        const submission = isCodeActivity ? editorContent : (nonCodeSubmission || editorContent);
        const res = await onVerifyDayLab(dayNumber, submission, isCodeActivity);
        setVerificationResult(res);
      } else if (activeArtifact) {
        await onSaveArtifact(activeArtifact.id, editorContent);
        const res = await onVerifyArtifact(activeArtifact.id);
        setVerificationResult(res);
      }
    } finally {
      setBusy(false);
    }
  };

  const handleCompleteLab = async () => {
    setBusy(true);
    try {
      if (onCompleteDay) {
        await onCompleteDay(dayNumber);
      } else {
        if (activeArtifact) {
          await onSaveArtifact(activeArtifact.id, editorContent);
        }
        await onCompleteMilestone(selectedMilestone.id);
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-5 font-sans">
      {/* =====================================================================
          TOP DAY-WISE SELECTOR BAR (Source of truth: LearningDay across duration)
         ===================================================================== */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-800/90 bg-[#0b101e] px-5 py-3.5 shadow-lg">
        {/* Horizontal Day Pills */}
        <div className="flex items-center gap-2 overflow-x-auto py-0.5 max-w-[70vw]">
          {hasDays
            ? journeyDays.map((d) => {
                const isSelected = d.day_number === dayNumber;
                const isDone = d.builder_completed || d.is_completed;
                return (
                  <button
                    key={d.day_number}
                    type="button"
                    onClick={() => {
                      if (onSelectDay) onSelectDay(d.day_number);
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
                      <span className="font-mono text-[11px]">D{d.day_number}</span>
                    )}
                    <span>
                      Day {d.day_number}: {d.title.replace(/^Day\s*\d+\s*:\s*/i, '').slice(0, 28)}
                    </span>
                  </button>
                );
              })
            : project?.milestones.map((m) => {
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
                      Day {m.sequence_order}: {m.title.replace(/^Day\s*\d+\s*Lab:\s*/i, '').slice(0, 28)}
                    </span>
                  </button>
                );
              })}
        </div>

        {/* Right Quick Actions: Synthesize Lab + Switch to Day Theory */}
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
              <span>{busy ? 'Synthesizing...' : `Deep-Synthesize Day ${dayNumber} Lab`}</span>
            </button>
          )}

          <button
            type="button"
            onClick={() => {
              if (onSwitchToScholarDay) {
                onSwitchToScholarDay(dayNumber);
              } else {
                onSwitchToScholar(selectedMilestone.concept_id);
              }
            }}
            className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-500/40 bg-indigo-950/40 px-3.5 py-2 font-sans text-xs font-bold text-indigo-200 hover:bg-indigo-900/60 hover:text-white transition-colors"
          >
            <BookOpen className="h-3.5 w-3.5" />
            <span>Study Day {dayNumber} Scholar Theory →</span>
          </button>
        </div>
      </div>

      {/* =====================================================================
          FULL-WIDTH 12-COLUMN WORKSPACE:
          LEFT 6 COLS = REAL PROBLEM, OUTCOMES, STEP-BY-STEP GUIDE
          RIGHT 6 COLS = DOMAIN PRACTICE / PYTHON 3.11 IDE + DISCRETE TEST CASES
         ===================================================================== */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 items-start">
        {/* LEFT 6 COLS: PROBLEM STATEMENT, OUTCOMES, STEP-BY-STEP GUIDE */}
        <div className="lg:col-span-6 rounded-2xl border border-slate-800/90 bg-[#0b101e] overflow-hidden shadow-xl flex flex-col">
          {/* Header Inside Problem Panel */}
          <div className="border-b border-slate-800 bg-slate-950/90 px-6 py-5 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="rounded-lg bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider text-emerald-300">
                  DAY {dayNumber} OF {totalDays} BUILDER LAB
                </span>
                <span className="inline-flex items-center gap-1.5 rounded-lg border border-purple-500/30 bg-purple-950/40 px-2.5 py-1 font-mono text-xs font-bold text-purple-300">
                  <ActivityIcon className="h-3.5 w-3.5" />
                  {activityType.toUpperCase()}
                </span>
              </div>
              <code className="rounded bg-slate-900 px-2.5 py-1 font-mono text-xs text-indigo-300 border border-slate-800">
                {activeArtifact?.file_path || `src/day_${dayNumber}_lab.py`}
              </code>
            </div>

            <h1 className="font-serif text-2xl sm:text-3xl font-extrabold text-white leading-snug">
              {activeDay?.builder_lab_title || activeDay?.title || selectedMilestone.title}
            </h1>

            <MarkdownRenderer
              content={activeDay?.builder_lab_mission || selectedMilestone.mission}
              className="font-serif text-lg text-slate-300 leading-relaxed"
            />

            {/* Pedagogical Rationale: Why This Day Occurs Here */}
            {(activeDay?.why_this_day || selectedMilestone.why_this_matters) && (
              <div className="rounded-xl border border-indigo-500/30 bg-indigo-950/20 p-3.5 text-xs font-serif leading-relaxed text-indigo-200">
                <div className="flex items-center gap-1.5 font-mono text-[11px] font-extrabold uppercase tracking-wider text-indigo-300 mb-1">
                  <Compass className="h-3.5 w-3.5" />
                  <span>Pedagogical Rationale · Why This Day Occurs Here</span>
                </div>
                <span>{activeDay?.why_this_day || selectedMilestone.why_this_matters}</span>
              </div>
            )}
          </div>

          {/* Tab Navigation Bar */}
          <div className="flex items-center border-b border-slate-800 bg-slate-950/60 px-4 pt-2 overflow-x-auto">
            {[
              { id: 'problem' as const, label: '1. Problem & Outcomes', icon: FileText },
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

          {/* Tab Content Body */}
          <div className="p-6 space-y-6 max-h-[640px] overflow-y-auto">
            {/* TAB 1: PROBLEM & CANONICAL SHARED OUTCOMES */}
            {activeLeftTab === 'problem' && (
              <div className="space-y-6">
                {/* Canonical Shared Outcomes coupling Scholar and Builder */}
                {activeDay?.learning_outcomes && activeDay.learning_outcomes.length > 0 && (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 font-serif text-lg font-bold text-white">
                      <Target className="h-5 w-5 text-indigo-400" />
                      <span>Canonical Learning Outcomes &amp; Practice Tasks</span>
                    </div>
                    <div className="space-y-2">
                      {activeDay.learning_outcomes.map((lo, idx) => (
                        <div
                          key={lo.outcome_id || idx}
                          className="rounded-xl border border-indigo-500/20 bg-slate-950/80 p-3.5 space-y-1.5"
                        >
                          <div className="flex items-center justify-between text-xs font-mono font-bold">
                            <span className="text-indigo-300">{lo.outcome_id}</span>
                            <span className="rounded bg-emerald-500/20 border border-emerald-500/30 px-2 py-0.5 text-[11px] text-emerald-300">
                              Mapped Lab: {lo.builder_task_id || `BT-D${dayNumber}-${idx + 1}`}
                            </span>
                          </div>
                          <div className="font-serif text-base font-bold text-white">{lo.title}</div>
                          <div className="font-serif text-sm text-slate-300">{lo.description}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Step-by-Step Guide or Mission Content */}
                <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 space-y-3">
                  <MarkdownRenderer
                    content={activeDay?.builder_content_markdown || selectedMilestone.step_by_step_guide}
                    className="font-serif text-[18.5px] leading-[1.85] text-slate-200"
                  />
                </div>

                {/* Test Cases / Verification Criteria */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2 font-serif text-xl font-bold text-white">
                    <Layers className="h-5 w-5 text-emerald-400" />
                    <span>Required Verification Test Cases ({testDescriptions.length})</span>
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
                    <span>Implementation Constraints &amp; Edge Cases</span>
                  </div>
                  <ul className="space-y-2 pl-5 list-disc font-serif text-lg text-slate-300">
                    {(selectedMilestone.edge_cases || []).map((ec, i) => (
                      <li key={i}>{ec}</li>
                    ))}
                    <li>Domain-authentic execution with transparent environment isolation.</li>
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
                      desc: `Reject invalid inputs cleanly before executing Day ${dayNumber} logic.`,
                    },
                    {
                      id: `cp-2-${selectedMilestone.id}`,
                      title: `Checkpoint 2: Implement Core Day ${dayNumber} Transformation`,
                      desc: `Implement the primary domain algorithm for ${selectedMilestone.title}.`,
                    },
                    {
                      id: `cp-3-${selectedMilestone.id}`,
                      title: 'Checkpoint 3: Pass All Automated Sandbox Test Cases',
                      desc: 'Click "Run & Verify" on the right to execute and verify test cases.',
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
                  Unlock hints progressively only when needed so you build genuine first-principles intuition:
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
                    Great practitioners discover where assumptions break. Mutate inputs or invariants on the right and observe the failure output:
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

        {/* RIGHT 6 COLS: DOMAIN PRACTICE / CODE IDE + DISCRETE TEST CASES */}
        <div className="lg:col-span-6 flex flex-col gap-5">
          {isCodeActivity ? (
            /* CODE EDITOR CARD FOR CODE/SIMULATION DOMAINS */
            <div className="rounded-2xl border border-slate-800/90 bg-[#0b101e] overflow-hidden shadow-xl flex flex-col">
              {/* File Tab Bar */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 bg-slate-950/90 px-4 py-2.5">
                <div className="flex items-center gap-1.5 overflow-x-auto">
                  <div className="inline-flex items-center gap-2 rounded-lg bg-indigo-600/25 text-indigo-200 border border-indigo-500/40 px-3 py-1.5 font-mono text-xs font-bold">
                    <FileCode className="h-3.5 w-3.5 text-amber-400" />
                    <span>{activeArtifact?.file_path.replace(/^src\//, '') || `day_${dayNumber}_lab.py`}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      if (!practiceStarterMode) {
                        setEditorContent(buildStarterSkeleton(editorContent));
                        setPracticeStarterMode(true);
                      } else {
                        if (activeDay?.builder_starter_code) {
                          setEditorContent(activeDay.builder_starter_code);
                        } else if (activeArtifact) {
                          setEditorContent(activeArtifact.content);
                        }
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
                <span>Day {dayNumber} · Isolated Local Subprocess Execution</span>
                <span>Ln {editorLines.length}, Col 1 · Python 3.11</span>
              </div>
            </div>
          ) : (
            /* NON-CODE DOMAIN PRACTICE SUBMISSION CARD */
            <div className="rounded-2xl border border-slate-800/90 bg-[#0b101e] overflow-hidden shadow-xl flex flex-col p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <ActivityIcon className="h-5 w-5 text-indigo-400" />
                  <span className="font-serif text-lg font-bold text-white">
                    {activityType.replace(/_/g, ' ').toUpperCase()} WORKSPACE
                  </span>
                </div>
                <span className="rounded-lg bg-indigo-950/60 border border-indigo-500/30 px-3 py-1 font-mono text-xs text-indigo-300">
                  Interactive Practice
                </span>
              </div>

              <p className="font-serif text-base text-slate-300">
                Compose your response, translation, musical transcription, or derivation below. When ready, click &ldquo;Evaluate Submission&rdquo; to test against the structured rubric.
              </p>

              <textarea
                value={nonCodeSubmission}
                onChange={(e) => setNonCodeSubmission(e.target.value)}
                rows={12}
                placeholder="Write your practice response, analysis, or proof here..."
                className="w-full rounded-xl border border-slate-700 bg-slate-950 p-4 font-serif text-base text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
              />

              {/* Rubric Evaluation Card for Non-Code Activities */}
              {(() => {
                const rubricList: Array<{ criterion: string; weight?: string | number; description?: string }> =
                  Array.isArray(activeDay?.builder_rubric)
                    ? activeDay.builder_rubric.map((c: string) => ({ criterion: c, description: c }))
                    : (activeDay?.builder_rubric as any)?.criteria || [];
                if (rubricList.length === 0) return null;
                return (
                  <div className="space-y-3 pt-2">
                    <div className="font-mono text-xs font-bold uppercase text-emerald-400">
                      STRUCTURED EVALUATION RUBRIC
                    </div>
                    <div className="space-y-2">
                      {rubricList.map((cr, idx) => (
                        <div
                          key={idx}
                          className="rounded-xl border border-slate-800 bg-slate-950/80 p-3.5 space-y-1.5"
                        >
                          <div className="flex items-center justify-between font-serif text-sm font-bold text-white">
                            <span>{cr.criterion}</span>
                            <span className="font-mono text-xs text-indigo-400">Weight: {cr.weight || '1.0'}</span>
                          </div>
                          <p className="font-serif text-xs text-slate-300">{cr.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })()}
            </div>
          )}

          {/* TEST CASES & SANDBOX OUTPUT CARD */}
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
                  <span>Test Cases ({testDescriptions.length})</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveBottomRightTab('output')}
                  className={`inline-flex items-center gap-2 font-sans text-xs font-extrabold uppercase tracking-wider transition-colors ${
                    activeBottomRightTab === 'output' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Terminal className="h-4 w-4 text-emerald-400" />
                  <span>Sandbox Output &amp; Diagnostics</span>
                </button>
              </div>

              {isCodeActivity && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={handleRunVerify}
                  className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2 font-sans text-xs font-extrabold uppercase tracking-wider text-white shadow-md hover:bg-emerald-500 disabled:opacity-50 transition-all"
                >
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>{busy ? 'Executing...' : 'Run & Verify'}</span>
                </button>
              )}
            </div>

            <div className="p-5">
              {activeBottomRightTab === 'tests' ? (
                <div className="space-y-3">
                  {/* Honest Sandbox Engine Label */}
                  {verificationResult?.execution_engine && (
                    <div className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 font-mono text-[11px] text-slate-400 flex items-center justify-between">
                      <span>Execution Engine:</span>
                      <strong className="text-emerald-400">{verificationResult.execution_engine}</strong>
                    </div>
                  )}

                  {testDescriptions.map((desc, idx) => {
                    const tcPassed = hasDiscreteResults
                      ? discreteTestResults[idx]?.passed
                      : idx === 0
                      ? testCase1Passed
                      : idx === 1
                      ? testCase2Passed
                      : testCase3Passed;

                    return (
                      <div
                        key={idx}
                        className="flex items-center justify-between gap-4 rounded-xl border border-slate-800/90 bg-slate-950/80 px-4 py-3.5"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <span
                            className={`flex h-5 w-5 shrink-0 items-center justify-center rounded border ${
                              !hasRunTests
                                ? 'border-slate-700 bg-slate-900'
                                : tcPassed
                                ? 'border-emerald-500 bg-emerald-500/20 text-emerald-400'
                                : 'border-rose-500 bg-rose-500/20 text-rose-400'
                            }`}
                          >
                            {hasRunTests && tcPassed && <Check className="h-3.5 w-3.5" />}
                            {hasRunTests && !tcPassed && <X className="h-3.5 w-3.5" />}
                          </span>
                          <span className="font-mono text-xs font-bold text-indigo-300 shrink-0">
                            Test {idx + 1}
                          </span>
                          <span className="truncate font-serif text-base text-slate-200">
                            {desc}
                          </span>
                        </div>

                        <span
                          className={`rounded-md px-2.5 py-1 font-mono text-xs font-bold shrink-0 ${
                            !hasRunTests
                              ? 'bg-slate-800 text-slate-400'
                              : tcPassed
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                              : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          }`}
                        >
                          {!hasRunTests ? 'Pending' : tcPassed ? 'Passed' : 'Failed'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-sm">
                  {verificationResult ? (
                    <div className="space-y-3">
                      {verificationResult.stdout && (
                        <div>
                          <div className="text-xs text-slate-400 uppercase font-mono mb-1">STDOUT:</div>
                          <pre className="whitespace-pre-wrap text-emerald-300 leading-relaxed max-h-48 overflow-y-auto">
                            {verificationResult.stdout}
                          </pre>
                        </div>
                      )}
                      {verificationResult.stderr && (
                        <div>
                          <div className="text-xs text-rose-400 uppercase font-mono mb-1">STDERR:</div>
                          <pre className="whitespace-pre-wrap text-rose-300 leading-relaxed max-h-48 overflow-y-auto">
                            {verificationResult.stderr}
                          </pre>
                        </div>
                      )}
                      {!verificationResult.stdout && !verificationResult.stderr && (
                        <pre className="whitespace-pre-wrap text-slate-200 leading-relaxed max-h-48 overflow-y-auto">
                          {verificationResult.output || 'Execution complete.'}
                        </pre>
                      )}
                    </div>
                  ) : (
                    <div className="py-6 text-center text-slate-500">
                      Click &ldquo;Run &amp; Verify&rdquo; to execute the test suite in the isolated sandbox.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* BOTTOM ACTION BAR */}
          <div className="flex items-center justify-between rounded-2xl border border-slate-800/90 bg-[#0b101e] px-5 py-3.5 shadow-xl">
            <div className="flex items-center gap-3">
              {isCodeActivity && activeArtifact && (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      if (activeDay?.builder_starter_code) {
                        setEditorContent(activeDay.builder_starter_code);
                      } else {
                        setEditorContent(activeArtifact.content);
                      }
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
              onClick={handleCompleteLab}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-2.5 font-sans text-xs sm:text-sm font-extrabold text-white shadow-lg shadow-indigo-950/60 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 transition-all"
            >
              <Check className="h-4 w-4" />
              <span>
                {activeDay?.builder_completed || selectedMilestone.status === 'completed'
                  ? `Day ${dayNumber} Lab Completed`
                  : `Submit Lab & Complete Day ${dayNumber}`}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
