from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), default="Principal Researcher")
    bio: Mapped[str] = mapped_column(Text, default="First-principles learner, researcher, and builder.")
    experience_level: Mapped[str] = mapped_column(String(40), default="intermediate")
    preferred_format: Mapped[str] = mapped_column(String(50), default="combined")
    daily_minutes_goal: Mapped[int] = mapped_column(Integer, default=45)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    current_level: Mapped[int] = mapped_column(Integer, default=1)
    exploration_rank: Mapped[str] = mapped_column(String(80), default="First-Principles Explorer")
    active_days_count: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    settings: Mapped[Optional["UserSettings"]] = relationship(
        "UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    journeys: Mapped[List["LearningJourney"]] = relationship(
        "LearningJourney", back_populates="user", cascade="all, delete-orphan"
    )
    notes: Mapped[List["Note"]] = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    memories: Mapped[List["MemoryFact"]] = relationship(
        "MemoryFact", back_populates="user", cascade="all, delete-orphan"
    )
    progress_events: Mapped[List["ProgressEvent"]] = relationship(
        "ProgressEvent", back_populates="user", cascade="all, delete-orphan"
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), unique=True)
    theme: Mapped[str] = mapped_column(String(20), default="dark")
    default_road_mode: Mapped[str] = mapped_column(String(30), default="hybrid")
    default_explanation_depth: Mapped[str] = mapped_column(String(30), default="detailed")
    allow_cloud_ai: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_cloud_notes_egress: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_cloud_code_egress: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_local_code_execution: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_optional_streaks: Mapped[bool] = mapped_column(Boolean, default=True)
    free_resources_only_default: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="settings")


class LearningJourney(Base):
    __tablename__ = "learning_journeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_intent: Mapped[str] = mapped_column(Text, nullable=False)
    subject_domain: Mapped[str] = mapped_column(String(120), default="Computer Science & Engineering")
    road_mode: Mapped[str] = mapped_column(String(30), default="hybrid")  # scholar | builder | hybrid
    experience_level: Mapped[str] = mapped_column(String(40), default="beginner")
    preferred_format: Mapped[str] = mapped_column(String(50), default="combined")
    daily_minutes: Mapped[int] = mapped_column(Integer, default=30)
    duration_days: Mapped[int] = mapped_column(Integer, default=30)
    existing_knowledge: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    final_project_goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    intake_profile_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="active")
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
    current_road: Mapped[str] = mapped_column(String(30), default="scholar")
    current_concept_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_milestone_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="journeys")
    blueprint: Mapped[Optional["LearningBlueprint"]] = relationship(
        "LearningBlueprint", back_populates="journey", uselist=False, cascade="all, delete-orphan"
    )
    roads: Mapped[List["LearningRoad"]] = relationship(
        "LearningRoad", back_populates="journey", cascade="all, delete-orphan"
    )
    concepts: Mapped[List["Concept"]] = relationship(
        "Concept", back_populates="journey", cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="journey", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["LearningSession"]] = relationship(
        "LearningSession", back_populates="journey", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["LearningTask"]] = relationship(
        "LearningTask", back_populates="journey", cascade="all, delete-orphan"
    )
    days: Mapped[List["LearningDay"]] = relationship(
        "LearningDay", back_populates="journey", cascade="all, delete-orphan", order_by="LearningDay.day_number"
    )
    generation_jobs: Mapped[List["GenerationJob"]] = relationship(
        "GenerationJob", back_populates="journey", cascade="all, delete-orphan"
    )


class LearningBlueprint(Base):
    __tablename__ = "learning_blueprints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    journey_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_journeys.id", ondelete="CASCADE"), unique=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    what_will_be_created: Mapped[str] = mapped_column(Text, default="")
    why_it_matters: Mapped[str] = mapped_column(Text, default="")
    deliverables_json: Mapped[list] = mapped_column(JSON, default=list)
    required_knowledge_json: Mapped[list] = mapped_column(JSON, default=list)
    proposed_architecture: Mapped[str] = mapped_column(Text, default="")
    major_components_json: Mapped[list] = mapped_column(JSON, default=list)
    tools_and_tech_json: Mapped[list] = mapped_column(JSON, default=list)
    alternative_approaches_json: Mapped[list] = mapped_column(JSON, default=list)
    experiments_to_conduct_json: Mapped[list] = mapped_column(JSON, default=list)
    failure_modes_json: Mapped[list] = mapped_column(JSON, default=list)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=20)
    stretch_goals_json: Mapped[list] = mapped_column(JSON, default=list)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    journey: Mapped["LearningJourney"] = relationship("LearningJourney", back_populates="blueprint")


