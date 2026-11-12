export interface ConceptDependencyItem {
  id: number;
  source_concept_id: number;
  target_concept_id: number;
  dependency_type: 'essential' | 'recommended' | 'optional' | string;
  rationale: string;
}

export interface ConceptItem {
  id: number;
  journey_id: number;
  slug: string;
  title: string;
  summary: string;
  category: string;
  prerequisite_level: 'essential' | 'recommended' | 'optional' | string;
  difficulty_level: string;
  mastery_status: 'unstarted' | 'exploring' | 'practicing' | 'synthesized' | string;
  mastery_score: number;
  position_x: number;
  position_y: number;
  builder_milestone_id: number | null;
  related_disciplines: string[];
  research_directions: string[];
  dependencies: ConceptDependencyItem[];
}

export interface BlueprintData {
  id: number;
  title: string;
  objective: string;
  what_will_be_created: string;
  why_it_matters: string;
  deliverables_json: string[];
  required_knowledge_json: Array<{ name: string; level: string; category: string }>;
  proposed_architecture: string;
  major_components_json: string[];
  tools_and_tech_json: string[];
  alternative_approaches_json: string[];
  experiments_to_conduct_json: string[];
  failure_modes_json: string[];
  estimated_hours: number;
  stretch_goals_json: string[];
  is_approved: boolean;
  version: number;
}

export interface LearningTaskItem {
  id: number;
  title: string;
  task_type: string;
  road: 'scholar' | 'builder' | string;
  day_number: number;
  estimated_minutes: number;
  status: 'pending' | 'in_progress' | 'completed' | string;
  concept_id: number | null;
  milestone_id: number | null;
}

export interface JourneySummaryProject {
  id: number;
  title: string;
  domain: string;
  objective: string;
  status: string;
  current_milestone_order: number;
  next_action: string;
  milestone_count: number;
}

export interface LearningJourneyData {
  id: number;
  title: string;
  slug: string;
  user_intent: string;
  subject_domain: string;
  road_mode: 'scholar' | 'builder' | 'hybrid' | string;
  experience_level: string;
  preferred_format: string;
  daily_minutes: number;
  duration_days: number;
  existing_knowledge?: string | null;
  final_project_goal?: string | null;
  status: string;
  progress_percent: number;
  current_road: 'scholar' | 'builder' | string;
  current_concept_id: number | null;
  current_milestone_id: number | null;
  last_active_at: string | null;
  blueprint: BlueprintData | null;
  concepts: ConceptItem[];
  projects: JourneySummaryProject[];
  tasks: LearningTaskItem[];
}

export interface LessonSectionData {
  id: number;
  section_key: string;
  title: string;
  sequence_order: number;
  epistemic_label: 'CORE' | 'APPROXIMATE' | 'EXPLORATORY' | string;
  concise_content: string;
  detailed_content: string;
  research_content: string;
  mathematical_derivation: string;
  worked_example: string;
  citations: Array<{
    key: string;
    title: string;
    year: string;
    epistemic_status: string;
    url?: string;
    embed_url?: string;
    video_id?: string;
    channel?: string;
    duration?: string;
    thumbnail_url?: string;
  }>;
  is_expanded: boolean;
}

export interface LessonData {
  id: number;
  title: string;
  learning_format: string;
  current_depth: 'concise' | 'detailed' | 'research' | string;
  generation_stage: string;
  stages_completed: string[];
  problem_statement: string;
  why_it_exists: string;
  historical_context: string;
  first_principles_intuition: string;
  real_world_analogies: string;
  conceptual_explanation: string;
  formal_technical_explanation: string;
  mathematical_derivations: string;
  worked_examples: string;
  mermaid_diagram: string;
  code_examples: string;
  practical_applications: string;
  engineering_tradeoffs: string;
  common_misconceptions: string;
  limitations: string;
  connections_to_other_concepts: string;
  further_exploration: string;
  sections: LessonSectionData[];
}

export interface FeynmanFeedbackData {
  incorrect_assumptions: string[];
  missing_relationships: string[];
  logical_gaps: string[];
  memorised_jargon: string[];
  evidence_quotes: string[];
  guided_questions: string[];
  analogies_and_hints: string[];
  clarity_score: number;
}

export interface FeynmanHistoryItem {
  id: number;
  version_number: number;
  stage_reached: number;
  intuition_prompt: string;
  user_explanation: string;
  revised_explanation: string | null;
  formal_precision_notes: string;
  remaining_uncertainties: string;
  created_at: string | null;
  feedback: FeynmanFeedbackData | null;
}

export interface RecallQuestionItem {
  id: number;
  question_type: string;
  prompt: string;
  options: string[];
  reference_answer: string;
  grading_rubric: string;
  difficulty: string;
  attempts: Array<{
    id: number;
    user_response: string;
    ai_feedback: string;
    evidence_score: number;
    demonstrated_understanding: string;
  }>;
}

