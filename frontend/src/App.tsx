import React, { useEffect, useState } from 'react';
import { axiomApi } from './api/client';
import {
  ConceptItem,
  ConceptWorkspaceData,
  ExperimentData,
  LearningJourneyData,
  LearningDayData,
  GenerationJobData,
  ProjectFullData,
  ResourceDiscoveryResponse,
  ThinkDeeperQuestionItem,
} from './types/axiom';
import { ConceptGraphView } from './components/ConceptGraphView';
import { MermaidDiagram } from './components/MermaidDiagram';
import { ScholarWorkspaceView } from './views/ScholarWorkspaceView';
import { BuilderWorkspaceView } from './views/BuilderWorkspaceView';
import { SettingsAndAutomationView } from './views/SettingsAndAutomationView';
import { MarkdownRenderer } from './components/MarkdownRenderer';
import {
  AlertCircle,
  ArrowRight,
  Award,
  BookOpen,
  Calendar,
  CheckCircle2,
  CheckSquare,
  Clock,
  Code2,
  Compass,
  ExternalLink,
  FileDown,
  Flame,
  FlaskConical,
  FolderGit2,
  Globe,
  Home,
  Layers,
  Library,
  Map,
  Menu,
  Moon,
  Play,
  Plus,
  Search,
  Settings,
  Sparkles,
  Sun,
  Target,
  Trash2,
  Trophy,
  X,
  Zap,
} from 'lucide-react';

export type NavSection =
  | 'home'
  | 'explore'
  | 'journeys'
  | 'tasks'
  | 'scholar'
  | 'builder'
  | 'library'
  | 'projects'
  | 'experiments'
  | 'knowledge'
  | 'think_deeper'
  | 'settings';

interface NavGroup {
  title: string;
  items: Array<{
    id: NavSection;
    label: string;
    icon: any;
    badge?: string;
  }>;
}

interface ToastMessage {
  id: number;
  title: string;
  description?: string;
  type: 'success' | 'info' | 'warning';
}