class LearningRoad(Base):
    __tablename__ = "learning_roads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    journey_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_journeys.id", ondelete="CASCADE"), index=True
    )
    road_type: Mapped[str] = mapped_column(String(30), nullable=False)  # scholar | builder
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    sequence_order: Mapped[int] = mapped_column(Integer, default=1)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)

    journey: Mapped["LearningJourney"] = relationship("LearningJourney", back_populates="roads")
    modules: Mapped[List["LearningModule"]] = relationship(
        "LearningModule", back_populates="road", cascade="all, delete-orphan"
    )


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    journey_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_journeys.id", ondelete="CASCADE"), index=True
    )
    slug: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(
        String(60), default="foundational"
    )  # foundational | prerequisite | mathematical | terminology | intermediate | advanced | related | research_direction
    prerequisite_level: Mapped[str] = mapped_column(
        String(30), default="essential"
    )  # essential | recommended | optional
    difficulty_level: Mapped[str] = mapped_column(String(30), default="intermediate")
    mastery_status: Mapped[str] = mapped_column(
        String(40), default="unstarted"
    )  # unstarted | exploring | practicing | synthesized
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
    position_x: Mapped[float] = mapped_column(Float, default=100.0)
    position_y: Mapped[float] = mapped_column(Float, default=100.0)
    builder_milestone_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    related_disciplines_json: Mapped[list] = mapped_column(JSON, default=list)
    research_directions_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    journey: Mapped["LearningJourney"] = relationship("LearningJourney", back_populates="concepts")
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson", back_populates="concept", cascade="all, delete-orphan"
    )
    feynman_explanations: Mapped[List["FeynmanExplanation"]] = relationship(
        "FeynmanExplanation", back_populates="concept", cascade="all, delete-orphan"
    )
    recall_questions: Mapped[List["RecallQuestion"]] = relationship(
        "RecallQuestion", back_populates="concept", cascade="all, delete-orphan"
    )
    flashcards: Mapped[List["Flashcard"]] = relationship(
        "Flashcard", back_populates="concept", cascade="all, delete-orphan"
    )
    think_deeper_questions: Mapped[List["ThinkDeeperQuestion"]] = relationship(
        "ThinkDeeperQuestion", back_populates="concept", cascade="all, delete-orphan"
    )


class ConceptDependency(Base):
    __tablename__ = "concept_dependencies"
    __table_args__ = (UniqueConstraint("source_concept_id", "target_concept_id", name="uq_concept_dep"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="CASCADE"), index=True
    )
    target_concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="CASCADE"), index=True
    )
    dependency_type: Mapped[str] = mapped_column(String(30), default="essential")  # essential | recommended | optional
    rationale: Mapped[str] = mapped_column(Text, default="")


class LearningModule(Base):
    __tablename__ = "learning_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    road_id: Mapped[int] = mapped_column(Integer, ForeignKey("learning_roads.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    sequence_order: Mapped[int] = mapped_column(Integer, default=1)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=45)
    unlock_status: Mapped[str] = mapped_column(String(30), default="unlocked")

    road: Mapped["LearningRoad"] = relationship("LearningRoad", back_populates="modules")
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson", back_populates="module", cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    module_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("learning_modules.id", ondelete="SET NULL"), nullable=True
    )
    concept_id: Mapped[int] = mapped_column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    learning_format: Mapped[str] = mapped_column(String(50), default="combined")
    current_depth: Mapped[str] = mapped_column(String(30), default="detailed")  # concise | detailed | research
    generation_stage: Mapped[str] = mapped_column(String(40), default="complete")  # complete | generating | interrupted
    stages_completed_json: Mapped[list] = mapped_column(JSON, default=list)
    problem_statement: Mapped[str] = mapped_column(Text, default="")
    why_it_exists: Mapped[str] = mapped_column(Text, default="")
    historical_context: Mapped[str] = mapped_column(Text, default="")
    first_principles_intuition: Mapped[str] = mapped_column(Text, default="")
    real_world_analogies: Mapped[str] = mapped_column(Text, default="")
    conceptual_explanation: Mapped[str] = mapped_column(Text, default="")
    formal_technical_explanation: Mapped[str] = mapped_column(Text, default="")
    mathematical_derivations: Mapped[str] = mapped_column(Text, default="")
    worked_examples: Mapped[str] = mapped_column(Text, default="")
    mermaid_diagram: Mapped[str] = mapped_column(Text, default="")
    code_examples: Mapped[str] = mapped_column(Text, default="")
    practical_applications: Mapped[str] = mapped_column(Text, default="")
    engineering_tradeoffs: Mapped[str] = mapped_column(Text, default="")
    common_misconceptions: Mapped[str] = mapped_column(Text, default="")
    limitations: Mapped[str] = mapped_column(Text, default="")
    connections_to_other_concepts: Mapped[str] = mapped_column(Text, default="")
    further_exploration: Mapped[str] = mapped_column(Text, default="")
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    module: Mapped[Optional["LearningModule"]] = relationship("LearningModule", back_populates="lessons")
    concept: Mapped["Concept"] = relationship("Concept", back_populates="lessons")
    sections: Mapped[List["LessonSection"]] = relationship(
        "LessonSection", back_populates="lesson", cascade="all, delete-orphan"
    )