export interface FlashcardItem {
  id: number;
  front: string;
  back: string;
  hint: string;
  card_type: string;
  schedule: {
    interval_days: number;
    ease_factor: number;
    repetitions: number;
    stability_score: number;
    next_review_at: string | null;
    algorithm_explanation: string;
  } | null;
}

export interface ThinkDeeperQuestionItem {
  id: number;
  concept_id?: number | null;
  milestone_id?: number | null;
  question_category: string;
  prompt: string;
  why_this_question_matters?: string;
  optional_hint: string;
  socratic_guide?: string;
  model_research_discussion: string;
  responses?: Array<{
    id: number;
    user_reasoning: string;
    reasoning_analysis: string;
    identified_assumptions: string[];
    missing_perspectives: string[];
    socratic_followup_question: string;
    followup_user_reply?: string | null;
    model_discussion_unlocked: boolean;
  }>;
}

export interface ConceptWorkspaceData {
  concept: ConceptItem;
  lesson: LessonData | null;
  feynman_history: FeynmanHistoryItem[];
  recall_questions: RecallQuestionItem[];
  flashcards: FlashcardItem[];
  think_deeper_questions: ThinkDeeperQuestionItem[];
}

export interface ProjectMilestoneData {
  id: number;
  concept_id: number | null;
  sequence_order: number;
  title: string;
  mission: string;
  why_this_matters: string;
  prerequisites: Array<{ concept_id: number; title: string; level: string }>;
  architecture_design: string;
  architecture_diagram: string;
  pseudocode: string;
  interface_definitions: string;
  tradeoff_comparisons: string;
  step_by_step_guide: string;
  code_explanation: string;
  basic_tests: string[];
  edge_cases: string[];
  failure_scenarios: string[];
  debugging_steps: string[];
  experimentation_prompts: string[];
  break_it_challenges: string[];
  deliverable_description: string;
  reflection_prompts: string[];
  unlocked_hint_level: number;
  hints: Array<{ level: number; title: string; content: string }>;
  status: 'locked' | 'active' | 'completed' | string;
  tasks: Array<{
    id: number;
    title: string;
    file_target: string;
    description: string;
    verification_command: string;
    is_completed: boolean;
  }>;
  think_deeper_questions: ThinkDeeperQuestionItem[];
}

export interface ProjectArtifactData {
  id: number;
  milestone_id: number | null;
  file_path: string;
  language: string;
  content: string;
  previous_content: string | null;
  artifact_type: string;
  version: number;
}

export interface ProjectFullData {
  id: number;
  journey_id: number;
  title: string;
  slug: string;
  domain: string;
  objective: string;
  what_will_be_created: string;
  why_project_matters: string;
  architecture_overview: string;
  architecture_mermaid: string;
  tech_stack: string[];
  connected_local_dir: string | null;
  status: string;
  current_milestone_order: number;
  implementation_decisions: string[];
  outstanding_bugs: string[];
  failed_attempts: string[];
  outstanding_questions: string[];
  next_action: string;
  milestones: ProjectMilestoneData[];
  artifacts: ProjectArtifactData[];
}

export interface ExperimentData {
  id: number;
  project_id: number;
  milestone_id: number | null;
  concept_id: number | null;
  title: string;
  hypothesis: string;
  objective: string;
  variables_changed: string[];
  procedure: string;
  expected_outcome: string;
  actual_outcome: string;
  observations: string;
  conclusion: string;
  next_experiment_suggestion: string;
  status: string;
  ai_interpretation: string;
  created_at: string | null;
  results: Array<{
    id: number;
    run_number: number;
    label: string;
    parameters: Record<string, unknown>;
    metrics: Record<string, number | string>;
    log_output: string;
  }>;
}

export interface ResourceItem {
  id: number;
  provider_name: string;
  external_id: string;
  title: string;
  url: string;
  resource_type: string;
  authors: string[];
  published_date: string;
  access_status:
    | 'Completely free'
    | 'Free audit'
    | 'Free learning, paid certificate'
    | 'Free preview only'
    | 'Paid'
    | 'Unverified'
    | string;
  license_info: string;
  description: string;
  relevance_explanation: string;
  credibility_score: number;
  relevance_score: number;
  difficulty_level: string;
  stars_or_citations: number;
  language: string;
  duration_or_length: string;
  thumbnail_url: string;
  last_verified_at: string | null;
}

export interface ResourceDiscoveryResponse {
  query: string;
  free_only_applied: boolean;
  total_count: number;
  primary_resource: ResourceItem | null;
  supplementary_resources: ResourceItem[];
  practical_repository: ResourceItem | null;
  explore_more: ResourceItem[];
  all_resources: ResourceItem[];
}
