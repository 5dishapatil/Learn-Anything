import {
  ConceptWorkspaceData,
  ExperimentData,
  LearningJourneyData,
  ProjectFullData,
  ResourceDiscoveryResponse,
  ThinkDeeperQuestionItem,
} from '../types/axiom';

const API_BASE = '/api/v1';

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
    ...options,
  });
  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error(errText || `HTTP ${resp.status}`);
  }
  return resp.json();
}

export const axiomApi = {
  getDashboard: () => requestJson<any>(`${API_BASE}/dashboard`),
  getResumeBrief: (journeyId?: number) =>
    requestJson<any>(`${API_BASE}/sessions/resume${journeyId ? `?journey_id=${journeyId}` : ''}`),
  listJourneys: () => requestJson<LearningJourneyData[]>(`${API_BASE}/journeys`),
  createJourney: (payload: {
    user_intent: string;
    experience_level: string;
    daily_minutes: number;
    duration_days: number;
    target_deadline?: string;
    road_mode: string;
    preferred_format: string;
    existing_knowledge?: string;
    final_project_goal?: string;
  }) =>
    requestJson<LearningJourneyData>(`${API_BASE}/journeys`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteJourney: (journeyId: number) =>
    requestJson<{ deleted: boolean; journey_id: number; title: string }>(`${API_BASE}/journeys/${journeyId}`, {
      method: 'DELETE',
    }),
  liveWebSearch: (query: string) =>
    requestJson<{
      query: string;
      count: number;
      results: Array<any>;
      grounding_digest: string;
    }>(`${API_BASE}/web-search?query=${encodeURIComponent(query)}`),
  runSocraticTutor: (payload: { concept_id?: number | null; user_message: string; command?: string }) =>
    requestJson<{
      concept_id: number | null;
      concept_title: string;
      current_level: number;
      max_level: number;
      model_used: string;
      tutor_reply: string;
      subskill_map: Array<{
        concept_id: number;
        title: string;
        level: number;
        max_level: number;
        bar: string;
        status_tag: string;
      }>;
    }>(`${API_BASE}/socratic-tutor`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateBlueprint: (
    journeyId: number,
    payload: {
      title?: string;
      objective?: string;
      what_will_be_created?: string;
      proposed_architecture?: string;
      estimated_hours?: number;
      is_approved?: boolean;
    }
  ) =>
    requestJson<LearningJourneyData>(`${API_BASE}/journeys/${journeyId}/blueprint`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  switchRoad: (
    journeyId: number,
    payload: { target_road: 'scholar' | 'builder'; concept_id?: number | null; milestone_id?: number | null }
  ) =>
    requestJson<any>(`${API_BASE}/journeys/${journeyId}/switch-road`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  toggleTask: (taskId: number) =>
    requestJson<any>(`${API_BASE}/tasks/${taskId}/toggle`, {
      method: 'POST',
    }),
  getConceptWorkspace: (conceptId: number) =>
    requestJson<ConceptWorkspaceData>(`${API_BASE}/concepts/${conceptId}`),
  changeExplanationDepth: (
    conceptId: number,
    payload: { depth_mode: string; learning_format: string; use_live_llm?: boolean }
  ) =>
    requestJson<ConceptWorkspaceData>(`${API_BASE}/concepts/${conceptId}/explain`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  submitFeynman: (
    conceptId: number,
    payload: { user_explanation: string; revised_explanation?: string; remaining_uncertainties?: string }
  ) =>
    requestJson<any>(`${API_BASE}/concepts/${conceptId}/feynman`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  reviewFlashcard: (flashcardId: number, outcome: 'again' | 'hard' | 'good' | 'easy') =>
    requestJson<any>(`${API_BASE}/recall/flashcards/${flashcardId}/review`, {
      method: 'POST',
      body: JSON.stringify({ outcome }),
    }),
  attemptRecallQuestion: (questionId: number, userResponse: string) =>
    requestJson<any>(`${API_BASE}/recall/questions/${questionId}/attempt`, {
      method: 'POST',
      body: JSON.stringify({ user_response: userResponse }),
    }),
  listThinkDeeper: () => requestJson<ThinkDeeperQuestionItem[]>(`${API_BASE}/think-deeper`),
  submitThinkDeeper: (questionId: number, payload: { user_reasoning: string; followup_reply?: string }) =>
    requestJson<any>(`${API_BASE}/think-deeper/${questionId}/respond`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  listProjects: () => requestJson<ProjectFullData[]>(`${API_BASE}/projects`),
  getProject: (projectId: number) => requestJson<ProjectFullData>(`${API_BASE}/projects/${projectId}`),
  unlockMilestoneHint: (milestoneId: number, level: number) =>
    requestJson<any>(`${API_BASE}/milestones/${milestoneId}/hints`, {
      method: 'POST',
      body: JSON.stringify({ level }),
    }),
  completeMilestone: (milestoneId: number) =>
    requestJson<ProjectFullData>(`${API_BASE}/milestones/${milestoneId}/complete`, {
      method: 'POST',
    }),
  updateArtifact: (artifactId: number, content: string) =>
    requestJson<any>(`${API_BASE}/artifacts/${artifactId}`, {
      method: 'PUT',
      body: JSON.stringify({ content }),
    }),
  verifyArtifact: (artifactId: number) =>
    requestJson<any>(`${API_BASE}/artifacts/${artifactId}/verify`, {
      method: 'POST',
    }),
  listExperiments: (projectId?: number) =>
    requestJson<ExperimentData[]>(
      `${API_BASE}/experiments${projectId ? `?project_id=${projectId}` : ''}`
    ),
  createExperiment: (payload: {
    project_id: number;
    milestone_id?: number | null;
    concept_id?: number | null;
    title: string;
    hypothesis: string;
    objective: string;
    variables_changed: string[];
    procedure: string;
    expected_outcome: string;
    actual_outcome: string;
    observations: string;
    conclusion: string;
    status: string;
    metrics?: Record<string, any>;
  }) =>
    requestJson<ExperimentData>(`${API_BASE}/experiments`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  discoverResources: (query: string, freeOnly = true, includeLive = true, journeyId?: number, conceptId?: number) =>
    requestJson<ResourceDiscoveryResponse>(
      `${API_BASE}/resources/discover?query=${encodeURIComponent(
        query
      )}&free_only=${freeOnly}&include_live=${includeLive}${journeyId ? `&journey_id=${journeyId}` : ''}${
        conceptId ? `&concept_id=${conceptId}` : ''
      }`
    ),
  getKnowledgeWorkspace: () => requestJson<any>(`${API_BASE}/knowledge/workspace`),
  createNote: (payload: {
    title: string;
    content_markdown: string;
    personal_understanding: string;
    note_type: string;
    journey_id?: number | null;
    concept_id?: number | null;
    project_id?: number | null;
    tags: string[];
    unresolved_questions: string[];
  }) =>
    requestJson<any>(`${API_BASE}/notes`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  createReflection: (payload: {
    concept_id?: number | null;
    milestone_id?: number | null;
    what_built_or_learned: string;
    why_it_works: string;
    what_failed: string;
    what_surprised: string;
    what_to_change: string;
  }) =>
    requestJson<any>(`${API_BASE}/reflections`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  globalSearch: (q: string) =>
    requestJson<{ query: string; count: number; results: Array<any> }>(
      `${API_BASE}/search?q=${encodeURIComponent(q)}`
    ),
  getAiAndHardwareStatus: () => requestJson<any>(`${API_BASE}/ai/status`),
  getLiveAiStatus: () =>
    requestJson<{
      active_provider: string;
      active_model: string;
      is_local: boolean;
      online: boolean;
      model_installed: boolean;
      is_connected: boolean;
      latency_ms: number;
      status_message: string;
      installed_models: string[];
      generation_status: string;
    }>(`${API_BASE}/ai/live-status`),
  updateAiProvider: (payload: any) =>
    requestJson<any>(`${API_BASE}/ai/providers`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  listMemories: (category?: string) =>
    requestJson<any[]>(`${API_BASE}/memories${category ? `?category=${category}` : ''}`),
  upsertMemory: (payload: { memory_category: string; subject_key: string; fact_statement: string }) =>
    requestJson<any>(`${API_BASE}/memories`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteMemory: (id: number) =>
    requestJson<any>(`${API_BASE}/memories/${id}`, {
      method: 'DELETE',
    }),
  getObsidianConfig: () => requestJson<any>(`${API_BASE}/obsidian/config`),
  updateObsidianConfig: (payload: any) =>
    requestJson<any>(`${API_BASE}/obsidian/config`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  exportToObsidian: (payload: {
    export_type: 'concept' | 'project' | 'experiment' | 'think_deeper' | 'note';
    entity_id: number;
    allow_overwrite?: boolean;
  }) =>
    requestJson<any>(`${API_BASE}/obsidian/export`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getObsidianSyncPreview: () => requestJson<any>(`${API_BASE}/obsidian/sync-preview`),
  getAutomationStatus: () => requestJson<any>(`${API_BASE}/automation/status`),
  executeAutomationWorkflow: (workflowKey: string, payload?: Record<string, any>) =>
    requestJson<any>(`${API_BASE}/automation/workflows/${workflowKey}/execute`, {
      method: 'POST',
      body: JSON.stringify(payload || {}),
    }),
  listBackups: () => requestJson<any[]>(`${API_BASE}/system/backups`),
  createBackup: () =>
    requestJson<any>(`${API_BASE}/system/backups`, {
      method: 'POST',
    }),
  testAiGeneration: (payload: { prompt: string; model?: string; system_prompt?: string }) =>
    requestJson<any>(`${API_BASE}/ai/test-generate`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};