class LessonSection(Base):
    __tablename__ = "lesson_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    section_key: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, default=1)
    epistemic_label: Mapped[str] = mapped_column(String(30), default="CORE")  # CORE | APPROXIMATE | EXPLORATORY
    concise_content: Mapped[str] = mapped_column(Text, default="")
    detailed_content: Mapped[str] = mapped_column(Text, default="")
    research_content: Mapped[str] = mapped_column(Text, default="")
    mathematical_derivation: Mapped[str] = mapped_column(Text, default="")
    worked_example: Mapped[str] = mapped_column(Text, default="")
    citations_json: Mapped[list] = mapped_column(JSON, default=list)
    is_expanded: Mapped[bool] = mapped_column(Boolean, default=False)

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="sections")
    citations: Mapped[List["ResearchCitation"]] = relationship(
        "ResearchCitation", back_populates="lesson_section", cascade="all, delete-orphan"
    )


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True)
    journey_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_journeys.id", ondelete="CASCADE"), index=True
    )
    active_road: Mapped[str] = mapped_column(String(30), default="scholar")
    concept_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    milestone_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    summary: Mapped[str] = mapped_column(Text, default="")
    incomplete_task: Mapped[str] = mapped_column(Text, default="")
    next_recommended_action: Mapped[str] = mapped_column(Text, default="")

    journey: Mapped["LearningJourney"] = relationship("LearningJourney", back_populates="sessions")


class LearningTask(Base):
    __tablename__ = "learning_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    journey_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_journeys.id", ondelete="CASCADE"), index=True
    )
    concept_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    milestone_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    task_type: Mapped[str] = mapped_column(
        String(40), default="study"
    )  # study | feynman | recall | think_deeper | build | experiment
    road: Mapped[str] = mapped_column(String(30), default="scholar")
    day_number: Mapped[int] = mapped_column(Integer, default=1)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(String(30), default="pending")  # pending | in_progress | completed
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    journey: Mapped["LearningJourney"] = relationship("LearningJourney", back_populates="tasks")


class FeynmanExplanation(Base):
    __tablename__ = "feynman_explanations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    concept_id: Mapped[int] = mapped_column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), default=1)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    stage_reached: Mapped[int] = mapped_column(Integer, default=2)  # Stages 1..6
    intuition_prompt: Mapped[str] = mapped_column(Text, default="")
    user_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    revised_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    formal_precision_notes: Mapped[str] = mapped_column(Text, default="")
    remaining_uncertainties: Mapped[str] = mapped_column(Text, default="")
    related_concepts_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    concept: Mapped["Concept"] = relationship("Concept", back_populates="feynman_explanations")
    feedbacks: Mapped[List["FeynmanFeedback"]] = relationship(
        "FeynmanFeedback", back_populates="explanation", cascade="all, delete-orphan"
    )