export function App() {
  const [activeNav, setActiveNav] = useState<NavSection>('home');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // Toast Notification Stack
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const pushToast = (title: string, description?: string, type: 'success' | 'info' | 'warning' = 'success') => {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    setToasts((prev) => [...prev, { id, title, description, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5500);
  };

  // Core Application State
  const [dashboard, setDashboard] = useState<any | null>(null);
  const [journeys, setJourneys] = useState<LearningJourneyData[]>([]);
  const [activeJourneyId, setActiveJourneyId] = useState<number | null>(null);
  const [conceptWorkspace, setConceptWorkspace] = useState<ConceptWorkspaceData | null>(null);
  const [projects, setProjects] = useState<ProjectFullData[]>([]);
  const [activeProject, setActiveProject] = useState<ProjectFullData | null>(null);
  const [selectedMilestoneId, setSelectedMilestoneId] = useState<number | null>(null);
  const [experiments, setExperiments] = useState<ExperimentData[]>([]);
  const [resourceDiscovery, setResourceDiscovery] = useState<ResourceDiscoveryResponse | null>(null);
  const [knowledgeWorkspace, setKnowledgeWorkspace] = useState<any | null>(null);
  const [thinkDeeperList, setThinkDeeperList] = useState<ThinkDeeperQuestionItem[]>([]);
  const [aiStatus, setAiStatus] = useState<any | null>(null);
  const [liveAiStatus, setLiveAiStatus] = useState<{
    active_provider: string;
    active_model: string;
    is_local: boolean;
    online: boolean;
    model_installed: boolean;
    is_connected: boolean;
    latency_ms: number;
    status_message: string;
  } | null>(null);
  const [memories, setMemories] = useState<any[]>([]);
  const [obsidianConfig, setObsidianConfig] = useState<any | null>(null);
  const [automationStatus, setAutomationStatus] = useState<any | null>(null);
  const [backups, setBackups] = useState<any[]>([]);
  const [obsidianExportModal, setObsidianExportModal] = useState<any | null>(null);
  const [statusBanner, setStatusBanner] = useState<string>('');

  // Curriculum Planner / Onboarding Form State
  const [intentInput, setIntentInput] = useState('');
  const [expLevel, setExpLevel] = useState('beginner');
  const [dailyMins, setDailyMins] = useState(60);
  const [durationDays, setDurationDays] = useState(30);
  const [targetDeadline, setTargetDeadline] = useState('');
  const [roadMode, setRoadMode] = useState<'hybrid' | 'scholar' | 'builder'>('hybrid');
  const [learningFormat, setLearningFormat] = useState('combined');
  const [existingKnowledge, setExistingKnowledge] = useState('');
  const [finalGoal, setFinalGoal] = useState('');
  const [currentDayNumber, setCurrentDayNumber] = useState<number>(1);
  const [specificResearchFocus, setSpecificResearchFocus] = useState<string>('');
  const [intakeTools, setIntakeTools] = useState<string>('');
  const [intakePastProjects, setIntakePastProjects] = useState<string>('');
  const [intakeGaps, setIntakeGaps] = useState<string>('');
  const [intakeUnresolvedProblems, setIntakeUnresolvedProblems] = useState<string>('');
  const [intakePapers, setIntakePapers] = useState<string>('');
  const [activeJob, setActiveJob] = useState<GenerationJobData | null>(null);
  const [creatingJourney, setCreatingJourney] = useState(false);
  const [generationStageText, setGenerationStageText] = useState('');
  const [showAdvancedOnboarding, setShowAdvancedOnboarding] = useState(false);

  // Live Web Search Grounding Preview State
  const [liveWebPreview, setLiveWebPreview] = useState<any | null>(null);
  const [searchingWeb, setSearchingWeb] = useState(false);

  // Jane Street Socratic Tutor State
  const [socraticInput, setSocraticInput] = useState('');
  const [socraticState, setSocraticState] = useState<any | null>(null);
  const [socraticBusy, setSocraticBusy] = useState(false);

  // Blueprint Editing State
  const [editingBlueprintTitle, setEditingBlueprintTitle] = useState('');
  const [editingBlueprintHours, setEditingBlueprintHours] = useState(20);

  // Resource Search Form State
  const [resourceQuery, setResourceQuery] = useState('');
  const [freeOnlyFilter, setFreeOnlyFilter] = useState(true);

  // New Experiment Form State
  const [expTitle, setExpTitle] = useState('');
  const [expHypothesis, setExpHypothesis] = useState('');
  const [expVariables, setExpVariables] = useState('learning_rate: [1e-3, 1e-1]');
  const [expProcedure, setExpProcedure] = useState('');
  const [expExpected, setExpExpected] = useState('');
  const [expActual, setExpActual] = useState('');
  const [expConclusion, setExpConclusion] = useState('');

  // New Note Form State
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [noteUnderstanding, setNoteUnderstanding] = useState('');
  const [noteTags, setNoteTags] = useState('first-principles, synthesis');

  const activeJourney =
    journeys.find((j) => j.id === activeJourneyId) || (journeys.length > 0 ? journeys[0] : null);

  // Guarantee Builder Road ALWAYS finds the linked project if any exists
  const effectiveProject =
    activeProject ||
    (activeJourney ? projects.find((p) => p.journey_id === activeJourney.id) : null) ||
    (projects.length > 0 ? projects[0] : null);

  // Theme sync
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'light') {
      root.classList.remove('dark');
      root.classList.add('light');
    } else {
      root.classList.remove('light');
      root.classList.add('dark');
    }
  }, [theme]);

  // Keyboard shortcut Ctrl+K / Cmd+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen((p) => !p);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  async function loadInitialState() {
    try {
      const [dash, jList, pList, expList, kw, tdList] = await Promise.all([
        axiomApi.getDashboard(),
        axiomApi.listJourneys(),
        axiomApi.listProjects(),
        axiomApi.listExperiments(),
        axiomApi.getKnowledgeWorkspace(),
        axiomApi.listThinkDeeper(),
      ]);
      setDashboard(dash);
      setJourneys(jList);
      setProjects(pList);
      setExperiments(expList);
      setKnowledgeWorkspace(kw);
      setThinkDeeperList(tdList);

      if (jList.length > 0) {
        const firstJ = jList[0];
        setActiveJourneyId(firstJ.id);
        if (firstJ.blueprint) {
          setEditingBlueprintTitle(firstJ.blueprint.title);
          setEditingBlueprintHours(firstJ.blueprint.estimated_hours);
        }
        const cId = firstJ.current_concept_id || firstJ.concepts[0]?.id;
        if (cId) {
          const cw = await axiomApi.getConceptWorkspace(cId);
          setConceptWorkspace(cw);
        }
        const linkedP = pList.find((p) => p.journey_id === firstJ.id) || pList[0];
        if (linkedP) {
          setActiveProject(linkedP);
          setSelectedMilestoneId(linkedP.milestones[0]?.id || null);
        }
      } else {
        setActiveJourneyId(null);
        setConceptWorkspace(null);
        setActiveProject(null);
        setSelectedMilestoneId(null);
      }

      const initialTopic = jList.length > 0 ? jList[0].title : 'First-Principles Engineering';
      const resDisc = await axiomApi.discoverResources(initialTopic, true, false);
      setResourceDiscovery(resDisc);
    } catch {
      // Graceful fallback during unit test mount when backend server is not running
    }
  }

  async function loadSettingsAndHardware() {
    try {
      const [ai, mems, obs, auto, bks] = await Promise.all([
        axiomApi.getAiAndHardwareStatus(),
        axiomApi.listMemories(),
        axiomApi.getObsidianConfig(),
        axiomApi.getAutomationStatus(),
        axiomApi.listBackups(),
      ]);
      setAiStatus(ai);
      setMemories(mems);
      setObsidianConfig(obs);
      setAutomationStatus(auto);
      setBackups(bks);
    } catch {
      // Ignore offline errors in isolated test environment
    }
  }

  async function refreshLiveAiStatus() {
    try {
      const live = await axiomApi.getLiveAiStatus();
      setLiveAiStatus(live);
    } catch {
      setLiveAiStatus({
        active_provider: 'ollama',
        active_model: 'qwen3.5:9b',
        is_local: true,
        online: false,
        model_installed: false,
        is_connected: false,
        latency_ms: 0,
        status_message: 'Disconnected (Backend or Ollama offline)',
      });
    }
  }

  useEffect(() => {
    loadInitialState();
    loadSettingsAndHardware();
    refreshLiveAiStatus();
    const pollId = setInterval(() => {
      refreshLiveAiStatus();
    }, 10000);
    return () => clearInterval(pollId);
  }, []);

  const handleSelectJourney = async (
    journey: LearningJourneyData,
    overrideProjects?: ProjectFullData[]
  ) => {
    setActiveJourneyId(journey.id);
    if (journey.blueprint) {
      setEditingBlueprintTitle(journey.blueprint.title);
      setEditingBlueprintHours(journey.blueprint.estimated_hours);
    }
    const cId = journey.current_concept_id || journey.concepts[0]?.id;
    if (cId) {
      const cw = await axiomApi.getConceptWorkspace(cId);
      setConceptWorkspace(cw);
    }
    const pool = overrideProjects || projects;
    const linkedProj = pool.find((p) => p.journey_id === journey.id) || pool[0] || null;
    if (linkedProj) {
      setActiveProject(linkedProj);
      setSelectedMilestoneId(linkedProj.milestones[0]?.id || null);
    }
  };

  const handleCreateJourney = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!intentInput.trim()) {
      pushToast('Please enter a learning topic', 'Describe what you want to learn or build first.', 'warning');
      return;
    }
    setCreatingJourney(true);
    setGenerationStageText('Stage 1/3: Searching live web sources (Wikipedia, DuckDuckGo, arXiv, GitHub)...');
    const stageTimer1 = setTimeout(() => {
      setGenerationStageText('Stage 2/3: Synthesizing curriculum & CodeChef Builder Labs with qwen3.5:9b...');
    }, 1400);
    const stageTimer2 = setTimeout(() => {
      setGenerationStageText('Stage 3/3: Initializing Daily Tasks, Socratic Mastery Map & Sandbox...');
    }, 3200);

    try {
      const intakeProfile = {
        experience_level: expLevel,
        prior_topics_understood: existingKnowledge || undefined,
        tools_and_languages_used: intakeTools || undefined,
        previous_projects_completed: intakePastProjects || undefined,
        specific_gaps_to_bridge: intakeGaps || undefined,
        target_next_level_goal: finalGoal || undefined,
        unresolved_problems: intakeUnresolvedProblems || undefined,
        papers_or_frameworks_to_replicate: intakePapers || undefined,
      };

      const created = await axiomApi.createJourney({
        user_intent: intentInput,
        experience_level: expLevel,
        daily_minutes: dailyMins,
        duration_days: durationDays,
        target_deadline: targetDeadline || undefined,
        road_mode: roadMode,
        preferred_format: learningFormat,
        existing_knowledge: existingKnowledge || undefined,
        final_project_goal: finalGoal || undefined,
        specific_research_focus: specificResearchFocus || undefined,
        intake_profile: intakeProfile,
      });
      setCurrentDayNumber(1);
      const [jList, pList, dash, tdList] = await Promise.all([
        axiomApi.listJourneys(),
        axiomApi.listProjects(),
        axiomApi.getDashboard(),
        axiomApi.listThinkDeeper(),
      ]);
      setJourneys(jList);
      setProjects(pList);
      setDashboard(dash);
      setThinkDeeperList(tdList);
      await handleSelectJourney(created, pList);
      setIntentInput('');
      setStatusBanner(`Roadmap Generated: "${created.title}" (${created.duration_days} Days · qwen3.5:9b)`);
      pushToast(
        'Roadmap & Builder Track Generated!',
        `Redirected to "${created.title}" (${created.concepts.length} modules & ${created.projects?.[0]?.milestone_count || 4} CodeChef labs ready).`,
        'success'
      );
      setActiveNav('journeys');
    } catch (err: any) {
      pushToast('Generation Error', err?.message || 'Could not generate roadmap.', 'warning');
    } finally {
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      setCreatingJourney(false);
      setGenerationStageText('');
    }
  };

  const handleDeleteJourney = async (journeyId: number, title: string) => {
    try {
      await axiomApi.deleteJourney(journeyId);
      const [jList, pList, dash] = await Promise.all([
        axiomApi.listJourneys(),
        axiomApi.listProjects(),
        axiomApi.getDashboard(),
      ]);
      setJourneys(jList);
      setProjects(pList);
      setDashboard(dash);
      if (jList.length > 0) {
        await handleSelectJourney(jList[0], pList);
      } else {
        setActiveJourneyId(null);
        setConceptWorkspace(null);
        setActiveProject(null);
        setSelectedMilestoneId(null);
      }
      pushToast('Journey Deleted', `Removed "${title}" and its associated tasks.`, 'info');
      setStatusBanner(`Deleted journey "${title}".`);
    } catch (err: any) {
      pushToast('Delete Failed', err?.message || 'Could not delete journey.', 'warning');
    }
  };

  const handleSwitchRoad = async (
    targetRoad: 'scholar' | 'builder',
    conceptId?: number | null,
    milestoneId?: number | null
  ) => {
    if (!activeJourney) {
      setActiveNav(targetRoad);
      return;
    }
    await axiomApi.switchRoad(activeJourney.id, {
      target_road: targetRoad,
      concept_id: conceptId,
      milestone_id: milestoneId,
    });
    if (conceptId) {
      const cw = await axiomApi.getConceptWorkspace(conceptId);
      setConceptWorkspace(cw);
    }
    const linkedProj =
      projects.find((p) => p.journey_id === activeJourney.id) || activeProject || projects[0] || null;
    if (linkedProj) {
      setActiveProject(linkedProj);
      if (milestoneId) {
        setSelectedMilestoneId(milestoneId);
      } else if (!selectedMilestoneId) {
        setSelectedMilestoneId(linkedProj.milestones[0]?.id || null);
      }
    }
    const jList = await axiomApi.listJourneys();
    setJourneys(jList);
    setActiveNav(targetRoad);
    pushToast(
      `Switched to ${targetRoad === 'builder' ? 'CodeChef Builder Road' : 'Scholar Road'}`,
      'Full concept and milestone context preserved.',
      'info'
    );
  };

  const handleExportObsidian = async (
    exportType: 'concept' | 'project' | 'experiment' | 'think_deeper' | 'note',
    entityId: number
  ) => {
    const res = await axiomApi.exportToObsidian({
      export_type: exportType,
      entity_id: entityId,
      allow_overwrite: false,
    });
    setObsidianExportModal(res);
    pushToast('Exported to Obsidian Markdown', res.relative_vault_path, 'success');
  };

  const handleDeadlineChange = (dateStr: string) => {
    setTargetDeadline(dateStr);
    if (dateStr) {
      const target = new Date(dateStr);
      const now = new Date();
      const diffDays = Math.max(1, Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)));
      setDurationDays(diffDays);
    }
  };

  // Structured Navigation System (Obsidian / Startup Workspace Hierarchy)
  const pendingTasksCount = (activeJourney?.tasks || []).filter((t) => t.status !== 'completed').length;

  const navGroups: NavGroup[] = [
    {
      title: 'Workspace',
      items: [
        { id: 'home', label: 'Dashboard', icon: Home },
        { id: 'explore', label: 'Explore & Onboard', icon: Compass, badge: 'Planner' },
        { id: 'journeys', label: 'My Journeys & Blueprint', icon: Map },
        {
          id: 'tasks',
          label: 'Daily Tasks',
          icon: CheckSquare,
          badge: pendingTasksCount > 0 ? String(pendingTasksCount) : undefined,
        },
      ],
    },
    {
      title: 'Learning Roads',
      items: [
        { id: 'scholar', label: 'Scholar Road', icon: BookOpen, badge: 'Theory' },
        { id: 'builder', label: 'Builder Road', icon: Code2, badge: 'CodeChef' },
      ],
    },
    {
      title: 'Lab & Research',
      items: [
        { id: 'think_deeper', label: 'Think Deeper', icon: Sparkles, badge: 'Socratic' },
        { id: 'library', label: 'Research Library', icon: Library },
        { id: 'projects', label: 'Projects', icon: FolderGit2 },
        { id: 'experiments', label: 'Experiment Lab', icon: FlaskConical },
      ],
    },
    {
      title: 'Knowledge & System',
      items: [
        { id: 'knowledge', label: 'My Knowledge', icon: Layers },
        { id: 'settings', label: 'Settings & AI', icon: Settings },
      ],
    },
  ];

  const allNavItems = navGroups.flatMap((g) => g.items);

  // Day 1 Tasks for Dashboard Timeline
  const day1Tasks = (activeJourney?.tasks || []).filter((t) => t.day_number === 1);
  const allTasks = activeJourney?.tasks || [];
  const completedTasks = allTasks.filter((t) => t.status === 'completed');
  const pendingTasks = allTasks.filter((t) => t.status !== 'completed');

  return (
    <div
      className={`min-h-screen flex ${
        theme === 'light' ? 'bg-slate-50 text-slate-900' : 'bg-[#090d16] text-slate-100'
      }`}
    >
      {/* FLOATING TOAST NOTIFICATION STACK (TOP-RIGHT) */}
      <div className="fixed top-5 right-5 z-50 flex flex-col gap-2.5 max-w-md w-full pointer-events-none px-4 sm:px-0">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-start justify-between gap-3 rounded-2xl border p-4 shadow-2xl backdrop-blur-md transition-all ${
              t.type === 'success'
                ? 'border-emerald-500/40 bg-slate-900/95 text-emerald-100 shadow-emerald-950/50'
                : t.type === 'warning'
                ? 'border-amber-500/40 bg-slate-900/95 text-amber-100 shadow-amber-950/50'
                : 'border-indigo-500/40 bg-slate-900/95 text-indigo-100 shadow-indigo-950/50'
            }`}
          >
            <div className="flex items-start gap-3">
              {t.type === 'success' ? (
                <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
              ) : t.type === 'warning' ? (
                <AlertCircle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
              ) : (
                <Sparkles className="h-5 w-5 text-indigo-400 shrink-0 mt-0.5" />
              )}
              <div>
                <div className="text-sm font-bold text-white">{t.title}</div>
                {t.description && (
                  <div className="text-xs text-slate-300 mt-0.5 leading-relaxed">{t.description}</div>
                )}
              </div>
            </div>
            <button
              type="button"
              onClick={() => setToasts((prev) => prev.filter((item) => item.id !== t.id))}
              className="text-slate-400 hover:text-white p-1"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>

      {/* Collapsible Obsidian-Style Sidebar */}
      <aside
        className={`flex flex-col justify-between border-r border-slate-800/80 bg-[#070a12] transition-all duration-200 shrink-0 ${
          sidebarCollapsed ? 'w-18' : 'w-64'
        }`}
      >
        <div className="overflow-y-auto">
          {/* Brand Header */}
          <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-4">
            {!sidebarCollapsed && (
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-emerald-500 font-extrabold text-white shadow-md shadow-indigo-950/60">
                  A
                </div>
                <div>
                  <div className="text-[15px] font-extrabold tracking-tight text-white">AXIOM OS</div>
                  <div className="text-[11px] font-mono uppercase tracking-wider text-indigo-400">
                    Research · Learn · Build
                  </div>
                </div>
              </div>
            )}
            <button
              type="button"
              aria-label="Toggle Sidebar"
              onClick={() => setSidebarCollapsed((p) => !p)}
              className="rounded-lg p-2 text-slate-400 hover:bg-slate-900 hover:text-slate-200"
            >
              <Menu className="h-4 w-4" />
            </button>
          </div>

          {/* Categorized Navigation Groups */}
          <nav className="p-3 space-y-4">
            {navGroups.map((group, gIdx) => (
              <div key={gIdx} className="space-y-1">
                {!sidebarCollapsed && (
                  <div className="px-3 pt-2 pb-1 font-mono text-[11px] font-bold uppercase tracking-wider text-slate-500">
                    {group.title}
                  </div>
                )}
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeNav === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setActiveNav(item.id)}
                      className={`flex w-full items-center justify-between rounded-xl px-3.5 py-2.5 text-[14.5px] font-medium transition-all ${
                        isActive
                          ? 'bg-indigo-600/95 text-white font-semibold shadow-md shadow-indigo-950/60'
                          : 'text-slate-300 hover:bg-slate-900/90 hover:text-white'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="h-4 w-4 shrink-0" />
                        {!sidebarCollapsed && <span>{item.label}</span>}
                      </div>
                      {!sidebarCollapsed && item.badge && (
                        <span
                          className={`rounded-md px-2 py-0.5 font-mono text-[11px] font-bold ${
                            isActive ? 'bg-indigo-500 text-white' : 'bg-slate-800/90 text-slate-300'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            ))}
          </nav>
        </div>

        {/* Bottom User Level & XP Indicator */}
        {!sidebarCollapsed && (
          <div className="m-3 rounded-2xl border border-slate-800/80 bg-slate-900/50 p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[11px] font-bold uppercase tracking-wider text-indigo-300">
                LV {dashboard?.user?.current_level ?? 1} · EXPLORER
              </span>
              <span className="font-mono text-xs font-bold text-emerald-400">
                {dashboard?.user?.total_xp ?? 0} XP
              </span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full"
                style={{ width: `${Math.min(100, ((dashboard?.user?.total_xp ?? 0) % 250) / 2.5)}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span>{dashboard?.user?.total_xp ?? 0} / 250 XP</span>
              <span>Streak: {dashboard?.user?.active_days_count ?? 0}d</span>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content Viewport */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Enterprise Navigation Header: ONLY Search Bar + Real Live Model Status */}
        <header className="sticky top-0 z-20 flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 bg-[#090d16]/90 px-6 sm:px-8 py-3.5 backdrop-blur-md">
          {/* Search Bar Only on Left/Center */}
          <div className="flex-1 max-w-xl">
            <button
              type="button"
              onClick={() => setCommandPaletteOpen(true)}
              className="w-full flex items-center justify-between gap-3 rounded-xl border border-slate-700/80 bg-slate-900/90 px-4 py-2.5 text-sm font-medium text-slate-300 hover:border-indigo-500/60 hover:text-white transition-colors"
            >
              <div className="flex items-center gap-2.5 truncate">
                <Search className="h-4 w-4 text-indigo-400 shrink-0" />
                <span className="truncate">Search & Command</span>
                <span className="hidden md:inline text-xs text-slate-500">
                  — Search concepts, lessons, videos, code labs, notes...
                </span>
              </div>
              <kbd className="hidden sm:inline rounded bg-slate-800 px-2 py-0.5 font-mono text-[11px] text-slate-400 shrink-0">
                Ctrl+K
              </kbd>
            </button>
          </div>

          {/* Real Live Model Connection Status Only on Right */}
          <div className="flex items-center gap-3">
            {(() => {
              const isConnected = Boolean(
                liveAiStatus ? liveAiStatus.is_connected : dashboard?.ai_status?.is_connected
              );
              const activeModel =
                liveAiStatus?.active_model || dashboard?.ai_status?.active_model || 'qwen3.5:9b';
              const latencyMs = liveAiStatus?.latency_ms ?? dashboard?.ai_status?.latency_ms ?? 0;
              return (
                <button
                  type="button"
                  onClick={() => {
                    refreshLiveAiStatus();
                    setActiveNav('settings');
                  }}
                  title={
                    liveAiStatus?.status_message ||
                    (isConnected
                      ? `Live connection verified to ${activeModel}`
                      : `Model ${activeModel} is currently offline or unreachable`)
                  }
                  className={`inline-flex items-center gap-2.5 rounded-full border px-4 py-1.5 text-xs font-mono font-semibold transition-all ${
                    isConnected
                      ? 'border-emerald-500/40 bg-emerald-950/30 text-emerald-300 hover:bg-emerald-950/50'
                      : 'border-rose-500/50 bg-rose-950/40 text-rose-300 hover:bg-rose-950/60'
                  }`}
                >
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'
                    }`}
                  />
                  <span>
                    Ollama · <strong>{activeModel}</strong> ·{' '}
                    {isConnected
                      ? `Connected${latencyMs > 0 ? ` (${latencyMs}ms)` : ''}`
                      : 'Disconnected'}
                  </span>
                </button>
              );
            })()}
          </div>
        </header>

        {/* Status Notification Banner */}
        {statusBanner && (
          <div className="flex items-center justify-between bg-indigo-950/60 border-b border-indigo-500/30 px-6 sm:px-8 py-2 text-xs text-indigo-200">
            <span className="font-medium flex items-center gap-2">
              <Sparkles className="h-3.5 w-3.5 text-indigo-400" /> {statusBanner}
            </span>
            <button
              type="button"
              onClick={() => setStatusBanner('')}
              className="text-slate-400 hover:text-white p-1"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )}

        {/* Primary Viewport */}
        <main className="flex-1 p-5 sm:p-7 max-w-[1600px] w-full mx-auto space-y-7">
          {/* =================================================================
              SCREEN 1: ENTERPRISE HOME DASHBOARD (Obsidian Aesthetic + Structured Cards)
             ================================================================= */}
          {activeNav === 'home' && (
            <div className="space-y-7">
              {/* Top Greeting Header */}
              <div className="flex flex-wrap items-end justify-between gap-4 border-b border-slate-800/80 pb-5">
                <div>
                  <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
                    Good Afternoon, {dashboard?.user?.name || 'Principal Researcher'}
                  </h1>
                  <p className="mt-1 font-mono text-xs uppercase tracking-widest text-slate-400">
                    {activeJourney
                      ? `ACTIVE FOCUS: ${activeJourney.title.toUpperCase()} · ${activeJourney.duration_days}-DAY ROADMAP`
                      : 'OPEN EXPLORE & ONBOARD TO ARCHITECT YOUR LEARNING & ENGINEERING JOURNEY'}
                  </p>
                </div>
                <div className="flex items-center gap-2.5">
                  {activeJourney && (
                    <button
                      type="button"
                      onClick={() => setActiveNav('tasks')}
                      className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-xs sm:text-sm font-semibold text-slate-200 hover:bg-slate-800 transition-colors"
                    >
                      <CheckSquare className="h-4 w-4 text-emerald-400" /> View All Tasks ({pendingTasks.length})
                    </button>
                  )}
                </div>
              </div>

              {/* TOP 3-COLUMN ENTERPRISE GRID: [DAY 01 TIMELINE] | [STATS + SOCRATIC GAPS] | [XP & LEVEL] */}
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
                {/* LEFT (5 COLS): DAY 01 VERTICAL TIMELINE CARD */}
                <div className="lg:col-span-5 rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 flex flex-col justify-between space-y-6 shadow-lg">
                  <div className="space-y-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-2xl font-extrabold tracking-tight text-white">DAY 01</div>
                        <div className="flex items-center gap-1.5 font-mono text-xs text-slate-400 mt-0.5">
                          <Clock className="h-3.5 w-3.5 text-indigo-400" />
                          <span>
                            {activeJourney
                              ? `${activeJourney.daily_minutes} MINS DAILY COMMITMENT`
                              : 'AWAITING CURRICULUM PLAN'}
                          </span>
                        </div>
                      </div>
                      <span className="h-2.5 w-2.5 rounded-sm bg-indigo-500" />
                    </div>

                    {/* Vertical Timeline */}
                    <div className="relative pl-6 space-y-4 before:absolute before:left-[7px] before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-800">
                      {/* Slot 1: 09:00 AM Learning */}
                      <div className="relative">
                        <span className="absolute -left-[21px] top-1.5 h-3 w-3 rounded-sm bg-indigo-500 ring-4 ring-slate-900" />
                        <div
                          onClick={() => setActiveNav(activeJourney ? 'scholar' : 'explore')}
                          className="cursor-pointer rounded-xl border border-slate-800 bg-slate-950/80 p-4 hover:border-indigo-500/50 transition-all"
                        >
                          <div className="flex items-center justify-between text-xs font-mono">
                            <span className="rounded bg-indigo-500/15 border border-indigo-500/30 px-2 py-0.5 font-bold text-indigo-300">
                              📖 LEARNING · 09:00 AM
                            </span>
                            <span className="text-slate-400">
                              {day1Tasks[0]?.estimated_minutes || 25}m
                            </span>
                          </div>
                          <div className="mt-2 text-sm font-bold text-white">
                            {activeJourney?.concepts[0]?.title || 'First-Principles Concept Foundations'}
                          </div>
                        </div>
                      </div>

                      {/* Slot 2: 11:00 AM Coding Practice */}
                      <div className="relative">
                        <span className="absolute -left-[21px] top-1.5 h-3 w-3 rounded-sm bg-emerald-500 ring-4 ring-slate-900" />
                        <div
                          onClick={() => handleSwitchRoad('builder')}
                          className="cursor-pointer rounded-xl border border-slate-800 bg-slate-950/80 p-4 hover:border-emerald-500/50 transition-all"
                        >
                          <div className="flex items-center justify-between text-xs font-mono">
                            <span className="rounded bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5 font-bold text-emerald-300">
                              &lt;/&gt; CODING LAB · 11:00 AM
                            </span>
                            <span className="text-slate-400">
                              {day1Tasks[1]?.estimated_minutes || 25}m
                            </span>
                          </div>
                          <div className="mt-2 text-sm font-bold text-white">
                            {effectiveProject?.milestones[0]?.title || 'Step-by-Step CodeChef Practice Lab'}
                          </div>
                        </div>
                      </div>

                      {/* Slot 3: 14:00 PM Socratic & Feynman Assessment */}
                      <div className="relative">
                        <span className="absolute -left-[21px] top-1.5 h-3 w-3 rounded-sm bg-purple-500 ring-4 ring-slate-900" />
                        <div
                          onClick={() => setActiveNav('think_deeper')}
                          className="cursor-pointer rounded-xl border border-slate-800 bg-slate-950/80 p-4 hover:border-purple-500/50 transition-all"
                        >
                          <div className="flex items-center justify-between text-xs font-mono">
                            <span className="rounded bg-purple-500/15 border border-purple-500/30 px-2 py-0.5 font-bold text-purple-300">
                              ⚡ ASSESSMENT · 02:00 PM
                            </span>
                            <span className="text-slate-400">
                              {day1Tasks[2]?.estimated_minutes || 15}m
                            </span>
                          </div>
                          <div className="mt-2 text-sm font-bold text-white">
                            Socratic Mastery Probe & Feynman Reconstruction
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      if (activeJourney) {
                        setActiveNav('scholar');
                        pushToast('Started Day 1 Session', `Opening "${activeJourney.concepts[0]?.title}"`, 'info');
                      } else {
                        setActiveNav('explore');
                      }
                    }}
                    className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-emerald-600 py-3.5 px-6 text-sm font-extrabold uppercase tracking-wider text-white hover:from-indigo-500 hover:to-emerald-500 shadow-lg shadow-indigo-950/50 transition-all"
                  >
                    <Play className="h-4 w-4 fill-current" />
                    {activeJourney ? 'START DAY 1' : 'CREATE YOUR FIRST PLAN'}
                  </button>
                </div>

                {/* CENTER + RIGHT (7 COLS): STATS, XP & LEVEL, AND JANE STREET SOCRATIC MASTERY */}
                <div className="lg:col-span-7 flex flex-col justify-between gap-6">
                  {/* Top Row: STATS (7 cols) + XP & LEVEL (5 cols) */}
                  <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
                    {/* STATS CARD */}
                    <div className="md:col-span-6 rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 space-y-4 shadow-lg">
                      <div className="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                        STATS
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 space-y-2">
                          <div className="flex items-center gap-1.5 font-mono text-[11px] font-bold uppercase text-amber-400">
                            <Zap className="h-3.5 w-3.5" /> STREAK
                          </div>
                          <div className="text-3xl font-extrabold text-white">
                            {dashboard?.user?.active_days_count ?? 0}{' '}
                            <span className="text-xs font-normal text-slate-400">Days</span>
                          </div>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 space-y-2">
                          <div className="flex items-center gap-1.5 font-mono text-[11px] font-bold uppercase text-emerald-400">
                            <Target className="h-3.5 w-3.5" /> PROGRESS
                          </div>
                          <div className="text-3xl font-extrabold text-white">
                            {activeJourney ? `${Math.round(activeJourney.progress_percent)}%` : '0%'}
                          </div>
                          <div className="font-mono text-[11px] text-slate-400">
                            {completedTasks.length}/{allTasks.length || 0} Tasks Done
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* XP & LEVEL CARD */}
                    <div className="md:col-span-6 rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 space-y-4 shadow-lg">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                          XP & LEVEL
                        </span>
                        <span className="rounded-md border border-indigo-500/30 bg-indigo-500/10 px-2 py-0.5 font-mono text-[11px] font-bold text-indigo-300">
                          LV {dashboard?.user?.current_level ?? 1} — EXPLORER
                        </span>
                      </div>

                      <div className="flex items-baseline justify-between">
                        <div>
                          <span className="text-3xl font-extrabold text-white">
                            {dashboard?.user?.total_xp ?? 0}
                          </span>
                          <span className="ml-1 font-mono text-xs text-slate-400">XP</span>
                        </div>
                        <div className="text-right font-mono text-xs text-emerald-400">
                          DAILY GOAL: {Math.min(200, dashboard?.user?.total_xp ?? 0)}/200 XP
                        </div>
                      </div>

                      <div className="space-y-1.5">
                        <div className="flex justify-between font-mono text-[11px] text-slate-400">
                          <span>LEVEL PROGRESS</span>
                          <span>{(dashboard?.user?.total_xp ?? 0) % 250} / 250 XP</span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full"
                            style={{ width: `${Math.min(100, ((dashboard?.user?.total_xp ?? 0) % 250) / 2.5)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Bottom Row: JANE STREET SOCRATIC SKILL MAP & GAP FIXER */}
                  <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 space-y-4 shadow-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Trophy className="h-4 w-4 text-indigo-400" />
                        <span className="font-mono text-xs font-bold uppercase tracking-wider text-slate-200">
                          JANE STREET SOCRATIC MASTERY & GAP DIAGNOSTICS (LEVELS 0–5)
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setActiveNav('think_deeper')}
                        className="font-mono text-xs font-bold text-indigo-400 hover:text-indigo-300"
                      >
                        OPEN SOCRATIC TUTOR &gt;
                      </button>
                    </div>

                    {activeJourney && activeJourney.concepts.length > 0 ? (
                      <div className="space-y-2">
                        {activeJourney.concepts.slice(0, 4).map((c, idx) => {
                          const lvl = Math.min(5, Math.max(0, Math.round((c.mastery_score || 0) * 5)));
                          return (
                            <div
                              key={c.id}
                              className="flex items-center justify-between gap-4 rounded-xl border border-slate-800/80 bg-slate-950/60 px-4 py-2.5 text-xs"
                            >
                              <span className="font-semibold text-slate-200 truncate">
                                {idx + 1}. {c.title}
                              </span>
                              <div className="flex items-center gap-3 shrink-0">
                                <div className="w-24 h-2 rounded-full bg-slate-800 overflow-hidden">
                                  <div
                                    className="h-full bg-indigo-500 rounded-full"
                                    style={{ width: `${(lvl / 5) * 100}%` }}
                                  />
                                </div>
                                <span className="font-mono font-bold text-indigo-300">{lvl}/5</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="py-6 text-center space-y-2">
                        <div className="font-mono text-xs font-bold uppercase text-slate-400">
                          NO ACTIVE SUBSKILL DIAGNOSTICS YET
                        </div>
                        <p className="text-xs text-slate-500">
                          Generate a curriculum roadmap to initialize your 0–5 Socratic mastery map and gap diagnostics.
                        </p>
                      </div>
                    )}

                    <button
                      type="button"
                      onClick={() => setActiveNav('think_deeper')}
                      className="w-full rounded-xl border border-indigo-500/40 bg-indigo-950/30 py-2.5 text-xs font-mono font-bold uppercase tracking-wider text-indigo-300 hover:bg-indigo-900/50 hover:text-white transition-colors"
                    >
                      ⚡ FIX MY GAPS WITH JANE STREET SOCRATIC TUTOR (QWEN3.5:9B)
                    </button>
                  </div>
                </div>
              </div>

              {/* YOUR ACTIVE JOURNEY BANNER BAR */}
              {activeJourney && (
                <div
                  onClick={() => setActiveNav('journeys')}
                  className="cursor-pointer rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 hover:border-indigo-500/50 transition-all shadow-md"
                >
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-400">
                        <Target className="h-6 w-6" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                            YOUR JOURNEY
                          </span>
                          <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[11px] uppercase text-indigo-300 font-bold">
                            {activeJourney.experience_level}
                          </span>
                        </div>
                        <h3 className="text-lg font-extrabold text-white mt-0.5">
                          {activeJourney.title}
                        </h3>
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <div className="text-xl font-extrabold text-white">
                          1<span className="text-sm font-normal text-slate-400">/{activeJourney.duration_days}</span>
                        </div>
                        <div className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
                          DAYS
                        </div>
                      </div>
                      <ArrowRight className="h-5 w-5 text-slate-400" />
                    </div>
                  </div>
                  <div className="mt-4 h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full"
                      style={{ width: `${Math.max(4, activeJourney.progress_percent)}%` }}
                    />
                  </div>
                </div>
              )}

              {/* BADGES & ACHIEVEMENTS GRID */}
              <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 space-y-4 shadow-md">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Award className="h-4 w-4 text-emerald-400" />
                    <span className="font-mono text-xs font-bold uppercase tracking-wider text-slate-300">
                      BADGES & MILESTONE ACHIEVEMENTS
                    </span>
                  </div>
                  <span className="font-mono text-xs text-indigo-400 font-bold">
                    {journeys.length > 0 ? '2 / 8 UNLOCKED' : '0 / 8 UNLOCKED'}
                  </span>
                </div>

                <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
                  {[
                    {
                      title: 'First Step',
                      desc: 'Architected your first learning blueprint',
                      unlocked: journeys.length > 0,
                    },
                    {
                      title: 'CodeChef Builder',
                      desc: 'Provisioned step-by-step hands-on coding labs',
                      unlocked: projects.length > 0,
                    },
                    {
                      title: 'Feynman Synthesizer',
                      desc: 'Completed a 6-stage Feynman explanation',
                      unlocked: (dashboard?.user?.total_xp ?? 0) >= 60,
                    },
                    {
                      title: 'Socratic Contender',
                      desc: 'Reached Level 4/5 in Socratic Tutor',
                      unlocked: (dashboard?.user?.total_xp ?? 0) >= 150,
                    },
                    {
                      title: 'Break-It Engineer',
                      desc: 'Verified edge-case failure invariants',
                      unlocked: false,
                    },
                    {
                      title: 'Week Warrior',
                      desc: '7-day first-principles learning streak',
                      unlocked: (dashboard?.user?.active_days_count ?? 0) >= 7,
                    },
                    {
                      title: 'Experiment Scientist',
                      desc: 'Logged formal hypothesis & ablation run',
                      unlocked: experiments.length > 0,
                    },
                    {
                      title: 'Obsidian Architect',
                      desc: 'Exported connected notes to Obsidian vault',
                      unlocked: false,
                    },
                  ].map((b, i) => (
                    <div
                      key={i}
                      className={`rounded-xl border p-4 transition-all ${
                        b.unlocked
                          ? 'border-indigo-500/40 bg-indigo-950/25 text-white'
                          : 'border-slate-800/70 bg-slate-950/50 text-slate-500'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-slate-100">{b.title}</span>
                        {b.unlocked && (
                          <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 font-mono text-[10px] font-bold text-emerald-300">
                            EARNED
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-xs text-slate-400 leading-relaxed">{b.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* =================================================================
              SCREEN 2: CURRICULUM PLANNER (2-Column Layout with My Plans, Delete & Deadline)
             ================================================================= */}
          {activeNav === 'explore' && (
            <div className="space-y-6">
              {/* Top Header */}
              <div className="flex flex-wrap items-end justify-between gap-4 border-b border-slate-800 pb-5">
                <div>
                  <span className="font-mono text-xs font-bold uppercase tracking-wider text-indigo-400">
                    CURRICULUM PLANNER · POWERED BY QWEN3.5:9B + FREE LIVE WEB SEARCH
                  </span>
                  <h2 className="mt-1 text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                    What Do You Want to Understand From First Principles or Build Today?
                  </h2>
                  <p className="mt-1 text-sm sm:text-base text-slate-300">
                    Design your personalized learning & CodeChef-style engineering journey with local AI and live web grounding.
                  </p>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-900/90 px-4 py-2.5 font-mono text-xs text-slate-300">
                  ACTIVE PLANS: <strong className="text-emerald-400 text-sm">{journeys.length}</strong>
                </div>
              </div>

              {/* 2-Column Split: Left 8 Cols = Step 1/2/3 Form, Right 4 Cols = My Plans (with Delete & Continue) */}
              <div className="grid grid-cols-1 gap-8 lg:grid-cols-12 items-start">
                {/* LEFT COLUMN: NUMBERED STEPS 1, 2, 3 */}
                <form onSubmit={handleCreateJourney} className="lg:col-span-8 space-y-7">
                  {/* STEP 1: WHAT DO YOU WANT TO LEARN? */}
                  <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 sm:p-7 space-y-4 shadow-lg">
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 font-mono text-sm font-extrabold text-white">
                          1
                        </span>
                        <label className="text-lg font-extrabold text-white">
                          What do you want to learn or build?
                        </label>
                      </div>
                      <button
                        type="button"
                        disabled={!intentInput.trim() || searchingWeb}
                        onClick={async () => {
                          if (!intentInput.trim()) return;
                          setSearchingWeb(true);
                          try {
                            const res = await axiomApi.liveWebSearch(intentInput);
                            setLiveWebPreview(res);
                            pushToast('Live Web Search Complete', `Found ${res.count} up-to-date web & academic sources.`, 'info');
                          } finally {
                            setSearchingWeb(false);
                          }
                        }}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-500/40 bg-emerald-950/30 px-3 py-1.5 font-mono text-xs font-bold text-emerald-300 hover:bg-emerald-900/50 disabled:opacity-40 transition-colors"
                      >
                        <Globe className="h-3.5 w-3.5" />
                        {searchingWeb ? 'Searching Web...' : 'Preview Live Web Grounding'}
                      </button>
                    </div>

                    <input
                      type="text"
                      value={intentInput}
                      onChange={(e) => setIntentInput(e.target.value)}
                      placeholder="e.g. Brain Computer Interface, Full-Stack Rust Kernel, Transformers from Scratch, Distributed Systems..."
                      className="w-full rounded-xl border border-slate-700 bg-slate-950 px-5 py-4 text-base text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    />

                    {/* Quick Topic Chips */}
                    <div className="flex flex-wrap gap-2 pt-1">
                      {[
                        'Brain-Computer Interfaces & Neural Signal Decoding',
                        'Transformers & Building a Tiny GPT from Scratch',
                        'Quantum Computing & Qubit Circuit Simulator',
                        'Distributed Key-Value Storage Engine with Raft',
                      ].map((chip, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setIntentInput(chip)}
                          className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs font-medium text-slate-300 hover:border-indigo-500 hover:text-white transition-colors"
                        >
                          + {chip}
                        </button>
                      ))}
                    </div>

                    {/* Live Web Search Preview Box */}
                    {liveWebPreview && (
                      <div className="rounded-xl border border-emerald-500/30 bg-slate-950/90 p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs font-bold uppercase text-emerald-400">
                            ✓ Live Web & Research Grounding Sources ({liveWebPreview.count} Verified)
                          </span>
                          <button
                            type="button"
                            onClick={() => setLiveWebPreview(null)}
                            className="text-xs text-slate-400 hover:text-white"
                          >
                            Close
                          </button>
                        </div>
                        <div className="space-y-1.5 max-h-40 overflow-y-auto">
                          {(liveWebPreview.results || []).map((r: any, i: number) => (
                            <div key={i} className="text-xs text-slate-300 flex items-center justify-between gap-2 border-b border-slate-800/60 pb-1">
                              <span className="truncate">
                                <strong className="text-indigo-300 uppercase font-mono">[{r.provider_name}]</strong>{' '}
                                {r.title}
                              </span>
                              <a
                                href={r.url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-emerald-400 hover:underline shrink-0 font-mono"
                              >
                                Link ↗
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* STEP 2: EXPERIENCE LEVEL & LEARNING ROAD */}
                  <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 sm:p-7 space-y-5 shadow-lg">
                    <div className="flex items-center gap-3">
                      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 font-mono text-sm font-extrabold text-white">
                        2
                      </span>
                      <span className="text-lg font-extrabold text-white">
                        What&apos;s your experience level & learning mode?
                      </span>
                    </div>

                    <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-3">
                      {[
                        { id: 'beginner', label: 'BEGINNER', sub: 'NEW TO THIS TOPIC' },
                        { id: 'intermediate', label: 'INTERMEDIATE', sub: 'SOME PRIOR KNOWLEDGE' },
                        { id: 'advanced', label: 'ADVANCED', sub: 'DEEP RESEARCH & SYSTEMS' },
                      ].map((lvl) => {
                        const active = expLevel === lvl.id;
                        return (
                          <button
                            key={lvl.id}
                            type="button"
                            onClick={() => setExpLevel(lvl.id)}
                            className={`rounded-xl border p-4 text-left transition-all ${
                              active
                                ? 'border-indigo-500 bg-indigo-950/35 ring-1 ring-indigo-500/40'
                                : 'border-slate-800 bg-slate-950/70 hover:border-slate-700'
                            }`}
                          >
                            <div className="h-3 w-3 rounded-sm mb-3 border border-indigo-400 bg-indigo-500/20 flex items-center justify-center">
                              {active && <div className="h-2 w-2 rounded-xs bg-indigo-400" />}
                            </div>
                            <div className="font-mono text-sm font-extrabold text-white">{lvl.label}</div>
                            <div className="font-mono text-[11px] text-slate-400 mt-0.5">{lvl.sub}</div>
                          </button>
                        );
                      })}
                    </div>

                    {/* Dynamic Expertise-Level Intake Questionnaire */}
                    {expLevel === 'beginner' && (
                      <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4 space-y-3">
                        <div className="flex items-center gap-2 font-mono text-xs font-bold uppercase text-emerald-400">
                          <Sparkles className="h-4 w-4" /> Zero-Assumed-Knowledge Onboarding
                        </div>
                        <p className="font-serif text-sm text-slate-200">
                          Axiom starts from absolute physical and mathematical primitives. Day 1 builds foundational intuition before introducing formal notations or advanced equations.
                        </p>
                        <div className="space-y-1.5">
                          <label className="font-mono text-xs text-slate-300">What is your ultimate dream project or goal with this topic?</label>
                          <input
                            type="text"
                            value={finalGoal}
                            onChange={(e) => setFinalGoal(e.target.value)}
                            placeholder="e.g. Build an end-to-end EEG motor-imagery classifier and understand neural dynamics"
                            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
                          />
                        </div>
                      </div>
                    )}

                    {expLevel === 'intermediate' && (
                      <div className="rounded-xl border border-indigo-500/30 bg-indigo-950/20 p-4 space-y-3">
                        <div className="flex items-center gap-2 font-mono text-xs font-bold uppercase text-indigo-300">
                          <Target className="h-4 w-4" /> Prior Knowledge &amp; Gap Bridging
                        </div>
                        <p className="font-serif text-sm text-slate-200">
                          Tell us what you already know so Axiom skips repetitive basics and focuses on bridging your foundational gaps to high-level mastery.
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          <div className="space-y-1">
                            <label className="font-mono text-xs text-slate-300">Prior Concepts / Theory Mastered</label>
                            <input
                              type="text"
                              value={existingKnowledge}
                              onChange={(e) => setExistingKnowledge(e.target.value)}
                              placeholder="e.g. Linear algebra, gradient descent, basic PyTorch"
                              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs sm:text-sm text-white focus:border-indigo-500 focus:outline-none"
                            />
                          </div>
                          <div className="space-y-1">
                            <label className="font-mono text-xs text-slate-300">Tools / Languages / Libraries Used</label>
                            <input
                              type="text"
                              value={intakeTools}
                              onChange={(e) => setIntakeTools(e.target.value)}
                              placeholder="e.g. Python, NumPy, SciPy, MNE-Python"
                              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs sm:text-sm text-white focus:border-indigo-500 focus:outline-none"
                            />
                          </div>
                          <div className="space-y-1">
                            <label className="font-mono text-xs text-slate-300">Previous Projects or Systems Built</label>
                            <input
                              type="text"
                              value={intakePastProjects}
                              onChange={(e) => setIntakePastProjects(e.target.value)}
                              placeholder="e.g. Simple CNN digit classifier, bandpass filter script"
                              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs sm:text-sm text-white focus:border-indigo-500 focus:outline-none"
                            />
                          </div>
                          <div className="space-y-1">
                            <label className="font-mono text-xs text-slate-300">Specific Gaps You Want to Bridge</label>
                            <input
                              type="text"
                              value={intakeGaps}
                              onChange={(e) => setIntakeGaps(e.target.value)}
                              placeholder="e.g. Mathematical derivation of spatial filtering, real-time buffer sync"
                              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs sm:text-sm text-white focus:border-indigo-500 focus:outline-none"
                            />
                          </div>
                        </div>
                      </div>
                    )}

                    {expLevel === 'advanced' && (
                      <div className="rounded-xl border border-purple-500/30 bg-purple-950/20 p-4 space-y-3">
                        <div className="flex items-center gap-2 font-mono text-xs font-bold uppercase text-purple-300">
                          <Flame className="h-4 w-4" /> Frontier Research &amp; Advanced Specialization
                        </div>
                        <p className="font-serif text-sm text-slate-200">
                          Elementary primitives will be omitted. Axiom structures the roadmap around state-of-the-art papers, novel hypotheses, open problems, and production-grade architectures.
                        </p>
                        <div className="space-y-3">
                          <div className="space-y-1">
                            <label className="font-mono text-xs text-slate-300">Specific Research Focus / Subfield Specialization</label>
                            <input
                              type="text"
                              value={specificResearchFocus}
                              onChange={(e) => setSpecificResearchFocus(e.target.value)}
                              placeholder="e.g. Biologically plausible credit assignment, predictive coding, STDP"
                              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
                            />
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div className="space-y-1">
                              <label className="font-mono text-xs text-slate-300">Unresolved Problems / Engineering Bottlenecks</label>
                              <input
                                type="text"
                                value={intakeUnresolvedProblems}
                                onChange={(e) => setIntakeUnresolvedProblems(e.target.value)}
                                placeholder="e.g. Catastrophic forgetting in continuous neuromorphic streams"
                                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs sm:text-sm text-white focus:border-indigo-500 focus:outline-none"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="font-mono text-xs text-slate-300">Benchmark Papers / Systems to Replicate</label>
                              <input
                                type="text"
                                value={intakePapers}
                                onChange={(e) => setIntakePapers(e.target.value)}
                                placeholder="e.g. Rao & Ballard 1999, Lillicrap 2016 Feedback Alignment"
                                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs sm:text-sm text-white focus:border-indigo-500 focus:outline-none"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Road Mode Selector */}
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 pt-1">
                      {[
                        { id: 'hybrid', label: 'Hybrid (Scholar + CodeChef Builder)' },
                        { id: 'scholar', label: 'Scholar Road (Deep Theory)' },
                        { id: 'builder', label: 'Builder Road (Step-by-Step Code)' },
                      ].map((rm) => (
                        <button
                          key={rm.id}
                          type="button"
                          onClick={() => setRoadMode(rm.id as any)}
                          className={`rounded-xl border px-3.5 py-2.5 font-mono text-xs font-bold transition-all ${
                            roadMode === rm.id
                              ? 'border-emerald-500/60 bg-emerald-950/30 text-emerald-300'
                              : 'border-slate-800 bg-slate-950/50 text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {rm.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* STEP 3: TIME COMMITMENT & TARGET DEADLINE / DAYS */}
                  <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 sm:p-7 space-y-5 shadow-lg">
                    <div className="flex items-center gap-3">
                      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 font-mono text-sm font-extrabold text-white">
                        3
                      </span>
                      <span className="text-lg font-extrabold text-white">
                        Time Commitment & Target Deadline
                      </span>
                    </div>

                    <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
                      {/* Daily Commitment Stepper */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between font-mono text-xs text-slate-400">
                          <span>DAILY TIME</span>
                          <span className="text-indigo-300">{(dailyMins / 60).toFixed(1)}h / day</span>
                        </div>
                        <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5">
                          <button
                            type="button"
                            onClick={() => setDailyMins((m) => Math.max(15, m - 15))}
                            className="rounded-lg bg-slate-900 px-3 py-1 font-mono text-base font-bold text-slate-300 hover:bg-slate-800 hover:text-white"
                          >
                            -
                          </button>
                          <span className="font-mono text-base font-extrabold text-white">
                            {dailyMins} mins
                          </span>
                          <button
                            type="button"
                            onClick={() => setDailyMins((m) => Math.min(360, m + 15))}
                            className="rounded-lg bg-slate-900 px-3 py-1 font-mono text-base font-bold text-slate-300 hover:bg-slate-800 hover:text-white"
                          >
                            +
                          </button>
                        </div>
                      </div>

                      {/* Target Days Quick Selector + Input */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between font-mono text-xs text-slate-400">
                          <span>TARGET DAYS</span>
                          <span className="text-emerald-300">{durationDays} Days</span>
                        </div>
                        <div className="grid grid-cols-3 sm:grid-cols-6 gap-1.5">
                          {[
                            { label: '7d', days: 7 },
                            { label: '14d', days: 14 },
                            { label: '1m', days: 30 },
                            { label: '3m', days: 90 },
                            { label: '6m', days: 180 },
                            { label: '1y', days: 365 },
                          ].map((p) => (
                            <button
                              key={p.days}
                              type="button"
                              onClick={() => setDurationDays(p.days)}
                              className={`rounded-xl border py-2.5 font-mono text-xs font-bold transition-all ${
                                durationDays === p.days
                                  ? 'border-indigo-500 bg-indigo-600 text-white'
                                  : 'border-slate-800 bg-slate-950 text-slate-400 hover:text-white'
                              }`}
                            >
                              {p.label}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Target Deadline Date Picker */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between font-mono text-xs text-slate-400">
                          <span>TARGET DEADLINE</span>
                          <span className="text-amber-300">Optional Date</span>
                        </div>
                        <input
                          type="date"
                          aria-label="Target Deadline Date"
                          value={targetDeadline}
                          onChange={(e) => handleDeadlineChange(e.target.value)}
                          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 font-mono text-xs sm:text-sm text-white focus:border-indigo-500 focus:outline-none"
                        />
                      </div>
                    </div>

                    {/* Custom Days Input & Advanced Options */}
                    <div className="flex flex-wrap items-center justify-between gap-4 border-t border-slate-800/80 pt-4">
                      <div className="flex items-center gap-2 text-xs text-slate-300">
                        <span>Custom Target Days:</span>
                        <input
                          type="number"
                          min={1}
                          max={365}
                          value={durationDays}
                          onChange={(e) => setDurationDays(Math.max(1, Number(e.target.value)))}
                          className="w-20 rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 font-mono text-xs text-white"
                        />
                      </div>
                      <button
                        type="button"
                        onClick={() => setShowAdvancedOnboarding((p) => !p)}
                        className="text-xs font-mono font-semibold text-indigo-400 hover:text-indigo-300"
                      >
                        {showAdvancedOnboarding ? 'Hide Advanced Goals' : '+ Prior Knowledge & Project Goal'}
                      </button>
                    </div>

                    {showAdvancedOnboarding && (
                      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 pt-2">
                        <input
                          type="text"
                          value={existingKnowledge}
                          onChange={(e) => setExistingKnowledge(e.target.value)}
                          placeholder="Prior knowledge (e.g. Python, basic calculus)..."
                          className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-white"
                        />
                        <input
                          type="text"
                          value={finalGoal}
                          onChange={(e) => setFinalGoal(e.target.value)}
                          placeholder="Final engineering deliverable goal..."
                          className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-white"
                        />
                      </div>
                    )}
                  </div>

                  {/* Live Generation Progress Indicator */}
                  {creatingJourney && generationStageText && (
                    <div className="rounded-2xl border border-indigo-500/40 bg-indigo-950/30 p-4 flex items-center gap-3 text-sm text-indigo-200 animate-pulse">
                      <Sparkles className="h-5 w-5 text-indigo-400 shrink-0" />
                      <span className="font-mono font-semibold">{generationStageText}</span>
                    </div>
                  )}

                  {/* GENERATE CURRICULUM CTA */}
                  <button
                    type="submit"
                    disabled={creatingJourney}
                    className="w-full inline-flex items-center justify-center gap-2.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-emerald-600 px-8 py-4 text-base font-extrabold uppercase tracking-wider text-white shadow-xl shadow-indigo-950/60 hover:from-indigo-500 hover:to-emerald-500 disabled:opacity-50 transition-all"
                  >
                    <Sparkles className="h-5 w-5" />
                    {creatingJourney
                      ? 'Generating Curriculum with qwen3.5:9b...'
                      : 'Generate Research & Build Blueprint →'}
                  </button>
                </form>

                {/* RIGHT COLUMN (4 COLS): MY PLANS SIDEBAR (With Delete & Continue) */}
                <div className="lg:col-span-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-extrabold text-white">My Plans</h3>
                    <span className="font-mono text-xs text-slate-400">
                      {journeys.length} ACTIVE
                    </span>
                  </div>

                  {journeys.length > 0 ? (
                    <div className="space-y-4">
                      {journeys.map((j) => {
                        const doneCount = (j.tasks || []).filter((t) => t.status === 'completed').length;
                        return (
                          <div
                            key={j.id}
                            className="rounded-2xl border border-slate-800/90 bg-slate-900/70 p-5 space-y-4 shadow-md hover:border-slate-700 transition-all"
                          >
                            <div className="flex items-center justify-between text-xs font-mono">
                              <span className="rounded-md border border-indigo-500/40 bg-indigo-500/15 px-2.5 py-0.5 font-bold uppercase text-indigo-300">
                                IN PROGRESS
                              </span>
                              <span className="text-slate-400">{j.duration_days} days target</span>
                            </div>

                            <div>
                              <h4 className="text-base font-extrabold uppercase tracking-tight text-white">
                                {j.title}
                              </h4>
                              <div className="mt-1 font-mono text-xs text-slate-400 capitalize">
                                {j.experience_level} · {doneCount} Tasks Done · {j.daily_minutes}m/day
                              </div>
                            </div>

                            <div className="space-y-1.5">
                              <div className="flex justify-between font-mono text-xs text-slate-400">
                                <span>Progress</span>
                                <span>{Math.round(j.progress_percent)}%</span>
                              </div>
                              <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                                <div
                                  className="h-full bg-indigo-500 rounded-full"
                                  style={{ width: `${Math.max(3, j.progress_percent)}%` }}
                                />
                              </div>
                            </div>

                            <div className="flex items-center justify-between border-t border-slate-800/80 pt-3">
                              <button
                                type="button"
                                onClick={() => handleDeleteJourney(j.id, j.title)}
                                className="inline-flex items-center gap-1.5 font-mono text-xs font-semibold text-slate-400 hover:text-rose-400 transition-colors"
                              >
                                <Trash2 className="h-3.5 w-3.5" /> Delete
                              </button>
                              <button
                                type="button"
                                onClick={async () => {
                                  await handleSelectJourney(j);
                                  setActiveNav('journeys');
                                }}
                                className="inline-flex items-center gap-1.5 font-mono text-xs font-extrabold uppercase text-indigo-400 hover:text-indigo-300"
                              >
                                CONTINUE <ArrowRight className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/40 p-8 text-center space-y-2">
                      <Map className="mx-auto h-8 w-8 text-slate-600" />
                      <div className="text-sm font-bold text-slate-300">No Active Plans Yet</div>
                      <p className="text-xs text-slate-500 leading-relaxed">
                        Fill out steps 1–3 on the left and click Generate to create your first personalized learning & CodeChef builder plan.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* =================================================================
              SCREEN 3: LEARNING PATHS & BLUEPRINT (Inspired by Screenshot #4 + Editable Blueprint)
             ================================================================= */}
          {activeNav === 'journeys' && (
            activeJourney ? (
              <div className="space-y-8">
                {/* Top Header */}
                <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
                  <div>
                    <h2 className="text-3xl font-extrabold tracking-tight text-white">LEARNING PATHS</h2>
                    <p className="mt-1 text-sm text-slate-300">
                      Your personalized AI-generated learning journeys, Scholar modules, and CodeChef Builder tracks.
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => handleDeleteJourney(activeJourney.id, activeJourney.title)}
                      className="inline-flex items-center gap-1.5 rounded-xl border border-rose-500/40 bg-rose-950/30 px-4 py-2.5 text-xs font-bold uppercase text-rose-300 hover:bg-rose-900/50 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" /> Delete Journey
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveNav('explore')}
                      className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-extrabold uppercase tracking-wider text-white hover:bg-indigo-500 shadow-lg"
                    >
                      <Plus className="h-4 w-4" /> NEW JOURNEY
                    </button>
                  </div>
                </div>

                {/* CURRENT FOCUS HERO CARD */}
                <div className="grid grid-cols-1 lg:grid-cols-12 rounded-2xl border border-indigo-500/40 bg-gradient-to-br from-slate-900 via-indigo-950/30 to-slate-900 overflow-hidden shadow-xl">
                  <div className="lg:col-span-8 p-8 space-y-5">
                    <div className="inline-flex items-center gap-2 font-mono text-xs font-bold uppercase tracking-wider text-indigo-400">
                      <span className="h-2 w-2 rounded-xs bg-indigo-400" /> CURRENT FOCUS
                    </div>
                    <h3 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                      {activeJourney.title}
                    </h3>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-slate-300">
                      <span className="capitalize font-semibold">{activeJourney.experience_level}</span>
                      <span>|</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 rounded-full bg-slate-800 overflow-hidden">
                          <div
                            className="h-full bg-emerald-400 rounded-full"
                            style={{ width: `${Math.max(4, activeJourney.progress_percent)}%` }}
                          />
                        </div>
                        <span className="font-mono text-xs font-bold text-emerald-400">
                          {Math.round(activeJourney.progress_percent)}% Complete
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 pt-2">
                      <button
                        type="button"
                        onClick={() => setActiveNav('scholar')}
                        className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-xs sm:text-sm font-extrabold uppercase tracking-wider text-white hover:bg-indigo-500 shadow-md"
                      >
                        START LEARNING (SCHOLAR) <Play className="h-3.5 w-3.5 fill-current" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleSwitchRoad('builder')}
                        className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 text-xs sm:text-sm font-extrabold uppercase tracking-wider text-white hover:bg-emerald-500 shadow-md"
                      >
                        OPEN CODECHEF BUILDER ROAD <Code2 className="h-4 w-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveNav('tasks')}
                        className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-xs font-bold uppercase text-slate-200 hover:bg-slate-800"
                      >
                        DAILY TASKS ({pendingTasks.length})
                      </button>
                    </div>
                  </div>

                  <div className="lg:col-span-4 border-t lg:border-t-0 lg:border-l border-slate-800/80 bg-slate-950/60 p-8 flex flex-col justify-center">
                    <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 space-y-2">
                      <div className="flex items-center justify-between font-mono text-xs text-slate-400">
                        <span>DAILY GOAL</span>
                        <span>{activeJourney.daily_minutes}M / DAY</span>
                      </div>
                      <div className="text-3xl font-extrabold text-white">Day 1</div>
                      <div className="font-mono text-xs text-slate-400">
                        of {activeJourney.duration_days} total days
                      </div>
                    </div>
                  </div>
                </div>

                {/* DAY-BY-DAY ZERO-TO-GENIUS PROGRESSION (SCHOLAR MASTERCLASS + HANDS-ON BUILDER LAB PER DAY) */}
                <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 p-7 space-y-5 shadow-lg">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <span className="font-mono text-xs font-bold uppercase tracking-wider text-indigo-400">
                        DAY-BY-DAY ZERO-TO-GENIUS ROADMAP · CONTINUOUS THEORY + HANDS-ON CODE
                      </span>
                      <h3 className="text-xl font-extrabold text-white mt-0.5">
                        Daily Scholar Masterclasses (Watch & Read) & Linked Builder Coding Labs
                      </h3>
                    </div>
                  </div>

                  <div className="divide-y divide-slate-800/80">
                    {activeJourney.concepts.map((c, idx) => {
                      const linkedM = effectiveProject?.milestones[idx] || effectiveProject?.milestones[0];
                      const dayNum = idx + 1;
                      return (
                        <div
                          key={c.id}
                          className="py-5 flex flex-wrap items-center justify-between gap-4"
                        >
                          <div className="flex items-start gap-5">
                            <div className="flex flex-col items-center justify-center rounded-xl border border-indigo-500/30 bg-indigo-950/30 px-3 py-2 min-w-[68px]">
                              <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                                DAY
                              </span>
                              <span className="font-mono text-2xl font-extrabold text-white">
                                0{dayNum}
                              </span>
                            </div>
                            <div>
                              <div className="flex flex-wrap items-center gap-2.5">
                                <h4 className="text-lg font-extrabold text-white">
                                  Day {dayNum}: {c.title}
                                </h4>
                                <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[11px] uppercase text-indigo-300">
                                  {c.prerequisite_level}
                                </span>
                                <span className="rounded bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5 font-mono text-[10px] font-bold text-emerald-300">
                                  📺 Watch + 📖 Read + 💻 Code
                                </span>
                              </div>
                              <p className="text-sm text-slate-300 mt-1 max-w-2xl">{c.summary}</p>
                              {linkedM && (
                                <div className="mt-2 inline-flex items-center gap-2 font-mono text-xs text-emerald-400">
                                  <Code2 className="h-3.5 w-3.5" />
                                  <span>Day {dayNum} · Lab {dayNum}: {linkedM.title}</span>
                                </div>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center gap-2.5">
                            <button
                              type="button"
                              onClick={() => handleSwitchRoad('scholar', c.id)}
                              className="rounded-xl border border-indigo-500/40 bg-indigo-950/40 px-4 py-2.5 text-xs font-bold text-indigo-200 hover:bg-indigo-900/60"
                            >
                              Day {dayNum} Masterclass (Watch/Read) →
                            </button>
                            <button
                              type="button"
                              onClick={() => handleSwitchRoad('builder', c.id, linkedM?.id || c.builder_milestone_id)}
                              className="rounded-xl border border-emerald-500/40 bg-emerald-950/40 px-4 py-2.5 text-xs font-bold text-emerald-200 hover:bg-emerald-900/60"
                            >
                              Day {dayNum} Coding Lab →
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* EDITABLE BLUEPRINT & CONCEPT GRAPH */}
                <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-8 space-y-6">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                        Editable Research & Build Blueprint (v{activeJourney.blueprint?.version || 1})
                      </span>
                      <h3 className="text-2xl font-extrabold text-white">{activeJourney.blueprint?.title}</h3>
                    </div>
                    <div className="flex items-center gap-3">
                      <input
                        type="text"
                        value={editingBlueprintTitle}
                        onChange={(e) => setEditingBlueprintTitle(e.target.value)}
                        className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-slate-100"
                        placeholder="Blueprint Title"
                      />
                      <button
                        type="button"
                        onClick={async () => {
                          const updated = await axiomApi.updateBlueprint(activeJourney.id, {
                            title: editingBlueprintTitle,
                            estimated_hours: editingBlueprintHours,
                            is_approved: true,
                          });
                          setJourneys((prev) => prev.map((j) => (j.id === updated.id ? updated : j)));
                          pushToast('Blueprint Updated', 'Saved changes to your Research & Build Blueprint.', 'success');
                        }}
                        className="rounded-xl bg-emerald-600 px-5 py-2 text-sm font-bold text-white hover:bg-emerald-500"
                      >
                        Save Blueprint
                      </button>
                    </div>
                  </div>

                  <ConceptGraphView
                    concepts={activeJourney.concepts}
                    selectedConceptId={conceptWorkspace?.concept.id || null}
                    onSelectConcept={(c) => handleSwitchRoad('scholar', c.id)}
                    onJumpToBuilder={(c) => handleSwitchRoad('builder', c.id, c.builder_milestone_id)}
                  />
                </div>
              </div>
            ) : (
              <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-12 text-center space-y-4">
                <Map className="mx-auto h-12 w-12 text-indigo-400" />
                <h3 className="text-2xl font-bold text-white">No Learning Paths Active Yet</h3>
                <p className="mx-auto max-w-md text-sm text-slate-400">
                  Open the Curriculum Planner to design your first personalized roadmap with qwen3.5:9b.
                </p>
                <button
                  type="button"
                  onClick={() => setActiveNav('explore')}
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-sm font-bold text-white hover:bg-indigo-500"
                >
                  <Plus className="h-4 w-4" /> Open Curriculum Planner
                </button>
              </div>
            )
          )}

          {/* =================================================================
              SCREEN 4: DAILY TASKS VIEW (Inspired by Screenshot #5)
             ================================================================= */}
          {activeNav === 'tasks' && (
            <div className="space-y-7">
              <div>
                <span className="font-mono text-xs font-bold uppercase tracking-wider text-indigo-400">
                  TASKS
                </span>
                <h2 className="text-3xl font-extrabold tracking-tight text-white">DAILY TASKS</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Auto-generated from your curriculum progress across Scholar Theory, CodeChef Builder Labs, and Socratic Assessments.
                </p>
              </div>

              {/* 3 SUMMARY CARDS: PENDING | COMPLETED | TOTAL */}
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
                <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 space-y-1 shadow-md">
                  <div className="text-3xl font-extrabold text-white">{pendingTasks.length}</div>
                  <div className="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                    PENDING
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 space-y-1 shadow-md">
                  <div className="text-3xl font-extrabold text-emerald-400">{completedTasks.length}</div>
                  <div className="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                    COMPLETED
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 p-6 space-y-1 shadow-md">
                  <div className="text-3xl font-extrabold text-indigo-400">{allTasks.length}</div>
                  <div className="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                    TOTAL
                  </div>
                </div>
              </div>

              {/* GROUPED TASKS LIST WITH START -> BUTTONS */}
              {activeJourney && allTasks.length > 0 ? (
                <div className="rounded-2xl border border-slate-800/90 bg-slate-900/60 overflow-hidden shadow-lg">
                  <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/70 px-6 py-4">
                    <div className="flex items-center gap-3">
                      <span className="h-2.5 w-2.5 rounded-xs bg-indigo-500" />
                      <span className="font-extrabold uppercase tracking-tight text-white">
                        {activeJourney.title}
                      </span>
                      <span className="rounded border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 font-mono text-[10px] font-bold uppercase text-emerald-300">
                        ACTIVE
                      </span>
                    </div>
                    <span className="font-mono text-xs text-slate-400">
                      {completedTasks.length}/{allTasks.length} Completed · {Math.round(activeJourney.progress_percent)}%
                    </span>
                  </div>

                  <div className="divide-y divide-slate-800/80">
                    {allTasks.map((t) => {
                      const isDone = t.status === 'completed';
                      const isBuilder = t.road === 'builder';
                      return (
                        <div
                          key={t.id}
                          className={`flex flex-wrap items-center justify-between gap-4 px-6 py-4 border-l-4 transition-colors ${
                            isBuilder ? 'border-l-emerald-500' : 'border-l-indigo-500'
                          } ${isDone ? 'bg-slate-950/40 opacity-65' : 'bg-slate-900/40 hover:bg-slate-900/80'}`}
                        >
                          <div className="flex items-center gap-4">
                            <input
                              type="checkbox"
                              checked={isDone}
                              onChange={async () => {
                                await axiomApi.toggleTask(t.id);
                                const jList = await axiomApi.listJourneys();
                                setJourneys(jList);
                                pushToast(
                                  isDone ? 'Task Marked Pending' : 'Task Completed! +XP',
                                  t.title,
                                  'success'
                                );
                              }}
                              className="h-4 w-4 rounded border-slate-700 text-indigo-600 cursor-pointer"
                            />
                            <div>
                              <div
                                className={`text-sm sm:text-base font-extrabold ${
                                  isDone ? 'line-through text-slate-500' : 'text-white'
                                }`}
                              >
                                {t.title}
                              </div>
                              <div className="font-mono text-xs text-slate-400 mt-0.5">
                                Day {t.day_number} · {t.road.toUpperCase()} ROAD · ~{t.estimated_minutes}m
                              </div>
                            </div>
                          </div>

                          <button
                            type="button"
                            onClick={() => {
                              if (isBuilder) {
                                handleSwitchRoad('builder', t.concept_id, t.milestone_id);
                              } else {
                                handleSwitchRoad('scholar', t.concept_id, t.milestone_id);
                              }
                            }}
                            className="inline-flex items-center gap-1.5 rounded-lg bg-white px-4 py-2 font-mono text-xs font-extrabold uppercase text-slate-950 hover:bg-slate-200 transition-colors"
                          >
                            START <ArrowRight className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/40 p-12 text-center space-y-3">
                  <CheckSquare className="mx-auto h-10 w-10 text-slate-600" />
                  <h3 className="text-lg font-bold text-white">No Daily Tasks Generated Yet</h3>
                  <p className="text-xs text-slate-400 max-w-md mx-auto">
                    Create a learning journey in the Curriculum Planner to automatically schedule your daily Study, CodeChef Lab, and Socratic Assessment tasks.
                  </p>
                  <button
                    type="button"
                    onClick={() => setActiveNav('explore')}
                    className="rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-bold text-white hover:bg-indigo-500"
                  >
                    Open Curriculum Planner →
                  </button>
                </div>
              )}
            </div>
          )}

          {/* =================================================================
              SCREEN 5: SCHOLAR WORKSPACE
             ================================================================= */}
          {activeNav === 'scholar' && (
            <ScholarWorkspaceView
              concepts={activeJourney?.concepts || []}
              workspace={conceptWorkspace}
              journeyDays={activeJourney?.days || []}
              currentDayNumber={currentDayNumber}
              totalDurationDays={activeJourney?.duration_days || activeJourney?.days?.length || 30}
              onSelectDay={(dNum) => setCurrentDayNumber(dNum)}
              onSelectConcept={async (cId) => {
                const cw = await axiomApi.getConceptWorkspace(cId);
                setConceptWorkspace(cw);
              }}
              onChangeDepth={async (depth, format, useLiveLlm) => {
                if (!conceptWorkspace) return;
                const cw = await axiomApi.changeExplanationDepth(conceptWorkspace.concept.id, {
                  depth_mode: depth,
                  learning_format: format,
                  use_live_llm: useLiveLlm,
                });
                setConceptWorkspace(cw);
                if (effectiveProject) {
                  const p = await axiomApi.getProject(effectiveProject.id);
                  setActiveProject(p);
                }
                const jList = await axiomApi.listJourneys();
                setJourneys(jList);
                pushToast(
                  `Deep-Synthesized Day Content & Lab (${depth.toUpperCase()})`,
                  'Generated with qwen3.5:9b + Verified YouTube & Web Grounding',
                  'success'
                );
              }}
              onSubmitFeynman={async (userExp, revExp, unc) => {
                if (!conceptWorkspace) return;
                await axiomApi.submitFeynman(conceptWorkspace.concept.id, {
                  user_explanation: userExp,
                  revised_explanation: revExp,
                  remaining_uncertainties: unc,
                });
                const cw = await axiomApi.getConceptWorkspace(conceptWorkspace.concept.id);
                setConceptWorkspace(cw);
                pushToast('Feynman Evaluation Complete!', 'Earned +60 XP for active reconstruction.', 'success');
              }}
              onReviewFlashcard={async (fcId, outcome) => {
                if (!conceptWorkspace) return;
                await axiomApi.reviewFlashcard(fcId, outcome);
                const cw = await axiomApi.getConceptWorkspace(conceptWorkspace.concept.id);
                setConceptWorkspace(cw);
              }}
              onAttemptRecall={async (qId, respText) => {
                if (!conceptWorkspace) return;
                await axiomApi.attemptRecallQuestion(qId, respText);
                const cw = await axiomApi.getConceptWorkspace(conceptWorkspace.concept.id);
                setConceptWorkspace(cw);
              }}
              onSubmitThinkDeeper={async (qId, reasoning) => {
                if (!conceptWorkspace) return;
                await axiomApi.submitThinkDeeper(qId, { user_reasoning: reasoning });
                const cw = await axiomApi.getConceptWorkspace(conceptWorkspace.concept.id);
                setConceptWorkspace(cw);
                pushToast('Socratic Inquiry Evaluated', 'Earned +75 XP.', 'success');
              }}
              onSwitchToBuilder={(cId, mId) => handleSwitchRoad('builder', cId, mId)}
              onSwitchToBuilderDay={(dNum) => {
                setCurrentDayNumber(dNum);
                setActiveNav('builder');
              }}
              onExportObsidian={(type, id) => handleExportObsidian(type, id)}
            />
          )}

          {/* =================================================================
              SCREEN 6: CODECHEF-STYLE STEP-BY-STEP BUILDER WORKSPACE
             ================================================================= */}
          {activeNav === 'builder' && (
            <BuilderWorkspaceView
              project={effectiveProject}
              selectedMilestoneId={selectedMilestoneId}
              journeyDays={activeJourney?.days || []}
              currentDayNumber={currentDayNumber}
              totalDurationDays={activeJourney?.duration_days || activeJourney?.days?.length || 30}
              onSelectDay={(dNum) => setCurrentDayNumber(dNum)}
              onSelectMilestone={(mId) => setSelectedMilestoneId(mId)}
              onUnlockHint={async (mId, lvl) => {
                await axiomApi.unlockMilestoneHint(mId, lvl);
                if (effectiveProject) {
                  const p = await axiomApi.getProject(effectiveProject.id);
                  setActiveProject(p);
                  pushToast(`Unlocked Hint Level ${lvl}/5`, p.title, 'info');
                }
              }}
              onCompleteMilestone={async (mId) => {
                const updated = await axiomApi.completeMilestone(mId);
                setActiveProject(updated);
                pushToast('CodeChef Builder Lab Completed! +100 XP', 'Next sequential milestone unlocked.', 'success');
              }}
              onSaveArtifact={async (artId, content) => {
                await axiomApi.updateArtifact(artId, content);
                if (effectiveProject) {
                  const p = await axiomApi.getProject(effectiveProject.id);
                  setActiveProject(p);
                }
              }}
              onVerifyArtifact={async (artId) => {
                const res = await axiomApi.verifyArtifact(artId);
                pushToast(
                  res.passed ? 'All Sandbox Test Cases Passed!' : 'Sandbox Test Case Failed',
                  res.file_path,
                  res.passed ? 'success' : 'warning'
                );
                return res;
              }}
              onVerifyDayLab={async (dNum, code) => {
                if (!activeJourney) return null;
                const res = await axiomApi.verifyDayLab(activeJourney.id, dNum, { code_submission: code });
                pushToast(
                  res.passed ? `Day ${dNum} All Test Cases Passed!` : `Day ${dNum} Test Case Failed`,
                  (res as any).execution_engine || res.execution_sandbox || 'Isolated Sandbox',
                  res.passed ? 'success' : 'warning'
                );
                return res;
              }}
              onCompleteDay={async (dNum) => {
                if (!activeJourney) return;
                await axiomApi.markDayCompleted(activeJourney.id, dNum);
                const jList = await axiomApi.listJourneys();
                setJourneys(jList);
                pushToast('Day Builder Lab Completed! +100 XP', `Day ${dNum} marked completed.`, 'success');
                if (dNum < (activeJourney.days?.length || 0)) {
                  setCurrentDayNumber(dNum + 1);
                }
              }}
              onSubmitReflection={async (payload) => {
                await axiomApi.createReflection(payload);
                const kw = await axiomApi.getKnowledgeWorkspace();
                setKnowledgeWorkspace(kw);
                pushToast('Reflection Saved', 'Indexed in your Personal Knowledge Workspace.', 'success');
              }}
              onSwitchToScholar={(cId) => handleSwitchRoad('scholar', cId)}
              onSwitchToScholarDay={(dNum) => {
                setCurrentDayNumber(dNum);
                setActiveNav('scholar');
              }}
              onOpenExperimentLab={() => setActiveNav('experiments')}
              onGoToPlanner={() => setActiveNav('explore')}
              onSynthesizeDayLab={async (cId) => {
                const cw = await axiomApi.changeExplanationDepth(cId, {
                  depth_mode: 'research',
                  learning_format: 'combined',
                  use_live_llm: true,
                });
                setConceptWorkspace(cw);
                if (effectiveProject) {
                  const p = await axiomApi.getProject(effectiveProject.id);
                  setActiveProject(p);
                }
                const jList = await axiomApi.listJourneys();
                setJourneys(jList);
                pushToast(
                  'Synthesized Bespoke Day Python Lab!',
                  'Updated code & 3 test cases with qwen3.5:9b.',
                  'success'
                );
              }}
            />
          )}

          {/* =================================================================
              SCREEN 7: RESEARCH LIBRARY (Free Web & Academic Discovery)
             ================================================================= */}
          {activeNav === 'library' && (
            <div className="space-y-8">
              <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-8 sm:p-10 space-y-6">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                    Authentic Resource Intelligence Engine + Free Live Web Search
                  </span>
                  <h2 className="mt-2 text-3xl font-extrabold text-white">
                    Live Academic, GitHub & Web Resource Discovery
                  </h2>
                  <p className="mt-2 text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
                    Concurrently queries Wikipedia, DuckDuckGo, HackerNews Algolia, arXiv, OpenAlex, GitHub, and Hugging Face with zero mandatory cost.
                  </p>
                </div>

                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    const res = await axiomApi.discoverResources(resourceQuery, freeOnlyFilter, true);
                    setResourceDiscovery(res);
                    pushToast('Live Discovery Complete', `Ranked ${res.total_count} verified resources.`, 'success');
                  }}
                  className="flex flex-wrap items-center gap-3.5 pt-2"
                >
                  <input
                    type="text"
                    value={resourceQuery}
                    onChange={(e) => setResourceQuery(e.target.value)}
                    placeholder="Search technical topics, papers, university courses, or GitHub implementations..."
                    className="flex-1 min-w-[300px] rounded-xl border border-slate-700 bg-slate-950 px-5 py-3.5 text-base text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
                  />
                  <label className="flex items-center gap-2 text-sm text-slate-200 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={freeOnlyFilter}
                      onChange={(e) => setFreeOnlyFilter(e.target.checked)}
                      className="h-4 w-4 rounded border-slate-700 text-indigo-600 focus:ring-0"
                    />
                    <span>Genuinely Free Resources Only</span>
                  </label>
                  <button
                    type="submit"
                    className="rounded-xl bg-indigo-600 px-6 py-3.5 text-sm font-bold text-white hover:bg-indigo-500 shadow-md"
                  >
                    Discover & Rank Resources
                  </button>
                </form>

                {resourceDiscovery && (
                  <div className="space-y-6 pt-4">
                    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                      {resourceDiscovery.primary_resource && (
                        <div className="rounded-2xl border border-indigo-500/40 bg-indigo-950/20 p-7 space-y-3.5">
                          <div className="flex items-center justify-between text-xs">
                            <span className="rounded-md bg-indigo-600 px-3 py-1 font-bold text-white">
                              PRIMARY RECOMMENDED RESOURCE
                            </span>
                            <span className="rounded-md border border-emerald-500/40 bg-emerald-500/15 px-3 py-1 font-semibold text-emerald-300">
                              {resourceDiscovery.primary_resource.access_status}
                            </span>
                          </div>
                          <h3 className="text-xl font-bold text-white">
                            {resourceDiscovery.primary_resource.title}
                          </h3>
                          <p className="text-sm leading-relaxed text-slate-200">
                            {resourceDiscovery.primary_resource.description}
                          </p>
                          <div className="flex items-center justify-between pt-3 text-xs text-slate-300 border-t border-indigo-500/20">
                            <span>
                              Provider: <strong className="uppercase">{resourceDiscovery.primary_resource.provider_name}</strong>
                            </span>
                            <a
                              href={resourceDiscovery.primary_resource.url}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 font-bold text-indigo-400 hover:text-indigo-300"
                            >
                              Open Source <ExternalLink className="h-3.5 w-3.5" />
                            </a>
                          </div>
                        </div>
                      )}

                      {resourceDiscovery.practical_repository && (
                        <div className="rounded-2xl border border-emerald-500/40 bg-emerald-950/20 p-7 space-y-3.5">
                          <div className="flex items-center justify-between text-xs">
                            <span className="rounded-md bg-emerald-600 px-3 py-1 font-bold text-white">
                              PRACTICAL REPOSITORY
                            </span>
                            <span className="rounded-md border border-emerald-500/40 bg-emerald-500/15 px-3 py-1 font-semibold text-emerald-300">
                              {resourceDiscovery.practical_repository.access_status}
                            </span>
                          </div>
                          <h3 className="text-xl font-bold text-white">
                            {resourceDiscovery.practical_repository.title}
                          </h3>
                          <p className="text-sm leading-relaxed text-slate-200">
                            {resourceDiscovery.practical_repository.description}
                          </p>
                          <div className="flex items-center justify-between pt-3 text-xs text-slate-300 border-t border-emerald-500/20">
                            <span>
                              Provider: <strong className="uppercase">{resourceDiscovery.practical_repository.provider_name}</strong>
                            </span>
                            <a
                              href={resourceDiscovery.practical_repository.url}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 font-bold text-emerald-400 hover:text-emerald-300"
                            >
                              View Repository <ExternalLink className="h-3.5 w-3.5" />
                            </a>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {resourceDiscovery.all_resources.map((r) => (
                        <div
                          key={r.id}
                          className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5 flex flex-col justify-between space-y-3"
                        >
                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-mono uppercase text-indigo-400 font-bold">
                                {r.provider_name} · {r.resource_type}
                              </span>
                              <span className="rounded border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[11px] text-emerald-300">
                                {r.access_status}
                              </span>
                            </div>
                            <h5 className="text-sm font-bold text-white leading-snug">{r.title}</h5>
                            <p className="line-clamp-3 text-xs leading-relaxed text-slate-300">{r.description}</p>
                          </div>
                          <div className="flex items-center justify-between border-t border-slate-800 pt-2.5 text-xs text-slate-400">
                            <span>Credibility: {Math.round(r.credibility_score * 100)}%</span>
                            <a
                              href={r.url}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 font-semibold text-indigo-400 hover:text-indigo-300"
                            >
                              Open <ExternalLink className="h-3 w-3" />
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* =================================================================
              SCREEN 8: PROJECTS & CONTINUITY
             ================================================================= */}
          {activeNav === 'projects' && (
            projects.length > 0 ? (
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {projects.map((p) => (
                  <div key={p.id} className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-7 space-y-5">
                    <div className="flex items-center justify-between">
                      <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-bold text-emerald-300">
                        {p.domain}
                      </span>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => handleExportObsidian('project', p.id)}
                          className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800"
                        >
                          Export to Obsidian
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setActiveProject(p);
                            setSelectedMilestoneId(p.milestones[0]?.id || null);
                            setActiveNav('builder');
                          }}
                          className="rounded-xl bg-emerald-600 px-3.5 py-1.5 text-xs font-bold text-white hover:bg-emerald-500"
                        >
                          Open in CodeChef Builder →
                        </button>
                      </div>
                    </div>
                    <h3 className="text-2xl font-bold text-white">{p.title}</h3>
                    <p className="text-sm leading-relaxed text-slate-300">{p.objective}</p>
                    <MermaidDiagram chart={p.architecture_mermaid} title="System Architecture" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-12 text-center space-y-4">
                <FolderGit2 className="mx-auto h-12 w-12 text-emerald-400" />
                <h3 className="text-2xl font-bold text-white">No Engineering Projects Active</h3>
                <p className="mx-auto max-w-md text-sm text-slate-400">
                  Generate a curriculum plan to automatically provision a multi-milestone Builder project.
                </p>
                <button
                  type="button"
                  onClick={() => setActiveNav('explore')}
                  className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 text-sm font-bold text-white hover:bg-emerald-500"
                >
                  <Plus className="h-4 w-4" /> Architect a Builder Project
                </button>
              </div>
            )
          )}

          {/* =================================================================
              SCREEN 9: EXPERIMENT LABORATORY
             ================================================================= */}
          {activeNav === 'experiments' && (
            <div className="space-y-8">
              <div className="rounded-2xl border border-amber-500/30 bg-slate-900/60 p-8 space-y-6">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                    Scientific Experiment Laboratory
                  </span>
                  <h2 className="mt-1 text-3xl font-extrabold text-white">
                    Hypothesis-Driven Engineering Experiments
                  </h2>
                </div>

                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    if (!expTitle.trim() || !expHypothesis.trim()) return;
                    await axiomApi.createExperiment({
                      project_id: effectiveProject?.id || 1,
                      title: expTitle,
                      hypothesis: expHypothesis,
                      objective: 'Controlled parameter & invariant ablation study',
                      variables_changed: [expVariables],
                      procedure: expProcedure || 'Varied target parameter while holding baseline seed constant.',
                      expected_outcome: expExpected,
                      actual_outcome: expActual,
                      observations: expActual,
                      conclusion: expConclusion || 'Hypothesis evaluated and recorded.',
                      status: 'succeeded',
                    });
                    const list = await axiomApi.listExperiments();
                    setExperiments(list);
                    setExpTitle('');
                    setExpHypothesis('');
                    pushToast('Experiment Logged! +70 XP', expTitle, 'success');
                  }}
                  className="grid grid-cols-1 gap-4 md:grid-cols-2"
                >
                  <input
                    type="text"
                    value={expTitle}
                    onChange={(e) => setExpTitle(e.target.value)}
                    placeholder="Experiment Title..."
                    className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white"
                  />
                  <input
                    type="text"
                    value={expVariables}
                    onChange={(e) => setExpVariables(e.target.value)}
                    placeholder="Variables Changed..."
                    className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white"
                  />
                  <input
                    type="text"
                    value={expHypothesis}
                    onChange={(e) => setExpHypothesis(e.target.value)}
                    placeholder="Formal Hypothesis..."
                    className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white"
                  />
                  <input
                    type="text"
                    value={expProcedure}
                    onChange={(e) => setExpProcedure(e.target.value)}
                    placeholder="Experimental Procedure..."
                    className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white"
                  />
                  <input
                    type="text"
                    value={expExpected}
                    onChange={(e) => setExpExpected(e.target.value)}
                    placeholder="Expected Outcome..."
                    className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white"
                  />
                  <input
                    type="text"
                    value={expActual}
                    onChange={(e) => setExpActual(e.target.value)}
                    placeholder="Actual Outcome..."
                    className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white"
                  />
                  <input
                    type="text"
                    value={expConclusion}
                    onChange={(e) => setExpConclusion(e.target.value)}
                    placeholder="Conclusion..."
                    className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white"
                  />
                  <button
                    type="submit"
                    className="rounded-xl bg-amber-600 px-6 py-3 text-sm font-bold text-white hover:bg-amber-500"
                  >
                    Record Experiment Run
                  </button>
                </form>
              </div>

              <div className="space-y-4">
                {experiments.map((exp) => (
                  <div key={exp.id} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="rounded-full bg-amber-500/20 px-3 py-1 font-mono text-xs font-bold uppercase text-amber-300">
                        EXPERIMENT #{exp.id} · {exp.status}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleExportObsidian('experiment', exp.id)}
                        className="text-xs font-semibold text-indigo-400 hover:underline"
                      >
                        Export to Obsidian
                      </button>
                    </div>
                    <h3 className="text-lg font-bold text-white">{exp.title}</h3>
                    <p className="text-sm text-slate-300">
                      <strong>Hypothesis:</strong> {exp.hypothesis}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* =================================================================
              SCREEN 10: PERSONAL KNOWLEDGE WORKSPACE (Obsidian Sync & Notes)
             ================================================================= */}
          {activeNav === 'knowledge' && (
            <div className="space-y-8">
              <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-8 space-y-6">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                    Obsidian-Compatible Personal Knowledge Workspace
                  </span>
                  <h2 className="mt-1 text-3xl font-extrabold text-white">
                    My Knowledge, Notes, Wikilinks & Learning History
                  </h2>
                </div>

                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    if (!noteTitle.trim() || !noteContent.trim()) return;
                    await axiomApi.createNote({
                      title: noteTitle,
                      content_markdown: noteContent,
                      personal_understanding: noteUnderstanding,
                      note_type: 'concept_note',
                      journey_id: activeJourney?.id,
                      tags: noteTags.split(',').map((t) => t.trim()),
                      unresolved_questions: [],
                    });
                    const kw = await axiomApi.getKnowledgeWorkspace();
                    setKnowledgeWorkspace(kw);
                    setNoteTitle('');
                    setNoteContent('');
                    setNoteUnderstanding('');
                    pushToast('Note Created & Indexed', 'Saved in SQLite FTS5 knowledge graph.', 'success');
                  }}
                  className="grid grid-cols-1 gap-4 md:grid-cols-3 rounded-2xl border border-slate-800 bg-slate-950/70 p-6"
                >
                  <input
                    type="text"
                    value={noteTitle}
                    onChange={(e) => setNoteTitle(e.target.value)}
                    placeholder="Note Title (supports [[Wikilinks]])..."
                    className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
                  />
                  <input
                    type="text"
                    value={noteUnderstanding}
                    onChange={(e) => setNoteUnderstanding(e.target.value)}
                    placeholder="Key First-Principles Takeaway..."
                    className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
                  />
                  <input
                    type="text"
                    value={noteTags}
                    onChange={(e) => setNoteTags(e.target.value)}
                    placeholder="Tags (comma-separated)"
                    className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white"
                  />
                  <textarea
                    rows={3}
                    value={noteContent}
                    onChange={(e) => setNoteContent(e.target.value)}
                    placeholder="Markdown note content..."
                    className="md:col-span-2 rounded-xl border border-slate-700 bg-slate-900 p-4 text-sm text-white"
                  />
                  <button
                    type="submit"
                    className="rounded-xl bg-indigo-600 px-6 py-3 text-sm font-bold text-white hover:bg-indigo-500"
                  >
                    Create Knowledge Note
                  </button>
                </form>

                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                  {(knowledgeWorkspace?.my_knowledge_notes || []).map((n: any) => (
                    <div key={n.id} className="rounded-2xl border border-slate-800 bg-slate-950/80 p-6 space-y-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-mono text-indigo-400 font-semibold">{n.obsidian_folder}</span>
                        <button
                          type="button"
                          onClick={() => handleExportObsidian('note', n.id)}
                          className="inline-flex items-center gap-1 rounded-lg bg-indigo-600/20 border border-indigo-500/40 px-3 py-1 text-xs font-semibold text-indigo-300"
                        >
                          <FileDown className="h-3.5 w-3.5" /> Export to Obsidian
                        </button>
                      </div>
                      <h3 className="text-lg font-bold text-white">{n.title}</h3>
                      <div className="whitespace-pre-line text-sm text-slate-200">{n.content_markdown}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* =================================================================
              SCREEN 11: THINK DEEPER & JANE STREET SOCRATIC TUTOR (qwen3.5:9b)
             ================================================================= */}
          {activeNav === 'think_deeper' && (
            <div className="space-y-8">
              {/* JANE STREET SOCRATIC TUTOR INTERACTIVE STUDIO */}
              <div className="rounded-2xl border border-indigo-500/40 bg-slate-900/80 p-8 space-y-6 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <span className="rounded-md bg-indigo-500/20 border border-indigo-500/40 px-3 py-1 font-mono text-xs font-bold uppercase text-indigo-300">
                      JANE STREET SOCRATIC TUTOR · MAIEUTIC LOOP (QWEN3.5:9B)
                    </span>
                    <h2 className="mt-2 text-2xl sm:text-3xl font-extrabold text-white">
                      Interactive Socratic Probing & Devil&apos;s Advocate Arena
                    </h2>
                    <p className="mt-1 text-sm text-slate-300 max-w-3xl">
                      Inspired by Jane Street&apos;s <code className="text-indigo-300">socratic-tutor</code> skill: tracks your mastery from Level 0 (Unaware) to Level 5 (Can Teach & Handle Edge Cases), asks one probing question at a time, and plays devil&apos;s advocate when you&apos;re right.
                    </p>
                  </div>

                  {/* Quick Socratic Commands */}
                  <div className="flex flex-wrap gap-2">
                    {['show progress', 'harder', 'easier', 'just tell me'].map((cmd) => (
                      <button
                        key={cmd}
                        type="button"
                        disabled={socraticBusy}
                        onClick={async () => {
                          setSocraticBusy(true);
                          try {
                            const res = await axiomApi.runSocraticTutor({
                              concept_id: conceptWorkspace?.concept.id || activeJourney?.concepts[0]?.id || null,
                              user_message: cmd,
                              command: cmd,
                            });
                            setSocraticState(res);
                          } finally {
                            setSocraticBusy(false);
                          }
                        }}
                        className="rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 font-mono text-xs font-bold uppercase text-indigo-300 hover:border-indigo-500 hover:text-white transition-colors"
                      >
                        /{cmd}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Subskill Mastery Bar Map */}
                {socraticState?.subskill_map && socraticState.subskill_map.length > 0 && (
                  <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs space-y-1.5">
                    <div className="text-indigo-400 font-bold uppercase mb-2">
                      Subskill Mastery Map (0 = Unaware → 5 = Can Teach & Handle Adversarial Regimes)
                    </div>
                    {socraticState.subskill_map.map((s: any, i: number) => (
                      <div key={i} className="flex flex-wrap items-center justify-between gap-2 text-slate-200">
                        <span>
                          {i + 1}. {s.title}
                        </span>
                        <span className="text-emerald-400">
                          {s.bar} <strong className="text-indigo-300 ml-2">{s.status_tag}</strong>
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Tutor Output Display */}
                {socraticState && (
                  <div className="rounded-2xl border border-indigo-500/30 bg-indigo-950/20 p-6 space-y-2">
                    <div className="flex items-center justify-between font-mono text-xs text-indigo-300">
                      <span>
                        ACTIVE SUBSKILL: <strong>{socraticState.concept_title}</strong> (Level {socraticState.current_level}/5)
                      </span>
                      <span>MODEL: {socraticState.model_used}</span>
                    </div>
                    <MarkdownRenderer
                      content={socraticState.tutor_reply}
                      className="text-base leading-relaxed text-slate-100 pt-1"
                    />
                  </div>
                )}

                {/* Learner Input Form */}
                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    if (!socraticInput.trim()) return;
                    setSocraticBusy(true);
                    try {
                      const res = await axiomApi.runSocraticTutor({
                        concept_id: conceptWorkspace?.concept.id || activeJourney?.concepts[0]?.id || null,
                        user_message: socraticInput,
                      });
                      setSocraticState(res);
                      setSocraticInput('');
                      pushToast('Socratic Probe Evaluated', `Mastery Level: ${res.current_level}/5`, 'info');
                    } finally {
                      setSocraticBusy(false);
                    }
                  }}
                  className="flex flex-wrap gap-3"
                >
                  <input
                    type="text"
                    value={socraticInput}
                    onChange={(e) => setSocraticInput(e.target.value)}
                    placeholder="Defend your reasoning, answer the tutor's probe, or type 'harder' / 'just tell me'..."
                    className="flex-1 min-w-[260px] rounded-xl border border-slate-700 bg-slate-950 px-4 py-3.5 text-sm text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
                  />
                  <button
                    type="submit"
                    disabled={socraticBusy}
                    className="rounded-xl bg-indigo-600 px-6 py-3.5 text-xs sm:text-sm font-extrabold uppercase tracking-wider text-white hover:bg-indigo-500 disabled:opacity-50"
                  >
                    {socraticBusy ? 'Probing with qwen3.5:9b...' : 'Submit to Socratic Tutor →'}
                  </button>
                </form>
              </div>

              {/* THINK DEEPER CARDS */}
              {thinkDeeperList.length > 0 && (
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                  {thinkDeeperList.map((td) => (
                    <div key={td.id} className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-7 space-y-4">
                      <span className="rounded-md bg-purple-500/20 px-3 py-1 font-mono text-xs font-bold uppercase text-purple-300">
                        {td.question_category.replace('_', ' ')}
                      </span>
                      <h4 className="text-lg font-bold text-white leading-relaxed">{td.prompt}</h4>
                      <p className="text-sm text-amber-200/95">
                        <strong>Hint:</strong> {td.optional_hint}
                      </p>
                      <button
                        type="button"
                        onClick={async () => {
                          if (td.concept_id) {
                            const cw = await axiomApi.getConceptWorkspace(td.concept_id);
                            setConceptWorkspace(cw);
                            setActiveNav('scholar');
                          }
                        }}
                        className="text-sm font-semibold text-indigo-400 hover:text-indigo-300"
                      >
                        Open in Concept Socratic Workspace →
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* =================================================================
              SCREEN 12: SETTINGS, AI PROVIDERS & AUTOMATION
             ================================================================= */}
          {activeNav === 'settings' && (
            <SettingsAndAutomationView
              aiStatus={aiStatus}
              memories={memories}
              obsidianConfig={obsidianConfig}
              automationStatus={automationStatus}
              backups={backups}
              onRefreshStatus={loadSettingsAndHardware}
              onUpdateProvider={async (payload) => {
                const updated = await axiomApi.updateAiProvider(payload);
                setAiStatus(updated);
                pushToast('AI Provider Updated', `Active default model: ${payload.default_model || 'qwen3.5:9b'}`, 'success');
              }}
              onAddMemory={async (cat, key, stmt) => {
                await axiomApi.upsertMemory({
                  memory_category: cat,
                  subject_key: key,
                  fact_statement: stmt,
                });
                const mList = await axiomApi.listMemories();
                setMemories(mList);
              }}
              onDeleteMemory={async (id) => {
                await axiomApi.deleteMemory(id);
                const mList = await axiomApi.listMemories();
                setMemories(mList);
              }}
              onUpdateObsidian={async (payload) => {
                const cfg = await axiomApi.updateObsidianConfig(payload);
                setObsidianConfig(cfg);
                pushToast('Updated Obsidian Configuration', cfg.vault_name, 'success');
              }}
              onRunWorkflow={async (wfKey) => {
                const res = await axiomApi.executeAutomationWorkflow(wfKey);
                await loadSettingsAndHardware();
                return res;
              }}
              onCreateBackup={async () => {
                await axiomApi.createBackup();
                const bks = await axiomApi.listBackups();
                setBackups(bks);
                pushToast('Created Timestamped Backup', 'Saved SQLite + Markdown snapshot.', 'success');
              }}
            />
          )}
        </main>
      </div>

      {/* COMMAND PALETTE & SEARCH MODAL (Ctrl+K) */}
      {commandPaletteOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/80 pt-20 p-4 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-3 flex-1">
                <Search className="h-5 w-5 text-indigo-400" />
                <input
                  type="text"
                  autoFocus
                  value={searchQuery}
                  onChange={async (e) => {
                    const val = e.target.value;
                    setSearchQuery(val);
                    if (val.trim().length >= 2) {
                      const res = await axiomApi.globalSearch(val);
                      setSearchResults(res.results || []);
                    } else {
                      setSearchResults([]);
                    }
                  }}
                  placeholder="Search concepts, lessons, notes, projects, experiments, or resources (SQLite FTS5)..."
                  className="w-full bg-transparent text-base text-white placeholder:text-slate-500 focus:outline-none"
                />
              </div>
              <button
                type="button"
                onClick={() => setCommandPaletteOpen(false)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {searchResults.length > 0 && (
              <div className="max-h-64 overflow-y-auto space-y-2">
                {searchResults.map((item, idx) => (
                  <div
                    key={idx}
                    onClick={async () => {
                      setCommandPaletteOpen(false);
                      if (item.entity_type === 'concept') {
                        const cw = await axiomApi.getConceptWorkspace(item.entity_id);
                        setConceptWorkspace(cw);
                        setActiveNav('scholar');
                      } else if (item.entity_type === 'project') {
                        setActiveNav('builder');
                      } else if (item.entity_type === 'note') {
                        setActiveNav('knowledge');
                      } else if (item.entity_type === 'resource') {
                        setActiveNav('library');
                      }
                    }}
                    className="cursor-pointer rounded-xl border border-slate-800 bg-slate-950 p-3.5 text-xs hover:border-indigo-500 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-sm">{item.title}</span>
                      <span className="rounded bg-indigo-500/20 px-2 py-0.5 font-mono text-[11px] uppercase text-indigo-300">
                        {item.entity_type}
                      </span>
                    </div>
                    <div className="mt-1 text-slate-400">{item.snippet}</div>
                  </div>
                ))}
              </div>
            )}

            <div className="border-t border-slate-800 pt-3">
              <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                Quick Navigation
              </div>
              <div className="flex flex-wrap gap-2">
                {allNavItems.map((nav) => (
                  <button
                    key={nav.id}
                    type="button"
                    onClick={() => {
                      setActiveNav(nav.id);
                      setCommandPaletteOpen(false);
                    }}
                    className="rounded-xl border border-slate-800 bg-slate-950 px-3.5 py-1.5 text-xs font-medium text-slate-300 hover:border-indigo-500 hover:text-white"
                  >
                    Go to {nav.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* OBSIDIAN EXPORT MODAL */}
      {obsidianExportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-2xl border border-indigo-500/40 bg-slate-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-white">
                Obsidian Markdown Export: {obsidianExportModal.title}
              </h3>
              <button
                type="button"
                onClick={() => setObsidianExportModal(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4 text-xs text-emerald-200 space-y-1">
              <div>
                <strong>Vault Path:</strong> {obsidianExportModal.relative_vault_path}
              </div>
              <div>
                <strong>Staging File Written:</strong> {obsidianExportModal.written_file_path}
              </div>
            </div>
            <pre className="max-h-60 overflow-y-auto rounded-xl bg-slate-950 p-4 font-mono text-xs text-slate-300">
              {obsidianExportModal.markdown_preview}
            </pre>
            <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
              <a
                href={obsidianExportModal.obsidian_open_uri}
                className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-500/40 bg-indigo-950/50 px-4 py-2 text-xs font-semibold text-indigo-200 hover:bg-indigo-900"
              >
                Open in Obsidian (`obsidian://open`) <ExternalLink className="h-3.5 w-3.5" />
              </a>
              <a
                href={obsidianExportModal.obsidian_new_uri}
                className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500"
              >
                Create Note in Obsidian (`obsidian://new`) <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