class FeynmanFeedback(Base):
    __tablename__ = "feynman_feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    explanation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("feynman_explanations.id", ondelete="CASCADE"), index=True
    )
    incorrect_assumptions_json: Mapped[list] = mapped_column(JSON, default=list)
    missing_relationships_json: Mapped[list] = mapped_column(JSON, default=list)
    logical_gaps_json: Mapped[list] = mapped_column(JSON, default=list)
    memorised_jargon_json: Mapped[list] = mapped_column(JSON, default=list)
    conceptual_confusion_json: Mapped[list] = mapped_column(JSON, default=list)
    evidence_quotes_json: Mapped[list] = mapped_column(JSON, default=list)
    guided_questions_json: Mapped[list] = mapped_column(JSON, default=list)
    analogies_and_hints_json: Mapped[list] = mapped_column(JSON, default=list)
    technical_precision_unlock: Mapped[str] = mapped_column(Text, default="")
    clarity_score: Mapped[float] = mapped_column(Float, default=0.7)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    explanation: Mapped["FeynmanExplanation"] = relationship("FeynmanExplanation", back_populates="feedbacks")


class RecallQuestion(Base):
    __tablename__ = "recall_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    concept_id: Mapped[int] = mapped_column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), index=True)
    question_type: Mapped[str] = mapped_column(
        String(50), default="free_recall"
    )  # free_recall | short_answer | concept_reconstruction | mcq | derivation | problem_solving | compare_contrast | explain_difference | practical_application
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options_json: Mapped[list] = mapped_column(JSON, default=list)
    reference_answer: Mapped[str] = mapped_column(Text, default="")
    grading_rubric: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[str] = mapped_column(String(30), default="intermediate")

    concept: Mapped["Concept"] = relationship("Concept", back_populates="recall_questions")
    attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="question", cascade="all, delete-orphan"
    )


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    concept_id: Mapped[int] = mapped_column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), index=True)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    hint: Mapped[str] = mapped_column(Text, default="")
    card_type: Mapped[str] = mapped_column(String(40), default="conceptual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    concept: Mapped["Concept"] = relationship("Concept", back_populates="flashcards")
    schedule: Mapped[Optional["ReviewSchedule"]] = relationship(
        "ReviewSchedule", back_populates="flashcard", uselist=False, cascade="all, delete-orphan"
    )


class ReviewSchedule(Base):
    __tablename__ = "review_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    flashcard_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("flashcards.id", ondelete="CASCADE"), unique=True
    )
    concept_id: Mapped[int] = mapped_column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), index=True)
    next_review_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    interval_days: Mapped[float] = mapped_column(Float, default=1.0)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    stability_score: Mapped[float] = mapped_column(Float, default=0.5)
    algorithm_explanation: Mapped[str] = mapped_column(
        Text, default="Transparent SM-2 + Multi-Evidence Stability Schedule"
    )
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_outcome: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    flashcard: Mapped["Flashcard"] = relationship("Flashcard", back_populates="schedule")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recall_questions.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), default=1)
    user_response: Mapped[str] = mapped_column(Text, nullable=False)
    ai_feedback: Mapped[str] = mapped_column(Text, default="")
    evidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    demonstrated_understanding: Mapped[str] = mapped_column(
        String(40), default="partial_evidence"
    )  # strong_multi_evidence | partial_evidence | surface_recall | needs_reconstruction
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    question: Mapped["RecallQuestion"] = relationship("RecallQuestion", back_populates="attempts")


class ThinkDeeperQuestion(Base):
    __tablename__ = "think_deeper_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    concept_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=True, index=True
    )
    milestone_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("project_milestones.id", ondelete="CASCADE"), nullable=True, index=True
    )
    question_category: Mapped[str] = mapped_column(
        String(50), default="first_principles"
    )  # first_principles | assumption_analysis | counterfactual | tradeoff | systems_thinking | failure_investigation | cross_disciplinary
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    why_this_question_matters: Mapped[str] = mapped_column(Text, default="")
    optional_hint: Mapped[str] = mapped_column(Text, default="")
    socratic_guide: Mapped[str] = mapped_column(Text, default="")
    model_research_discussion: Mapped[str] = mapped_column(Text, default="")

    concept: Mapped[Optional["Concept"]] = relationship("Concept", back_populates="think_deeper_questions")
    milestone: Mapped[Optional["ProjectMilestone"]] = relationship(
        "ProjectMilestone", back_populates="think_deeper_questions"
    )
    responses: Mapped[List["ThinkDeeperResponse"]] = relationship(
        "ThinkDeeperResponse", back_populates="question", cascade="all, delete-orphan"
    )


class ThinkDeeperResponse(Base):
    __tablename__ = "think_deeper_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("think_deeper_questions.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), default=1)
    user_reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning_analysis: Mapped[str] = mapped_column(Text, default="")
    identified_assumptions_json: Mapped[list] = mapped_column(JSON, default=list)
    missing_perspectives_json: Mapped[list] = mapped_column(JSON, default=list)
    socratic_followup_question: Mapped[str] = mapped_column(Text, default="")
    followup_user_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_discussion_unlocked: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    question: Mapped["ThinkDeeperQuestion"] = relationship("ThinkDeeperQuestion", back_populates="responses")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    journey_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_journeys.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(100), default="Systems & AI Engineering")
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    what_will_be_created: Mapped[str] = mapped_column(Text, default="")
    why_project_matters: Mapped[str] = mapped_column(Text, default="")
    architecture_overview: Mapped[str] = mapped_column(Text, default="")
    architecture_mermaid: Mapped[str] = mapped_column(Text, default="")
    tech_stack_json: Mapped[list] = mapped_column(JSON, default=list)
    connected_local_dir: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="building")  # planning | building | experimenting | completed
    current_milestone_order: Mapped[int] = mapped_column(Integer, default=1)
    implementation_decisions_json: Mapped[list] = mapped_column(JSON, default=list)
    outstanding_bugs_json: Mapped[list] = mapped_column(JSON, default=list)
    failed_attempts_json: Mapped[list] = mapped_column(JSON, default=list)
    outstanding_questions_json: Mapped[list] = mapped_column(JSON, default=list)
    next_action: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    journey: Mapped["LearningJourney"] = relationship("LearningJourney", back_populates="projects")
    milestones: Mapped[List["ProjectMilestone"]] = relationship(
        "ProjectMilestone", back_populates="project", cascade="all, delete-orphan"
    )
    artifacts: Mapped[List["ProjectArtifact"]] = relationship(
        "ProjectArtifact", back_populates="project", cascade="all, delete-orphan"
    )
    experiments: Mapped[List["Experiment"]] = relationship(
        "Experiment", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectMilestone(Base):
    __tablename__ = "project_milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    concept_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    sequence_order: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    mission: Mapped[str] = mapped_column(Text, default="")
    why_this_matters: Mapped[str] = mapped_column(Text, default="")
    prerequisites_json: Mapped[list] = mapped_column(JSON, default=list)
    architecture_design: Mapped[str] = mapped_column(Text, default="")
    architecture_diagram: Mapped[str] = mapped_column(Text, default="")
    pseudocode: Mapped[str] = mapped_column(Text, default="")
    interface_definitions: Mapped[str] = mapped_column(Text, default="")
    tradeoff_comparisons: Mapped[str] = mapped_column(Text, default="")
    step_by_step_guide: Mapped[str] = mapped_column(Text, default="")
    code_explanation: Mapped[str] = mapped_column(Text, default="")
    basic_tests_json: Mapped[list] = mapped_column(JSON, default=list)
    edge_cases_json: Mapped[list] = mapped_column(JSON, default=list)
    failure_scenarios_json: Mapped[list] = mapped_column(JSON, default=list)
    debugging_steps_json: Mapped[list] = mapped_column(JSON, default=list)
    experimentation_prompts_json: Mapped[list] = mapped_column(JSON, default=list)
    break_it_challenges_json: Mapped[list] = mapped_column(JSON, default=list)
    deliverable_description: Mapped[str] = mapped_column(Text, default="")
    reflection_prompts_json: Mapped[list] = mapped_column(JSON, default=list)
    hint_level_1_conceptual: Mapped[str] = mapped_column(Text, default="")
    hint_level_2_approach: Mapped[str] = mapped_column(Text, default="")
    hint_level_3_pseudocode: Mapped[str] = mapped_column(Text, default="")
    hint_level_4_snippet: Mapped[str] = mapped_column(Text, default="")
    hint_level_5_full: Mapped[str] = mapped_column(Text, default="")
    unlocked_hint_level: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(30), default="active")  # locked | active | completed
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="milestones")
    tasks: Mapped[List["ProjectTask"]] = relationship(
        "ProjectTask", back_populates="milestone", cascade="all, delete-orphan"
    )
    think_deeper_questions: Mapped[List["ThinkDeeperQuestion"]] = relationship(
        "ThinkDeeperQuestion", back_populates="milestone", cascade="all, delete-orphan"
    )


class ProjectTask(Base):
    __tablename__ = "project_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    milestone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project_milestones.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_target: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    verification_command: Mapped[str] = mapped_column(String(255), default="")
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    milestone: Mapped["ProjectMilestone"] = relationship("ProjectMilestone", back_populates="tasks")


class ProjectArtifact(Base):
    __tablename__ = "project_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    milestone_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("project_milestones.id", ondelete="SET NULL"), nullable=True
    )
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(40), default="python")
    content: Mapped[str] = mapped_column(Text, default="")
    previous_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    artifact_type: Mapped[str] = mapped_column(
        String(40), default="source_code"
    )  # source_code | test_suite | architecture_doc | config
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="artifacts")


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    milestone_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("project_milestones.id", ondelete="SET NULL"), nullable=True
    )
    concept_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    objective: Mapped[str] = mapped_column(Text, default="")
    variables_changed_json: Mapped[list] = mapped_column(JSON, default=list)
    procedure: Mapped[str] = mapped_column(Text, default="")
    expected_outcome: Mapped[str] = mapped_column(Text, default="")
    actual_outcome: Mapped[str] = mapped_column(Text, default="")
    observations: Mapped[str] = mapped_column(Text, default="")
    conclusion: Mapped[str] = mapped_column(Text, default="")
    next_experiment_suggestion: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(
        String(40), default="succeeded"
    )  # planned | running | succeeded | refuted | failed_instructively
    ai_interpretation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="experiments")
    results: Mapped[List["ExperimentResult"]] = relationship(
        "ExperimentResult", back_populates="experiment", cascade="all, delete-orphan"
    )


class ExperimentResult(Base):
    __tablename__ = "experiment_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    experiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiments.id", ondelete="CASCADE"), index=True
    )
    run_number: Mapped[int] = mapped_column(Integer, default=1)
    label: Mapped[str] = mapped_column(String(120), default="Baseline Run")
    parameters_json: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics_json: Mapped[dict] = mapped_column(JSON, default=dict)
    log_output: Mapped[str] = mapped_column(Text, default="")
    chart_data_json: Mapped[list] = mapped_column(JSON, default=list)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="results")


class ResourceProvider(Base):
    __tablename__ = "resource_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), default="")
    requires_api_key: Mapped[bool] = mapped_column(Boolean, default=False)
    rate_limit_remaining: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[str] = mapped_column(String(30), default="online")
    last_queried_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    resources: Mapped[List["Resource"]] = relationship("Resource", back_populates="provider")


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("resource_providers.id", ondelete="SET NULL"), nullable=True
    )
    provider_name: Mapped[str] = mapped_column(String(60), default="arxiv", index=True)
    external_id: Mapped[str] = mapped_column(String(255), default="", index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    resource_type: Mapped[str] = mapped_column(
        String(50), default="paper"
    )  # paper | repository | video | course | lecture | documentation | article | model | dataset
    authors_json: Mapped[list] = mapped_column(JSON, default=list)
    published_date: Mapped[str] = mapped_column(String(40), default="")
    access_status: Mapped[str] = mapped_column(
        String(60), default="Completely free"
    )  # Completely free | Free audit | Free learning, paid certificate | Free preview only | Paid | Unverified
    license_info: Mapped[str] = mapped_column(String(120), default="Open Access")
    description: Mapped[str] = mapped_column(Text, default="")
    relevance_explanation: Mapped[str] = mapped_column(Text, default="")
    credibility_score: Mapped[float] = mapped_column(Float, default=0.92)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.90)
    difficulty_level: Mapped[str] = mapped_column(String(40), default="intermediate")
    stars_or_citations: Mapped[int] = mapped_column(Integer, default=0)
    language: Mapped[str] = mapped_column(String(50), default="")
    duration_or_length: Mapped[str] = mapped_column(String(60), default="")
    thumbnail_url: Mapped[str] = mapped_column(String(500), default="")
    is_saved_to_library: Mapped[bool] = mapped_column(Boolean, default=True)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    provider: Mapped[Optional["ResourceProvider"]] = relationship("ResourceProvider", back_populates="resources")
    relationships: Mapped[List["ResourceRelationship"]] = relationship(
        "ResourceRelationship", back_populates="resource", cascade="all, delete-orphan"
    )


class ResourceRelationship(Base):
    __tablename__ = "resource_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), index=True)
    journey_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    concept_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    milestone_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    recommendation_tier: Mapped[str] = mapped_column(
        String(40), default="primary"
    )  # primary | supplementary | practical_repo | explore_more

    resource: Mapped["Resource"] = relationship("Resource", back_populates="relationships")


class ResearchCitation(Base):
    __tablename__ = "research_citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("resources.id", ondelete="SET NULL"), nullable=True
    )
    lesson_section_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("lesson_sections.id", ondelete="CASCADE"), nullable=True
    )
    citation_key: Mapped[str] = mapped_column(String(80), nullable=False)
    authors: Mapped[str] = mapped_column(String(255), default="")
    year: Mapped[str] = mapped_column(String(20), default="")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    venue_or_source: Mapped[str] = mapped_column(String(255), default="")
    url: Mapped[str] = mapped_column(String(1000), default="")
    doi_or_arxiv_id: Mapped[str] = mapped_column(String(120), default="")
    claim_supported: Mapped[str] = mapped_column(Text, default="")
    epistemic_status: Mapped[str] = mapped_column(String(30), default="CORE")  # CORE | APPROXIMATE | EXPLORATORY
    methodology_limitations: Mapped[str] = mapped_column(Text, default="")
    disagreement_notes: Mapped[str] = mapped_column(Text, default="")

    lesson_section: Mapped[Optional["LessonSection"]] = relationship("LessonSection", back_populates="citations")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), default=1)
    journey_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    concept_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    project_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content_markdown: Mapped[str] = mapped_column(Text, default="")
    personal_understanding: Mapped[str] = mapped_column(Text, default="")
    unresolved_questions_json: Mapped[list] = mapped_column(JSON, default=list)
    note_type: Mapped[str] = mapped_column(
        String(50), default="concept_note"
    )  # concept_note | research_summary | project_journal | question | daily_log
    obsidian_folder: Mapped[str] = mapped_column(String(120), default="02 - Concepts")
    obsidian_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="notes")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=note_tags, back_populates="notes")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    color: Mapped[str] = mapped_column(String(30), default="indigo")

    notes: Mapped[List["Note"]] = relationship("Note", secondary=note_tags, back_populates="tags")


class NoteRelationship(Base):
    __tablename__ = "note_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), index=True)
    target_note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), index=True)
    relationship_type: Mapped[str] = mapped_column(
        String(40), default="wikilink"
    )  # wikilink | related_idea | contradicts | builds_upon
    context_snippet: Mapped[str] = mapped_column(Text, default="")


class Reflection(Base):
    __tablename__ = "reflections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), default=1)
    milestone_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("project_milestones.id", ondelete="SET NULL"), nullable=True
    )
    concept_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    what_built_or_learned: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_works: Mapped[str] = mapped_column(Text, default="")
    what_failed: Mapped[str] = mapped_column(Text, default="")
    what_surprised: Mapped[str] = mapped_column(Text, default="")
    what_to_change: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MemoryFact(Base):
    __tablename__ = "memory_facts"
    __table_args__ = (Index("ix_memory_category_key", "memory_category", "subject_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), default=1)
    memory_category: Mapped[str] = mapped_column(
        String(40), nullable=False
    )  # learner | knowledge | research | project | session
    subject_key: Mapped[str] = mapped_column(String(200), nullable=False)
    fact_statement: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.95)
    source_entity_type: Mapped[str] = mapped_column(String(60), default="system")
    source_entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="memories")


class ProgressEvent(Base):
    __tablename__ = "progress_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), default=1)
    journey_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(
        String(60), nullable=False
    )  # concept_synthesized | feynman_completed | think_deeper_answered | milestone_built | experiment_logged | break_it_completed
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    road: Mapped[str] = mapped_column(String(30), default="hybrid")
    xp_awarded: Mapped[int] = mapped_column(Integer, default=50)
    badge_unlocked: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="progress_events")


class AIProviderConfig(Base):
    __tablename__ = "ai_provider_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)  # ollama | gemini
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    base_url: Mapped[str] = mapped_column(String(255), default="")
    encrypted_api_key: Mapped[str] = mapped_column(String(500), default="")
    default_model: Mapped[str] = mapped_column(String(120), default="qwen3.5:9b")
    task_routing_json: Mapped[dict] = mapped_column(JSON, default=dict)
    context_length: Mapped[int] = mapped_column(Integer, default=16384)
    temperature: Mapped[float] = mapped_column(Float, default=0.3)
    privacy_notice: Mapped[str] = mapped_column(Text, default="")
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    health_status: Mapped[str] = mapped_column(String(40), default="unknown")


class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    integration_type: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)  # obsidian | n8n
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    endpoint_url: Mapped[str] = mapped_column(String(255), default="")
    auth_token: Mapped[str] = mapped_column(String(500), default="")
    vault_name: Mapped[str] = mapped_column(String(255), default="Learning OS")
    vault_local_path: Mapped[str] = mapped_column(String(500), default="")
    approved_folders_json: Mapped[list] = mapped_column(JSON, default=list)
    read_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    write_permission: Mapped[bool] = mapped_column(Boolean, default=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status_message: Mapped[str] = mapped_column(String(255), default="Ready for local configuration")


class BackupRecord(Base):
    __tablename__ = "backup_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    backup_type: Mapped[str] = mapped_column(String(60), default="full_snapshot")
    folder_path: Mapped[str] = mapped_column(String(500), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    triggered_by: Mapped[str] = mapped_column(String(60), default="manual")
    notes_summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LearningDay(Base):
    """First-class model representing a structured day of study, practice, or milestone."""
    __tablename__ = "learning_days"
    __table_args__ = (
        UniqueConstraint("journey_id", "day_number", name="uq_journey_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    journey_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_journeys.id", ondelete="CASCADE"), index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    theme: Mapped[str] = mapped_column(String(255), default="")
    phase_name: Mapped[str] = mapped_column(String(120), default="Phase 1: Foundations")
    week_number: Mapped[int] = mapped_column(Integer, default=1)
    day_type: Mapped[str] = mapped_column(
        String(40), default="lesson"
    )  # lesson | practice | review | project | assessment | research | rest | catch_up
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=90)
    why_this_day: Mapped[str] = mapped_column(Text, default="")
    prerequisites_json: Mapped[list] = mapped_column(JSON, default=list)
    introduced_concepts_json: Mapped[list] = mapped_column(JSON, default=list)
    learning_outcomes_json: Mapped[list] = mapped_column(JSON, default=list)

    # Scholar road linkage
    scholar_concept_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    scholar_objective: Mapped[str] = mapped_column(Text, default="")
    scholar_content_markdown: Mapped[str] = mapped_column(Text, default="")
    youtube_search_query: Mapped[str] = mapped_column(String(255), default="")
    youtube_video_id: Mapped[str] = mapped_column(String(60), default="")
    youtube_video_title: Mapped[str] = mapped_column(String(255), default="")

    # Builder road linkage
    builder_lab_title: Mapped[str] = mapped_column(String(255), default="")
    builder_lab_mission: Mapped[str] = mapped_column(Text, default="")
    builder_content_markdown: Mapped[str] = mapped_column(Text, default="")
    builder_activity_type: Mapped[str] = mapped_column(String(60), default="code_lab")
    builder_starter_code: Mapped[str] = mapped_column(Text, default="")
    builder_test_cases_json: Mapped[list] = mapped_column(JSON, default=list)
    builder_hints_json: Mapped[list] = mapped_column(JSON, default=list)
    builder_rubric_json: Mapped[list] = mapped_column(JSON, default=list)

    # Assessment linkage
    assessment_json: Mapped[dict] = mapped_column(JSON, default=dict)

    # Status & Progress
    generation_status: Mapped[str] = mapped_column(String(40), default="planned")  # planned | synthesized | ready
    scholar_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    builder_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    assessment_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_score: Mapped[float] = mapped_column(Float, default=0.0)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    feynman_stage: Mapped[int] = mapped_column(Integer, default=1)
    notes_summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    journey: Mapped["LearningJourney"] = relationship("LearningJourney", back_populates="days")
    concept: Mapped[Optional["Concept"]] = relationship("Concept")


class GenerationJob(Base):
    """Durable job record for asynchronous, resilient, resumable curriculum and lesson generation."""
    __tablename__ = "generation_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    journey_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("learning_journeys.id", ondelete="CASCADE"), nullable=True, index=True
    )
    job_type: Mapped[str] = mapped_column(
        String(60), nullable=False
    )  # curriculum_master | phase_expansion | day_detail | lesson_on_demand
    status: Mapped[str] = mapped_column(
        String(40), default="pending"
    )  # pending | running | completed | failed | paused
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
    current_step: Mapped[str] = mapped_column(String(255), default="Initializing...")
    total_steps: Mapped[int] = mapped_column(Integer, default=1)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    journey: Mapped[Optional["LearningJourney"]] = relationship("LearningJourney", back_populates="generation_jobs")
