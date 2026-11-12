from __future__ import annotations

import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, rebuild_fts5_index
from app.models.domain import (
    AIProviderConfig,
    BackupRecord,
    Concept,
    ConceptDependency,
    Experiment,
    ExperimentResult,
    FeynmanExplanation,
    FeynmanFeedback,
    Flashcard,
    GenerationJob,
    IntegrationConfig,
    LearningBlueprint,
    LearningDay,
    LearningJourney,
    LearningRoad,
    LearningSession,
    LearningTask,
    Lesson,
    LessonSection,
    MemoryFact,
    Note,
    NoteRelationship,
    ProgressEvent,
    Project,
    ProjectArtifact,
    ProjectMilestone,
    ProjectTask,
    QuizAttempt,
    RecallQuestion,
    Reflection,
    Resource,
    ReviewSchedule,
    Tag,
    ThinkDeeperQuestion,
    ThinkDeeperResponse,
    UserProfile,
    UserSettings,
)
from app.providers.hardware import inspect_host_hardware
from app.providers.ollama_provider import OllamaProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.router import ProviderRouter
from app.services.ai_orchestrator import AIOrchestrationService
from app.services.curriculum_planner import CurriculumPlannerService
from app.services.n8n_connector import N8nAutomationService
from app.services.obsidian_connector import ObsidianConnectorService
from app.services.resource_discovery import ResourceIntelligenceService

router = APIRouter(prefix="/api/v1")


# ---------------------------------------------------------------------------
# Request Payload Schemas
# ---------------------------------------------------------------------------
class CreateJourneyRequest(BaseModel):
    user_intent: str
    experience_level: str = "beginner"
    daily_minutes: int = 30
    duration_days: int = 30
    target_deadline: Optional[str] = None
    road_mode: str = "hybrid"
    preferred_format: str = "combined"
    existing_knowledge: Optional[str] = None
    final_project_goal: Optional[str] = None


class SocraticTutorRequest(BaseModel):
    concept_id: Optional[int] = None
    user_message: str
    command: Optional[str] = None


class UpdateBlueprintRequest(BaseModel):
    title: Optional[str] = None
    objective: Optional[str] = None
    what_will_be_created: Optional[str] = None
    proposed_architecture: Optional[str] = None
    estimated_hours: Optional[int] = None
    deliverables_json: Optional[list[str]] = None
    stretch_goals_json: Optional[list[str]] = None
    is_approved: Optional[bool] = None


class SwitchRoadRequest(BaseModel):
    target_road: str  # scholar | builder
    concept_id: Optional[int] = None
    milestone_id: Optional[int] = None


class ExplainDepthRequest(BaseModel):
    depth_mode: str = "detailed"  # concise | detailed | research
    learning_format: str = "combined"
    use_live_llm: bool = True


class FeynmanSubmitRequest(BaseModel):
    user_explanation: str
    revised_explanation: Optional[str] = None
    remaining_uncertainties: str = ""


class FlashcardReviewRequest(BaseModel):
    outcome: str = "good"  # again | hard | good | easy


class RecallAttemptRequest(BaseModel):
    user_response: str


class ThinkDeeperSubmitRequest(BaseModel):
    user_reasoning: str
    followup_reply: Optional[str] = None


class UnlockHintRequest(BaseModel):
    level: int = 2


class UpdateArtifactRequest(BaseModel):
    content: str


class CreateExperimentRequest(BaseModel):
    project_id: int
    milestone_id: Optional[int] = None
    concept_id: Optional[int] = None
    title: str
    hypothesis: str
    objective: str = ""
    variables_changed: list[str] = Field(default_factory=list)
    procedure: str = ""
    expected_outcome: str = ""
    actual_outcome: str = ""
    observations: str = ""
    conclusion: str = ""
    next_experiment_suggestion: str = ""
    status: str = "succeeded"
    metrics: dict[str, Any] = Field(default_factory=dict)


class CreateNoteRequest(BaseModel):
    title: str
    content_markdown: str
    personal_understanding: str = ""
    note_type: str = "concept_note"
    journey_id: Optional[int] = None
    concept_id: Optional[int] = None
    project_id: Optional[int] = None
    tags: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)


class CreateReflectionRequest(BaseModel):
    concept_id: Optional[int] = None
    milestone_id: Optional[int] = None
    what_built_or_learned: str
    why_it_works: str = ""
    what_failed: str = ""
    what_surprised: str = ""
    what_to_change: str = ""


class ObsidianExportRequest(BaseModel):
    export_type: str = "note"  # concept | project | experiment | think_deeper | note
    entity_id: int
    target_vault_dir: Optional[str] = None
    allow_overwrite: bool = False


class UpdateObsidianConfigRequest(BaseModel):
    is_enabled: bool = True
    endpoint_url: Optional[str] = None
    auth_token: Optional[str] = None
    vault_name: Optional[str] = None
    vault_local_path: Optional[str] = None
    read_permission: Optional[bool] = None
    write_permission: Optional[bool] = None


class UpdateAIProviderRequest(BaseModel):
    provider_name: str  # ollama | gemini
    is_enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    default_model: Optional[str] = None
    task_routing_json: Optional[dict[str, str]] = None
    allow_cloud_ai: Optional[bool] = None


class MemoryUpsertRequest(BaseModel):
    memory_category: str = "learner"
    subject_key: str
    fact_statement: str


# ---------------------------------------------------------------------------
# Serialization Helpers
# ---------------------------------------------------------------------------
def _serialize_concept(c: Concept, db: Session) -> dict[str, Any]:
    deps = db.query(ConceptDependency).filter(ConceptDependency.source_concept_id == c.id).all()
    return {
        "id": c.id,
        "journey_id": c.journey_id,
        "slug": c.slug,
        "title": c.title,
        "summary": c.summary,
        "category": c.category,
        "prerequisite_level": c.prerequisite_level,
        "difficulty_level": c.difficulty_level,
        "mastery_status": c.mastery_status,
        "mastery_score": c.mastery_score,
        "position_x": c.position_x,
        "position_y": c.position_y,
        "builder_milestone_id": c.builder_milestone_id,
        "related_disciplines": c.related_disciplines_json or [],
        "research_directions": c.research_directions_json or [],
        "dependencies": [
            {
                "id": d.id,
                "source_concept_id": d.source_concept_id,
                "target_concept_id": d.target_concept_id,
                "dependency_type": d.dependency_type,
                "rationale": d.rationale,
            }
            for d in deps
        ],
    }


def _serialize_journey(j: LearningJourney, db: Session) -> dict[str, Any]:
    bp = j.blueprint
    concepts = [_serialize_concept(c, db) for c in j.concepts]
    projects = db.query(Project).filter(Project.journey_id == j.id).all()
    tasks = db.query(LearningTask).filter(LearningTask.journey_id == j.id).order_by(LearningTask.day_number.asc()).all()

    # Load or lazily instantiate days for backward compatibility
    days = (
        db.query(LearningDay)
        .filter(LearningDay.journey_id == j.id)
        .order_by(LearningDay.day_number.asc())
        .all()
    )
    if not days and j.concepts:
        for idx, c in enumerate(j.concepts):
            d_num = idx + 1
            new_day = LearningDay(
                journey_id=j.id,
                day_number=d_num,
                title=c.title,
                phase_name="Phase 1: Foundations",
                week_number=(d_num - 1) // 7 + 1,
                day_type="lesson",
                estimated_minutes=j.daily_minutes or 45,
                scholar_concept_id=c.id,
                scholar_objective=c.summary,
                youtube_search_query=f"{j.title} {c.title}",
                builder_lab_title=f"{c.title} — Implementation Lab",
                builder_lab_mission=f"Implement and verify {c.title} with invariant assertions.",
                builder_starter_code="",
                feynman_stage=(idx % 6) + 1,
            )
            db.add(new_day)
        db.commit()
        days = (
            db.query(LearningDay)
            .filter(LearningDay.journey_id == j.id)
            .order_by(LearningDay.day_number.asc())
            .all()
        )

    serialized_days = [
        {
            "id": d.id,
            "day_number": d.day_number,
            "title": d.title,
            "theme": d.theme,
            "phase_name": d.phase_name,
            "week_number": d.week_number,
            "day_type": d.day_type,
            "estimated_minutes": d.estimated_minutes,
            "scholar_concept_id": d.scholar_concept_id,
            "scholar_objective": d.scholar_objective,
            "youtube_search_query": d.youtube_search_query,
            "youtube_video_id": d.youtube_video_id,
            "youtube_video_title": d.youtube_video_title,
            "builder_lab_title": d.builder_lab_title,
            "builder_lab_mission": d.builder_lab_mission,
            "builder_starter_code": d.builder_starter_code,
            "builder_test_cases": d.builder_test_cases_json or [],
            "builder_hints": d.builder_hints_json or [],
            "builder_completed": d.builder_completed,
            "is_completed": d.is_completed,
            "completion_score": d.completion_score,
            "feynman_stage": d.feynman_stage,
        }
        for d in days
    ]

    return {
        "id": j.id,
        "title": j.title,
        "slug": j.slug,
        "user_intent": j.user_intent,
        "subject_domain": j.subject_domain,
        "road_mode": j.road_mode,
        "experience_level": j.experience_level,
        "preferred_format": j.preferred_format,
        "daily_minutes": j.daily_minutes,
        "duration_days": j.duration_days,
        "existing_knowledge": j.existing_knowledge,
        "final_project_goal": j.final_project_goal,
        "status": j.status,
        "progress_percent": j.progress_percent,
        "current_road": j.current_road,
        "current_concept_id": j.current_concept_id,
        "current_milestone_id": j.current_milestone_id,
        "last_active_at": j.last_active_at.isoformat() if j.last_active_at else None,
        "days": serialized_days,
        "blueprint": {
            "id": bp.id,
            "title": bp.title,
            "objective": bp.objective,
            "what_will_be_created": bp.what_will_be_created,
            "why_it_matters": bp.why_it_matters,
            "deliverables_json": bp.deliverables_json,
            "required_knowledge_json": bp.required_knowledge_json,
            "proposed_architecture": bp.proposed_architecture,
            "major_components_json": bp.major_components_json,
            "tools_and_tech_json": bp.tools_and_tech_json,
            "alternative_approaches_json": bp.alternative_approaches_json,
            "experiments_to_conduct_json": bp.experiments_to_conduct_json,
            "failure_modes_json": bp.failure_modes_json,
            "estimated_hours": bp.estimated_hours,
            "stretch_goals_json": bp.stretch_goals_json,
            "is_approved": bp.is_approved,
            "version": bp.version,
        }
        if bp
        else None,
        "concepts": concepts,
        "projects": [
            {
                "id": p.id,
                "title": p.title,
                "domain": p.domain,
                "objective": p.objective,
                "status": p.status,
                "current_milestone_order": p.current_milestone_order,
                "next_action": p.next_action,
                "milestone_count": len(p.milestones),
            }
            for p in projects
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "task_type": t.task_type,
                "road": t.road,
                "day_number": t.day_number,
                "estimated_minutes": t.estimated_minutes,
                "status": t.status,
                "concept_id": t.concept_id,
                "milestone_id": t.milestone_id,
            }
            for t in tasks
        ],
    }


# ---------------------------------------------------------------------------
# 1. Dashboard & Session Resume Endpoints
# ---------------------------------------------------------------------------
@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)) -> dict[str, Any]:
    user = db.query(UserProfile).first()
    journeys = db.query(LearningJourney).order_by(LearningJourney.last_active_at.desc()).all()
    orchestrator = AIOrchestrationService(db)
    resume = orchestrator.generate_session_resume(journeys[0].id if journeys else None)

    now = datetime.now(timezone.utc)
    due_reviews = db.query(ReviewSchedule).filter(ReviewSchedule.next_review_at <= now).count()
    recent_notes = db.query(Note).order_by(Note.updated_at.desc()).limit(4).all()
    recent_resources = db.query(Resource).order_by(Resource.last_verified_at.desc()).limit(4).all()
    events = db.query(ProgressEvent).order_by(ProgressEvent.created_at.desc()).limit(6).all()

    p_router = ProviderRouter(db)
    provider, active_model, is_local = p_router.get_active_provider()
    health = await provider.health_check()
    installed_names = [m.name for m in health.available_models]
    model_installed = (
        any(
            active_model.lower() == m.lower() or active_model.split(":")[0].lower() in m.lower()
            for m in installed_names
        )
        if is_local
        else bool(health.online)
    )
    is_connected = bool(health.online and model_installed)

    return {
        "user": {
            "id": user.id if user else 1,
            "name": user.name if user else "Principal Researcher",
            "experience_level": user.experience_level if user else "intermediate",
            "total_xp": user.total_xp if user else 0,
            "current_level": user.current_level if user else 1,
            "exploration_rank": user.exploration_rank if user else "First-Principles Explorer",
            "active_days_count": user.active_days_count if user else 1,
        },
        "ai_status": {
            "active_provider": "ollama" if is_local else "gemini",
            "active_model": active_model,
            "is_local": is_local,
            "online": bool(health.online),
            "model_installed": bool(model_installed),
            "is_connected": is_connected,
            "latency_ms": round(health.latency_ms, 1),
            "status_message": health.message,
            "source_retrieval_enabled": True,
            "generation_status": "connected" if is_connected else "disconnected",
        },
        "resume_brief": resume,
        "active_journeys": [_serialize_journey(j, db) for j in journeys],
        "due_reviews_count": due_reviews,
        "recent_notes": [
            {"id": n.id, "title": n.title, "note_type": n.note_type, "obsidian_folder": n.obsidian_folder}
            for n in recent_notes
        ],
        "recent_discoveries": [
            {
                "id": r.id,
                "title": r.title,
                "provider_name": r.provider_name,
                "resource_type": r.resource_type,
                "access_status": r.access_status,
                "url": r.url,
            }
            for r in recent_resources
        ],
        "recent_progress_events": [
            {"id": e.id, "event_type": e.event_type, "title": e.title, "road": e.road, "xp_awarded": e.xp_awarded}
            for e in events
        ],
    }


@router.get("/sessions/resume")
def get_session_resume(journey_id: Optional[int] = None, db: Session = Depends(get_db)) -> dict[str, Any]:
    return AIOrchestrationService(db).generate_session_resume(journey_id)


# ---------------------------------------------------------------------------
# 2. Journeys, Blueprints & Road Switching (Test A, Test E, OS Test)
# ---------------------------------------------------------------------------
@router.get("/journeys")
def list_journeys(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    journeys = db.query(LearningJourney).order_by(LearningJourney.last_active_at.desc()).all()
    return [_serialize_journey(j, db) for j in journeys]


@router.post("/journeys")
async def create_journey(req: CreateJourneyRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    duration_days = req.duration_days
    if req.target_deadline:
        try:
            target_dt = datetime.fromisoformat(req.target_deadline.replace("Z", "+00:00"))
            if target_dt.tzinfo is None:
                target_dt = target_dt.replace(tzinfo=timezone.utc)
            delta_days = (target_dt - datetime.now(timezone.utc)).days
            if delta_days >= 1:
                duration_days = delta_days
        except Exception:
            pass

    planner = CurriculumPlannerService(db)
    job = planner.create_generation_job(
        job_type="curriculum_master",
        total_steps=6,
        payload={"user_intent": req.user_intent, "duration_days": duration_days},
    )

    try:
        journey = await planner.plan_full_curriculum(
            user_intent=req.user_intent,
            duration_days=duration_days,
            experience_level=req.experience_level,
            daily_minutes=req.daily_minutes,
            road_mode=req.road_mode,
            existing_knowledge=req.existing_knowledge,
            final_project_goal=req.final_project_goal,
            job_id=job.id,
        )
        return _serialize_journey(journey, db)
    except Exception as exc:
        planner.update_job_progress(job.id, "Generation failed", 0, status="failed", error_message=str(exc))
        raise HTTPException(status_code=500, detail=f"Curriculum Generation Failed: {exc}")


@router.get("/journeys/{journey_id}")
def get_journey(journey_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    j = db.query(LearningJourney).filter(LearningJourney.id == journey_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Learning journey not found")
    return _serialize_journey(j, db)


@router.get("/journeys/{journey_id}/days")
def get_journey_days(journey_id: int, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    j = db.query(LearningJourney).filter(LearningJourney.id == journey_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Learning journey not found")
    serialized = _serialize_journey(j, db)
    return serialized.get("days", [])


@router.get("/journeys/{journey_id}/days/{day_number}")
async def get_journey_day_detail(
    journey_id: int,
    day_number: int,
    deep_synthesize: bool = Query(False, description="Whether to trigger on-demand deep synthesis if code/theory is not yet generated"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    day = (
        db.query(LearningDay)
        .filter(LearningDay.journey_id == journey_id, LearningDay.day_number == day_number)
        .first()
    )
    if not day:
        raise HTTPException(status_code=404, detail=f"Day {day_number} not found for Journey {journey_id}")

    if deep_synthesize and not day.builder_starter_code:
        planner = CurriculumPlannerService(db)
        try:
            await planner.synthesize_day_content_deep(journey_id=journey_id, day_number=day_number)
            db.refresh(day)
        except Exception:
            pass

    return {
        "id": day.id,
        "journey_id": day.journey_id,
        "day_number": day.day_number,
        "title": day.title,
        "theme": day.theme,
        "phase_name": day.phase_name,
        "week_number": day.week_number,
        "day_type": day.day_type,
        "estimated_minutes": day.estimated_minutes,
        "scholar_concept_id": day.scholar_concept_id,
        "scholar_objective": day.scholar_objective,
        "youtube_search_query": day.youtube_search_query,
        "youtube_video_id": day.youtube_video_id,
        "youtube_video_title": day.youtube_video_title,
        "builder_lab_title": day.builder_lab_title,
        "builder_lab_mission": day.builder_lab_mission,
        "builder_starter_code": day.builder_starter_code,
        "builder_test_cases": day.builder_test_cases_json or [],
        "builder_hints": day.builder_hints_json or [],
        "builder_completed": day.builder_completed,
        "is_completed": day.is_completed,
        "completion_score": day.completion_score,
        "feynman_stage": day.feynman_stage,
    }


@router.post("/journeys/{journey_id}/days/{day_number}/complete")
def mark_journey_day_completed(
    journey_id: int,
    day_number: int,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    day = (
        db.query(LearningDay)
        .filter(LearningDay.journey_id == journey_id, LearningDay.day_number == day_number)
        .first()
    )
    if not day:
        raise HTTPException(status_code=404, detail=f"Day {day_number} not found")

    day.is_completed = True
    day.builder_completed = True
    day.completed_at = datetime.now(timezone.utc)
    day.completion_score = 1.0

    # Update overall journey progress
    total_days = db.query(LearningDay).filter(LearningDay.journey_id == journey_id).count()
    completed_days = (
        db.query(LearningDay)
        .filter(LearningDay.journey_id == journey_id, LearningDay.is_completed == True)
        .count()
    )
    j = db.query(LearningJourney).filter(LearningJourney.id == journey_id).first()
    if j and total_days > 0:
        j.progress_percent = round((completed_days / total_days) * 100.0, 1)
        j.last_active_at = datetime.now(timezone.utc)

    # Award progress event
    user = db.query(UserProfile).first()
    user_id = user.id if user else 1
    event = ProgressEvent(
        user_id=user_id,
        journey_id=journey_id,
        event_type="day_completed",
        title=f"Completed Day {day_number}: {day.title}",
        road="hybrid",
        xp_awarded=100,
    )
    db.add(event)
    db.commit()
    return {
        "success": True,
        "day_number": day.day_number,
        "is_completed": True,
        "journey_progress_percent": j.progress_percent if j else 0.0,
    }


@router.delete("/journeys/{journey_id}")
def delete_journey(journey_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    j = db.query(LearningJourney).filter(LearningJourney.id == journey_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Learning journey not found")
    title = j.title
    # Clean up linked projects, tasks, sessions, days, and progress events
    projects = db.query(Project).filter(Project.journey_id == journey_id).all()
    for p in projects:
        db.query(Experiment).filter(Experiment.project_id == p.id).delete()
        db.query(ProjectArtifact).filter(ProjectArtifact.project_id == p.id).delete()
        db.query(ProjectMilestone).filter(ProjectMilestone.project_id == p.id).delete()
        db.delete(p)
    db.query(LearningDay).filter(LearningDay.journey_id == journey_id).delete()
    db.query(GenerationJob).filter(GenerationJob.journey_id == journey_id).delete()
    db.query(LearningTask).filter(LearningTask.journey_id == journey_id).delete()
    db.query(LearningSession).filter(LearningSession.journey_id == journey_id).delete()
    db.query(ProgressEvent).filter(ProgressEvent.journey_id == journey_id).delete()
    db.delete(j)
    db.commit()
    rebuild_fts5_index(db)
    return {"deleted": True, "journey_id": journey_id, "title": title}


@router.get("/jobs/{job_id}")
def get_generation_job_status(job_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return {
        "job_id": job.id,
        "journey_id": job.journey_id,
        "job_type": job.job_type,
        "status": job.status,
        "progress_percent": job.progress_percent,
        "current_step": job.current_step,
        "total_steps": job.total_steps,
        "completed_steps": job.completed_steps,
        "error_message": job.error_message,
        "result": job.result_json,
    }


@router.get("/web-search")
async def live_web_search_endpoint(
    query: str = Query(..., min_length=1, description="Live web search query for real-time grounding"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    svc = ResourceIntelligenceService(db)
    return await svc.search_live_web_context(query, max_items=6)


@router.post("/socratic-tutor")
async def socratic_tutor_endpoint(
    req: SocraticTutorRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    orchestrator = AIOrchestrationService(db)
    return await orchestrator.run_socratic_tutor_turn(
        concept_id=req.concept_id,
        user_message=req.user_message,
        command=req.command,
    )


@router.put("/journeys/{journey_id}/blueprint")
def update_blueprint(
    journey_id: int,
    req: UpdateBlueprintRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    bp = db.query(LearningBlueprint).filter(LearningBlueprint.journey_id == journey_id).first()
    if not bp:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    if req.title is not None:
        bp.title = req.title
    if req.objective is not None:
        bp.objective = req.objective
    if req.what_will_be_created is not None:
        bp.what_will_be_created = req.what_will_be_created
    if req.proposed_architecture is not None:
        bp.proposed_architecture = req.proposed_architecture
    if req.estimated_hours is not None:
        bp.estimated_hours = req.estimated_hours
    if req.deliverables_json is not None:
        bp.deliverables_json = req.deliverables_json
    if req.stretch_goals_json is not None:
        bp.stretch_goals_json = req.stretch_goals_json
    if req.is_approved is not None:
        bp.is_approved = req.is_approved

    bp.version += 1
    db.commit()
    j = db.query(LearningJourney).filter(LearningJourney.id == journey_id).first()
    return _serialize_journey(j, db)


@router.post("/journeys/{journey_id}/switch-road")
def switch_journey_road(
    journey_id: int,
    req: SwitchRoadRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    j = db.query(LearningJourney).filter(LearningJourney.id == journey_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Journey not found")

    j.current_road = req.target_road
    if req.concept_id is not None:
        j.current_concept_id = req.concept_id
        concept = db.query(Concept).filter(Concept.id == req.concept_id).first()
        if concept and concept.builder_milestone_id and req.milestone_id is None:
            j.current_milestone_id = concept.builder_milestone_id
    if req.milestone_id is not None:
        j.current_milestone_id = req.milestone_id
        milestone = db.query(ProjectMilestone).filter(ProjectMilestone.id == req.milestone_id).first()
        if milestone and milestone.concept_id and req.concept_id is None:
            j.current_concept_id = milestone.concept_id

    j.last_active_at = datetime.now(timezone.utc)
    db.commit()

    orchestrator = AIOrchestrationService(db)
    orchestrator.record_memory(
        category="session",
        subject_key=f"road_switch_{j.id}",
        fact_statement=(
            f"Switched to {j.current_road.upper()} road while preserving context "
            f"(concept_id={j.current_concept_id}, milestone_id={j.current_milestone_id})."
        ),
        source_type="journey",
        source_id=j.id,
    )
    return {
        "journey_id": j.id,
        "current_road": j.current_road,
        "current_concept_id": j.current_concept_id,
        "current_milestone_id": j.current_milestone_id,
        "context_preserved": True,
        "resume_state": orchestrator.generate_session_resume(j.id),
    }


@router.post("/tasks/{task_id}/toggle")
def toggle_learning_task(task_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    task = db.query(LearningTask).filter(LearningTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "completed" if task.status != "completed" else "pending"
    task.completed_at = datetime.now(timezone.utc) if task.status == "completed" else None

    journey = db.query(LearningJourney).filter(LearningJourney.id == task.journey_id).first()
    if journey:
        all_tasks = db.query(LearningTask).filter(LearningTask.journey_id == journey.id).all()
        done_tasks = [t for t in all_tasks if t.status == "completed"]
        journey.progress_percent = round((len(done_tasks) / max(1, len(all_tasks))) * 100.0, 1)
        journey.last_active_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": task.id, "status": task.status, "journey_progress_percent": journey.progress_percent if journey else 0}


# ---------------------------------------------------------------------------
# 3. Scholar Workspace, Deep Explanations, Feynman, Recall & Think Deeper
# ---------------------------------------------------------------------------
@router.get("/concepts/{concept_id}")
def get_concept_workspace(concept_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    lesson = db.query(Lesson).filter(Lesson.concept_id == concept.id).first()
    feynman_history = (
        db.query(FeynmanExplanation)
        .filter(FeynmanExplanation.concept_id == concept.id)
        .order_by(FeynmanExplanation.version_number.asc())
        .all()
    )
    recall_questions = db.query(RecallQuestion).filter(RecallQuestion.concept_id == concept.id).all()
    flashcards = db.query(Flashcard).filter(Flashcard.concept_id == concept.id).all()
    think_deeper = (
        db.query(ThinkDeeperQuestion)
        .filter(
            ThinkDeeperQuestion.concept_id == concept.id,
            ThinkDeeperQuestion.milestone_id.is_(None),
        )
        .all()
    )

    return {
        "concept": _serialize_concept(concept, db),
        "lesson": {
            "id": lesson.id,
            "title": lesson.title,
            "learning_format": lesson.learning_format,
            "current_depth": lesson.current_depth,
            "generation_stage": lesson.generation_stage,
            "stages_completed": lesson.stages_completed_json or [],
            "problem_statement": lesson.problem_statement,
            "why_it_exists": lesson.why_it_exists,
            "historical_context": lesson.historical_context,
            "first_principles_intuition": lesson.first_principles_intuition,
            "real_world_analogies": lesson.real_world_analogies,
            "conceptual_explanation": lesson.conceptual_explanation,
            "formal_technical_explanation": lesson.formal_technical_explanation,
            "mathematical_derivations": lesson.mathematical_derivations,
            "worked_examples": lesson.worked_examples,
            "mermaid_diagram": lesson.mermaid_diagram,
            "code_examples": lesson.code_examples,
            "practical_applications": lesson.practical_applications,
            "engineering_tradeoffs": lesson.engineering_tradeoffs,
            "common_misconceptions": lesson.common_misconceptions,
            "limitations": lesson.limitations,
            "connections_to_other_concepts": lesson.connections_to_other_concepts,
            "further_exploration": lesson.further_exploration,
            "sections": [
                {
                    "id": s.id,
                    "section_key": s.section_key,
                    "title": s.title,
                    "sequence_order": s.sequence_order,
                    "epistemic_label": s.epistemic_label,
                    "concise_content": s.concise_content,
                    "detailed_content": s.detailed_content,
                    "research_content": s.research_content,
                    "mathematical_derivation": s.mathematical_derivation,
                    "worked_example": s.worked_example,
                    "citations": s.citations_json or [],
                    "is_expanded": s.is_expanded,
                }
                for s in lesson.sections
            ],
        }
        if lesson
        else None,
        "feynman_history": [
            {
                "id": f.id,
                "version_number": f.version_number,
                "stage_reached": f.stage_reached,
                "intuition_prompt": f.intuition_prompt,
                "user_explanation": f.user_explanation,
                "revised_explanation": f.revised_explanation,
                "formal_precision_notes": f.formal_precision_notes,
                "remaining_uncertainties": f.remaining_uncertainties,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "feedback": {
                    "incorrect_assumptions": f.feedbacks[0].incorrect_assumptions_json,
                    "missing_relationships": f.feedbacks[0].missing_relationships_json,
                    "logical_gaps": f.feedbacks[0].logical_gaps_json,
                    "memorised_jargon": f.feedbacks[0].memorised_jargon_json,
                    "evidence_quotes": f.feedbacks[0].evidence_quotes_json,
                    "guided_questions": f.feedbacks[0].guided_questions_json,
                    "analogies_and_hints": f.feedbacks[0].analogies_and_hints_json,
                    "clarity_score": f.feedbacks[0].clarity_score,
                }
                if f.feedbacks
                else None,
            }
            for f in feynman_history
        ],
        "recall_questions": [
            {
                "id": rq.id,
                "question_type": rq.question_type,
                "prompt": rq.prompt,
                "options": rq.options_json or [],
                "reference_answer": rq.reference_answer,
                "grading_rubric": rq.grading_rubric,
                "difficulty": rq.difficulty,
                "attempts": [
                    {
                        "id": a.id,
                        "user_response": a.user_response,
                        "ai_feedback": a.ai_feedback,
                        "evidence_score": a.evidence_score,
                        "demonstrated_understanding": a.demonstrated_understanding,
                    }
                    for a in rq.attempts
                ],
            }
            for rq in recall_questions
        ],
        "flashcards": [
            {
                "id": fc.id,
                "front": fc.front,
                "back": fc.back,
                "hint": fc.hint,
                "card_type": fc.card_type,
                "schedule": {
                    "interval_days": fc.schedule.interval_days,
                    "ease_factor": fc.schedule.ease_factor,
                    "repetitions": fc.schedule.repetitions,
                    "stability_score": fc.schedule.stability_score,
                    "next_review_at": fc.schedule.next_review_at.isoformat() if fc.schedule.next_review_at else None,
                    "algorithm_explanation": fc.schedule.algorithm_explanation,
                }
                if fc.schedule
                else None,
            }
            for fc in flashcards
        ],
        "think_deeper_questions": [
            {
                "id": td.id,
                "question_category": td.question_category,
                "prompt": td.prompt,
                "why_this_question_matters": td.why_this_question_matters,
                "optional_hint": td.optional_hint,
                "socratic_guide": td.socratic_guide,
                "model_research_discussion": td.model_research_discussion,
                "responses": [
                    {
                        "id": r.id,
                        "user_reasoning": r.user_reasoning,
                        "reasoning_analysis": r.reasoning_analysis,
                        "identified_assumptions": r.identified_assumptions_json,
                        "missing_perspectives": r.missing_perspectives_json,
                        "socratic_followup_question": r.socratic_followup_question,
                        "followup_user_reply": r.followup_user_reply,
                        "model_discussion_unlocked": r.model_discussion_unlocked,
                    }
                    for r in td.responses
                ],
            }
            for td in think_deeper
        ],
    }


@router.post("/concepts/{concept_id}/explain")
async def change_explanation_depth(
    concept_id: int,
    req: ExplainDepthRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    orchestrator = AIOrchestrationService(db)
    await orchestrator.generate_or_update_deep_explanation(
        concept_id=concept_id,
        depth_mode=req.depth_mode,
        learning_format=req.learning_format,
        use_live_llm=req.use_live_llm,
    )
    return get_concept_workspace(concept_id, db)


@router.post("/concepts/{concept_id}/feynman")
async def submit_feynman(
    concept_id: int,
    req: FeynmanSubmitRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    orchestrator = AIOrchestrationService(db)
    res = await orchestrator.submit_feynman_explanation(
        concept_id=concept_id,
        user_explanation=req.user_explanation,
        revised_explanation=req.revised_explanation,
        remaining_uncertainties=req.remaining_uncertainties,
    )
    exp = res["explanation"]
    fb = res["feedback"]
    return {
        "id": exp.id,
        "version_number": exp.version_number,
        "stage_reached": exp.stage_reached,
        "user_explanation": exp.user_explanation,
        "revised_explanation": exp.revised_explanation,
        "formal_precision_notes": exp.formal_precision_notes,
        "feedback": {
            "incorrect_assumptions": fb.incorrect_assumptions_json,
            "missing_relationships": fb.missing_relationships_json,
            "logical_gaps": fb.logical_gaps_json,
            "memorised_jargon": fb.memorised_jargon_json,
            "evidence_quotes": fb.evidence_quotes_json,
            "guided_questions": fb.guided_questions_json,
            "analogies_and_hints": fb.analogies_and_hints_json,
            "clarity_score": fb.clarity_score,
        },
        "history_count": res["history_count"],
    }


@router.post("/recall/flashcards/{flashcard_id}/review")
def review_flashcard_endpoint(
    flashcard_id: int,
    req: FlashcardReviewRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    sched = AIOrchestrationService(db).review_flashcard(flashcard_id, req.outcome)
    return {
        "flashcard_id": sched.flashcard_id,
        "interval_days": sched.interval_days,
        "ease_factor": sched.ease_factor,
        "repetitions": sched.repetitions,
        "stability_score": sched.stability_score,
        "next_review_at": sched.next_review_at.isoformat(),
        "algorithm_explanation": sched.algorithm_explanation,
    }


@router.post("/recall/questions/{question_id}/attempt")
def attempt_recall_question(
    question_id: int,
    req: RecallAttemptRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    att = AIOrchestrationService(db).submit_recall_attempt(question_id, req.user_response)
    return {
        "id": att.id,
        "question_id": att.question_id,
        "user_response": att.user_response,
        "ai_feedback": att.ai_feedback,
        "evidence_score": att.evidence_score,
        "demonstrated_understanding": att.demonstrated_understanding,
    }


@router.get("/think-deeper")
def list_all_think_deeper(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    questions = db.query(ThinkDeeperQuestion).all()
    return [
        {
            "id": q.id,
            "concept_id": q.concept_id,
            "milestone_id": q.milestone_id,
            "question_category": q.question_category,
            "prompt": q.prompt,
            "why_this_question_matters": q.why_this_question_matters,
            "optional_hint": q.optional_hint,
            "socratic_guide": q.socratic_guide,
            "model_research_discussion": q.model_research_discussion,
            "responses": [
                {
                    "id": r.id,
                    "user_reasoning": r.user_reasoning,
                    "reasoning_analysis": r.reasoning_analysis,
                    "identified_assumptions": r.identified_assumptions_json,
                    "missing_perspectives": r.missing_perspectives_json,
                    "socratic_followup_question": r.socratic_followup_question,
                    "followup_user_reply": r.followup_user_reply,
                    "model_discussion_unlocked": r.model_discussion_unlocked,
                }
                for r in q.responses
            ],
        }
        for q in questions
    ]


@router.post("/think-deeper/{question_id}/respond")
async def respond_think_deeper(
    question_id: int,
    req: ThinkDeeperSubmitRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    res = await AIOrchestrationService(db).submit_think_deeper_response(
        question_id=question_id,
        user_reasoning=req.user_reasoning,
        followup_reply=req.followup_reply,
    )
    r = res["response"]
    return {
        "id": r.id,
        "question_id": r.question_id,
        "user_reasoning": r.user_reasoning,
        "reasoning_analysis": r.reasoning_analysis,
        "identified_assumptions": r.identified_assumptions_json,
        "missing_perspectives": r.missing_perspectives_json,
        "socratic_followup_question": r.socratic_followup_question,
        "followup_user_reply": r.followup_user_reply,
        "model_discussion_unlocked": r.model_discussion_unlocked,
        "model_research_discussion": res["model_research_discussion"],
    }


# ---------------------------------------------------------------------------
# 4. Builder Workspace, Projects, Milestones, Artifacts & Verification
# ---------------------------------------------------------------------------
def _serialize_project(p: Project) -> dict[str, Any]:
    return {
        "id": p.id,
        "journey_id": p.journey_id,
        "title": p.title,
        "slug": p.slug,
        "domain": p.domain,
        "objective": p.objective,
        "what_will_be_created": p.what_will_be_created,
        "why_project_matters": p.why_project_matters,
        "architecture_overview": p.architecture_overview,
        "architecture_mermaid": p.architecture_mermaid,
        "tech_stack": p.tech_stack_json or [],
        "connected_local_dir": p.connected_local_dir,
        "status": p.status,
        "current_milestone_order": p.current_milestone_order,
        "implementation_decisions": p.implementation_decisions_json or [],
        "outstanding_bugs": p.outstanding_bugs_json or [],
        "failed_attempts": p.failed_attempts_json or [],
        "outstanding_questions": p.outstanding_questions_json or [],
        "next_action": p.next_action,
        "milestones": [
            {
                "id": m.id,
                "concept_id": m.concept_id,
                "sequence_order": m.sequence_order,
                "title": m.title,
                "mission": m.mission,
                "why_this_matters": m.why_this_matters,
                "prerequisites": m.prerequisites_json or [],
                "architecture_design": m.architecture_design,
                "architecture_diagram": m.architecture_diagram,
                "pseudocode": m.pseudocode,
                "interface_definitions": m.interface_definitions,
                "tradeoff_comparisons": m.tradeoff_comparisons,
                "step_by_step_guide": m.step_by_step_guide,
                "code_explanation": m.code_explanation,
                "basic_tests": m.basic_tests_json or [],
                "edge_cases": m.edge_cases_json or [],
                "failure_scenarios": m.failure_scenarios_json or [],
                "debugging_steps": m.debugging_steps_json or [],
                "experimentation_prompts": m.experimentation_prompts_json or [],
                "break_it_challenges": m.break_it_challenges_json or [],
                "deliverable_description": m.deliverable_description,
                "reflection_prompts": m.reflection_prompts_json or [],
                "unlocked_hint_level": m.unlocked_hint_level,
                "hints": [
                    {"level": 1, "title": "Level 1 — Conceptual Hint", "content": m.hint_level_1_conceptual},
                    {"level": 2, "title": "Level 2 — Approach", "content": m.hint_level_2_approach},
                    {"level": 3, "title": "Level 3 — Pseudocode", "content": m.hint_level_3_pseudocode},
                    {"level": 4, "title": "Level 4 — Illustrative Snippet", "content": m.hint_level_4_snippet},
                    {"level": 5, "title": "Level 5 — Guided Full Implementation", "content": m.hint_level_5_full},
                ][: m.unlocked_hint_level],
                "status": m.status,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "file_target": t.file_target,
                        "description": t.description,
                        "verification_command": t.verification_command,
                        "is_completed": t.is_completed,
                    }
                    for t in m.tasks
                ],
                "think_deeper_questions": [
                    {
                        "id": td.id,
                        "question_category": td.question_category,
                        "prompt": td.prompt,
                        "optional_hint": td.optional_hint,
                        "model_research_discussion": td.model_research_discussion,
                    }
                    for td in m.think_deeper_questions
                ],
            }
            for m in sorted(p.milestones, key=lambda x: x.sequence_order)
        ],
        "artifacts": [
            {
                "id": a.id,
                "milestone_id": a.milestone_id,
                "file_path": a.file_path,
                "language": a.language,
                "content": a.content,
                "previous_content": a.previous_content,
                "artifact_type": a.artifact_type,
                "version": a.version,
            }
            for a in p.artifacts
        ],
    }


@router.get("/projects")
def list_projects(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    projects = db.query(Project).order_by(Project.updated_at.desc()).all()
    return [_serialize_project(p) for p in projects]


@router.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return _serialize_project(p)


@router.post("/milestones/{milestone_id}/hints")
def unlock_milestone_hint(
    milestone_id: int,
    req: UnlockHintRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return AIOrchestrationService(db).unlock_progressive_hint(milestone_id, req.level)


@router.post("/milestones/{milestone_id}/complete")
def complete_milestone(milestone_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    m = db.query(ProjectMilestone).filter(ProjectMilestone.id == milestone_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Milestone not found")
    m.status = "completed"
    m.completed_at = datetime.now(timezone.utc)
    for t in m.tasks:
        t.is_completed = True

    proj = db.query(Project).filter(Project.id == m.project_id).first()
    if proj:
        next_m = (
            db.query(ProjectMilestone)
            .filter(
                ProjectMilestone.project_id == proj.id,
                ProjectMilestone.sequence_order == m.sequence_order + 1,
            )
            .first()
        )
        if next_m:
            next_m.status = "active"
            proj.current_milestone_order = next_m.sequence_order
            proj.next_action = f"Implement Milestone {next_m.sequence_order}: {next_m.title}"
        else:
            proj.status = "completed"
            proj.next_action = "All milestones completed! Conduct further experiments or export to Obsidian."

    AIOrchestrationService(db).record_progress_event(
        journey_id=proj.journey_id if proj else None,
        event_type="milestone_built",
        title=f"Completed Builder Milestone: {m.title}",
        road="builder",
        xp=100,
    )
    db.commit()
    return _serialize_project(proj) if proj else {"status": "completed"}


@router.put("/artifacts/{artifact_id}")
def update_project_artifact(
    artifact_id: int,
    req: UpdateArtifactRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    art = db.query(ProjectArtifact).filter(ProjectArtifact.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
    art.previous_content = art.content
    art.content = req.content
    art.version += 1
    db.commit()
    db.refresh(art)
    return {
        "id": art.id,
        "file_path": art.file_path,
        "content": art.content,
        "previous_content": art.previous_content,
        "version": art.version,
    }


@router.post("/artifacts/{artifact_id}/verify")
def verify_project_artifact(artifact_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Run controlled, user-approved local syntax and execution verification in an isolated sandbox.
    
    Zero in-process exec() fallback. Clean environment and strict 5-second process timeout.
    """
    from app.services.code_execution import CodeExecutionService

    art = db.query(ProjectArtifact).filter(ProjectArtifact.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")

    res = CodeExecutionService.execute_python_code(
        code=art.content,
        timeout=5.0,
        entry_file_name=f"artifact_{art.id}.py",
    )

    return {
        "artifact_id": art.id,
        "file_path": art.file_path,
        "passed": res.success,
        "exit_code": res.exit_code if res.exit_code is not None else (0 if res.success else 1),
        "output": res.output or ("[PASS] Script executed cleanly with exit code 0." if res.success else "Execution failed."),
        "timed_out": res.timed_out,
        "syntax_error": res.syntax_error,
        "manual_run_command": res.manual_run_command,
        "security_note": "Executed in ephemeral isolated sandbox with sanitized environment and 5-second timeout.",
    }


# ---------------------------------------------------------------------------
# 5. Experiment Lab Endpoints
# ---------------------------------------------------------------------------
@router.get("/experiments")
def list_experiments(project_id: Optional[int] = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = db.query(Experiment)
    if project_id:
        query = query.filter(Experiment.project_id == project_id)
    exps = query.order_by(Experiment.created_at.desc()).all()
    return [
        {
            "id": e.id,
            "project_id": e.project_id,
            "milestone_id": e.milestone_id,
            "concept_id": e.concept_id,
            "title": e.title,
            "hypothesis": e.hypothesis,
            "objective": e.objective,
            "variables_changed": e.variables_changed_json or [],
            "procedure": e.procedure,
            "expected_outcome": e.expected_outcome,
            "actual_outcome": e.actual_outcome,
            "observations": e.observations,
            "conclusion": e.conclusion,
            "next_experiment_suggestion": e.next_experiment_suggestion,
            "status": e.status,
            "ai_interpretation": e.ai_interpretation,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "results": [
                {
                    "id": r.id,
                    "run_number": r.run_number,
                    "label": r.label,
                    "parameters": r.parameters_json or {},
                    "metrics": r.metrics_json or {},
                    "log_output": r.log_output,
                }
                for r in e.results
            ],
        }
        for e in exps
    ]


@router.post("/experiments")
def create_experiment(req: CreateExperimentRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    exp = Experiment(
        project_id=req.project_id,
        milestone_id=req.milestone_id,
        concept_id=req.concept_id,
        title=req.title,
        hypothesis=req.hypothesis,
        objective=req.objective,
        variables_changed_json=req.variables_changed,
        procedure=req.procedure,
        expected_outcome=req.expected_outcome,
        actual_outcome=req.actual_outcome,
        observations=req.observations,
        conclusion=req.conclusion,
        next_experiment_suggestion=req.next_experiment_suggestion
        or "Test boundary sensitivity by varying one variable at a time while holding others constant.",
        status=req.status,
        ai_interpretation=(
            "Experiment Analyst Note: Your comparison between expected and actual outcomes is recorded. "
            "Remember that empirical correlation across finite runs does not prove universal causation—verify invariants on edge cases."
        ),
    )
    db.add(exp)
    db.flush()

    db.add(
        ExperimentResult(
            experiment_id=exp.id,
            run_number=1,
            label="Primary Experimental Run",
            parameters_json={"variables": req.variables_changed},
            metrics_json=req.metrics or {"stability": 0.95, "latency_ms": 5.4},
            log_output=req.actual_outcome or "Recorded experimental run.",
        )
    )
    orchestrator = AIOrchestrationService(db)
    orchestrator.record_memory(
        category="project",
        subject_key=f"experiment_{exp.id}",
        fact_statement=f"Conducted experiment '{exp.title}' (Status: {exp.status}). Conclusion: {exp.conclusion}",
        source_type="experiment",
        source_id=exp.id,
    )
    orchestrator.record_progress_event(
        journey_id=None,
        event_type="experiment_logged",
        title=f"Logged Experiment: {exp.title}",
        road="builder",
        xp=70,
    )
    db.commit()
    rebuild_fts5_index(db)
    return list_experiments(req.project_id, db)[0]


# ---------------------------------------------------------------------------
# 6. Resource Intelligence Engine (Test F)
# ---------------------------------------------------------------------------
def _serialize_resource(r: Resource) -> dict[str, Any]:
    return {
        "id": r.id,
        "provider_name": r.provider_name,
        "external_id": r.external_id,
        "title": r.title,
        "url": r.url,
        "resource_type": r.resource_type,
        "authors": r.authors_json or [],
        "published_date": r.published_date,
        "access_status": r.access_status,
        "license_info": r.license_info,
        "description": r.description,
        "relevance_explanation": r.relevance_explanation,
        "credibility_score": r.credibility_score,
        "relevance_score": r.relevance_score,
        "difficulty_level": r.difficulty_level,
        "stars_or_citations": r.stars_or_citations,
        "language": r.language,
        "duration_or_length": r.duration_or_length,
        "thumbnail_url": r.thumbnail_url,
        "is_saved_to_library": r.is_saved_to_library,
        "last_verified_at": r.last_verified_at.isoformat() if r.last_verified_at else None,
    }


@router.get("/resources/discover")
async def discover_resources_endpoint(
    query: str = Query(..., description="Technical subject or project query"),
    free_only: bool = Query(True, description="Filter to genuinely free learning resources by default"),
    include_live: bool = Query(True, description="Query live public APIs (arXiv, OpenAlex, GitHub, HuggingFace)"),
    journey_id: Optional[int] = None,
    concept_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    svc = ResourceIntelligenceService(db)
    res = await svc.discover_resources(
        query=query,
        free_only=free_only,
        include_live_providers=include_live,
        journey_id=journey_id,
        concept_id=concept_id,
    )
    rebuild_fts5_index(db)
    return {
        "query": res["query"],
        "free_only_applied": res["free_only_applied"],
        "total_count": res["total_count"],
        "primary_resource": _serialize_resource(res["primary_resource"]) if res["primary_resource"] else None,
        "supplementary_resources": [_serialize_resource(r) for r in res["supplementary_resources"]],
        "practical_repository": _serialize_resource(res["practical_repository"]) if res["practical_repository"] else None,
        "explore_more": [_serialize_resource(r) for r in res["explore_more"]],
        "all_resources": [_serialize_resource(r) for r in res["all_resources"]],
    }


@router.get("/resources")
def list_saved_resources(
    saved_only: bool = Query(False, description="Filter strictly to saved resources"),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    query = db.query(Resource)
    if saved_only:
        query = query.filter(Resource.is_saved_to_library == True)
    resources = query.order_by(Resource.relevance_score.desc()).all()
    return [_serialize_resource(r) for r in resources]


@router.post("/resources/{resource_id}/toggle_save")
def toggle_save_resource(resource_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")
    res.is_saved_to_library = not res.is_saved_to_library
    db.commit()
    db.refresh(res)
    return {"saved": res.is_saved_to_library, "resource": _serialize_resource(res)}


# ---------------------------------------------------------------------------
# 7. Personal Knowledge Workspace, Notes, Reflections & FTS5 Search
# ---------------------------------------------------------------------------
@router.get("/knowledge/workspace")
def get_personal_knowledge_workspace(db: Session = Depends(get_db)) -> dict[str, Any]:
    notes = db.query(Note).order_by(Note.updated_at.desc()).all()
    note_rels = db.query(NoteRelationship).all()
    resources = db.query(Resource).order_by(Resource.credibility_score.desc()).all()
    projects = db.query(Project).all()
    experiments = db.query(Experiment).order_by(Experiment.created_at.desc()).all()
    reflections = db.query(Reflection).order_by(Reflection.created_at.desc()).all()
    feynman_items = db.query(FeynmanExplanation).order_by(FeynmanExplanation.created_at.desc()).all()
    sessions = db.query(LearningSession).order_by(LearningSession.started_at.desc()).all()

    unresolved_questions: list[dict[str, Any]] = []
    for n in notes:
        for q_str in n.unresolved_questions_json or []:
            unresolved_questions.append({"source": f"Note: {n.title}", "question": q_str})
    for p in projects:
        for q_str in p.outstanding_questions_json or []:
            unresolved_questions.append({"source": f"Project: {p.title}", "question": q_str})

    return {
        "my_knowledge_notes": [
            {
                "id": n.id,
                "title": n.title,
                "slug": n.slug,
                "content_markdown": n.content_markdown,
                "personal_understanding": n.personal_understanding,
                "unresolved_questions": n.unresolved_questions_json or [],
                "note_type": n.note_type,
                "obsidian_folder": n.obsidian_folder,
                "tags": [t.name for t in n.tags],
                "updated_at": n.updated_at.isoformat() if n.updated_at else None,
            }
            for n in notes
        ],
        "backlinks": [
            {
                "id": nr.id,
                "source_note_id": nr.source_note_id,
                "target_note_id": nr.target_note_id,
                "relationship_type": nr.relationship_type,
                "context_snippet": nr.context_snippet,
            }
            for nr in note_rels
        ],
        "my_library": [_serialize_resource(r) for r in resources],
        "my_projects": [_serialize_project(p) for p in projects],
        "my_experiments": list_experiments(None, db),
        "my_questions": unresolved_questions,
        "my_learning_history": {
            "sessions": [
                {
                    "id": s.id,
                    "journey_id": s.journey_id,
                    "active_road": s.active_road,
                    "duration_minutes": s.duration_minutes,
                    "summary": s.summary,
                    "next_recommended_action": s.next_recommended_action,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                }
                for s in sessions
            ],
            "reflections": [
                {
                    "id": ref.id,
                    "what_built_or_learned": ref.what_built_or_learned,
                    "why_it_works": ref.why_it_works,
                    "what_failed": ref.what_failed,
                    "what_surprised": ref.what_surprised,
                    "what_to_change": ref.what_to_change,
                    "created_at": ref.created_at.isoformat() if ref.created_at else None,
                }
                for ref in reflections
            ],
            "feynman_count": len(feynman_items),
        },
    }


@router.post("/notes")
def create_note(req: CreateNoteRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    slug = req.title.lower().replace(" ", "-")[:100]
    note = Note(
        user_id=1,
        journey_id=req.journey_id,
        concept_id=req.concept_id,
        project_id=req.project_id,
        title=req.title,
        slug=slug,
        content_markdown=req.content_markdown,
        personal_understanding=req.personal_understanding,
        unresolved_questions_json=req.unresolved_questions,
        note_type=req.note_type,
    )
    for t_name in req.tags:
        clean_t = t_name.strip().lower()
        if not clean_t:
            continue
        tag = db.query(Tag).filter(Tag.name == clean_t).first()
        if not tag:
            tag = Tag(name=clean_t, color="indigo")
            db.add(tag)
            db.flush()
        note.tags.append(tag)

    db.add(note)
    db.commit()
    db.refresh(note)
    rebuild_fts5_index(db)
    return {
        "id": note.id,
        "title": note.title,
        "slug": note.slug,
        "content_markdown": note.content_markdown,
        "personal_understanding": note.personal_understanding,
        "note_type": note.note_type,
        "tags": [t.name for t in note.tags],
    }


@router.post("/reflections")
def create_reflection(req: CreateReflectionRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    ref = Reflection(
        user_id=1,
        concept_id=req.concept_id,
        milestone_id=req.milestone_id,
        what_built_or_learned=req.what_built_or_learned,
        why_it_works=req.why_it_works,
        what_failed=req.what_failed,
        what_surprised=req.what_surprised,
        what_to_change=req.what_to_change,
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return {"id": ref.id, "what_built_or_learned": ref.what_built_or_learned}


@router.get("/search")
def global_fts5_search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)) -> dict[str, Any]:
    rebuild_fts5_index(db)
    safe_tokens = [re.sub(r"[^a-zA-Z0-9]", "", tok) for tok in q.split() if re.sub(r"[^a-zA-Z0-9]", "", tok)]
    results: list[dict[str, Any]] = []
    if safe_tokens and settings.DATABASE_URL.startswith("sqlite"):
        fts_query = " OR ".join(f"{tok}*" for tok in safe_tokens)
        rows = db.execute(
            text(
                """
                SELECT entity_type, entity_id, journey_id, title, subtitle, snippet(fts_search_index, 5, '[', ']', '...', 24)
                FROM fts_search_index
                WHERE fts_search_index MATCH :q
                LIMIT 25;
                """
            ),
            {"q": fts_query},
        ).fetchall()
        for r in rows:
            results.append(
                {
                    "entity_type": r[0],
                    "entity_id": int(r[1]),
                    "journey_id": int(r[2]),
                    "title": r[3],
                    "subtitle": r[4],
                    "snippet": r[5],
                }
            )
    return {"query": q, "count": len(results), "results": results}


# ---------------------------------------------------------------------------
# 8. AI Providers, Hardware Inspection & Persistent 5-Tier Memory
# ---------------------------------------------------------------------------
@router.get("/ai/live-status")
async def get_live_ai_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    p_router = ProviderRouter(db)
    provider, active_model, is_local = p_router.get_active_provider()
    health = await provider.health_check()
    installed_names = [m.name for m in health.available_models]
    model_installed = (
        any(
            active_model.lower() == m.lower() or active_model.split(":")[0].lower() in m.lower()
            for m in installed_names
        )
        if is_local
        else bool(health.online)
    )
    is_connected = bool(health.online and model_installed)
    return {
        "active_provider": "ollama" if is_local else "gemini",
        "active_model": active_model,
        "is_local": is_local,
        "online": bool(health.online),
        "model_installed": bool(model_installed),
        "is_connected": is_connected,
        "latency_ms": round(health.latency_ms, 1),
        "status_message": health.message,
        "installed_models": installed_names,
        "generation_status": "connected" if is_connected else "disconnected",
    }


@router.get("/ai/status")
async def get_ai_and_hardware_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    p_router = ProviderRouter(db)
    ollama_cfg = p_router.get_ollama_config()
    gemini_cfg = p_router.get_gemini_config()

    ollama_prov = OllamaProvider(base_url=ollama_cfg.base_url, default_model=ollama_cfg.default_model)
    ollama_health = await ollama_prov.health_check()

    installed_names = [m.name for m in ollama_health.available_models]
    hardware_report = inspect_host_hardware(installed_names)

    from app.services.secret_storage import decrypt_secret, mask_secret

    decrypted_gemini_key = decrypt_secret(gemini_cfg.encrypted_api_key)
    gemini_prov = GeminiProvider(
        api_key=decrypted_gemini_key,
        default_model=gemini_cfg.default_model,
        enabled=gemini_cfg.is_enabled,
    )
    gemini_health = await gemini_prov.health_check()

    return {
        "hardware": hardware_report.model_dump(),
        "ollama": {
            "config": {
                "is_enabled": ollama_cfg.is_enabled,
                "is_default": ollama_cfg.is_default,
                "base_url": ollama_cfg.base_url,
                "default_model": ollama_cfg.default_model,
                "task_routing": ollama_cfg.task_routing_json,
                "context_length": ollama_cfg.context_length,
                "privacy_notice": ollama_cfg.privacy_notice,
            },
            "health": ollama_health.model_dump(),
        },
        "gemini": {
            "config": {
                "is_enabled": gemini_cfg.is_enabled,
                "is_default": gemini_cfg.is_default,
                "default_model": gemini_cfg.default_model,
                "has_api_key": bool(decrypted_gemini_key),
                "masked_api_key": mask_secret(gemini_cfg.encrypted_api_key),
                "privacy_notice": gemini_cfg.privacy_notice,
            },
            "health": gemini_health.model_dump(),
        },
        "services_manifest": AIOrchestrationService.SERVICES_MANIFEST,
    }


@router.put("/ai/providers")
async def update_ai_provider_config(
    req: UpdateAIProviderRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    p_router = ProviderRouter(db)
    cfg = p_router.get_ollama_config() if req.provider_name == "ollama" else p_router.get_gemini_config()

    if req.is_enabled is not None:
        cfg.is_enabled = req.is_enabled
    if req.is_default is not None:
        cfg.is_default = req.is_default
    if req.base_url is not None:
        cfg.base_url = req.base_url
    if req.api_key is not None:
        from app.services.secret_storage import encrypt_secret
        cfg.encrypted_api_key = encrypt_secret(req.api_key.strip()) if req.api_key.strip() else ""
    if req.default_model is not None:
        cfg.default_model = req.default_model
    if req.task_routing_json is not None:
        cfg.task_routing_json = req.task_routing_json

    if req.allow_cloud_ai is not None:
        u_settings = db.query(UserSettings).first()
        if u_settings:
            u_settings.allow_cloud_ai = req.allow_cloud_ai

    db.commit()
    return await get_ai_and_hardware_status(db)


class TestPromptRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    system_prompt: Optional[str] = "You are Axiom OS Local AI Engine. Respond clearly from first principles."


@router.post("/ai/test-generate")
async def test_ai_generation(req: TestPromptRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    p_router = ProviderRouter(db)
    provider, active_model, is_local = p_router.get_active_provider()
    target_model = req.model or active_model
    t0 = time.perf_counter()
    try:
        res = await provider.generate(
            prompt=req.prompt,
            system_prompt=req.system_prompt or "",
            model=target_model,
            temperature=0.3,
            max_tokens=600,
        )
        dt_ms = round((time.perf_counter() - t0) * 1000, 1)
        return {
            "content": res.content,
            "model": target_model,
            "provider": "ollama" if is_local else "gemini",
            "is_local": is_local,
            "latency_ms": dt_ms,
            "status": res.generation_status,
        }
    except Exception as e:
        dt_ms = round((time.perf_counter() - t0) * 1000, 1)
        return {
            "content": f"[Error connecting to {target_model}]: {str(e)}",
            "model": target_model,
            "provider": "ollama" if is_local else "gemini",
            "is_local": is_local,
            "latency_ms": dt_ms,
            "status": "error",
        }


@router.get("/memories")
def list_memories(category: Optional[str] = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = db.query(MemoryFact).filter(MemoryFact.is_active == True)  # noqa: E712
    if category:
        query = query.filter(MemoryFact.memory_category == category)
    items = query.order_by(MemoryFact.updated_at.desc()).all()
    return [
        {
            "id": m.id,
            "memory_category": m.memory_category,
            "subject_key": m.subject_key,
            "fact_statement": m.fact_statement,
            "confidence": m.confidence,
            "source_entity_type": m.source_entity_type,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        }
        for m in items
    ]


@router.post("/memories")
def upsert_memory(req: MemoryUpsertRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    m = AIOrchestrationService(db).record_memory(
        category=req.memory_category,
        subject_key=req.subject_key,
        fact_statement=req.fact_statement,
        source_type="user_manual",
    )
    return {
        "id": m.id,
        "memory_category": m.memory_category,
        "subject_key": m.subject_key,
        "fact_statement": m.fact_statement,
    }


@router.delete("/memories/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    m = db.query(MemoryFact).filter(MemoryFact.id == memory_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Memory not found")
    db.delete(m)
    db.commit()
    return {"deleted": True, "id": memory_id}


# ---------------------------------------------------------------------------
# 9. Obsidian Integration Endpoints (Test G)
# ---------------------------------------------------------------------------
@router.get("/obsidian/config")
def get_obsidian_config(db: Session = Depends(get_db)) -> dict[str, Any]:
    svc = ObsidianConnectorService(db)
    cfg = svc.get_config()
    return {
        "is_enabled": cfg.is_enabled,
        "endpoint_url": cfg.endpoint_url,
        "has_auth_token": bool(cfg.auth_token),
        "vault_name": cfg.vault_name,
        "vault_local_path": cfg.vault_local_path,
        "approved_folders": cfg.approved_folders_json,
        "read_permission": cfg.read_permission,
        "write_permission": cfg.write_permission,
        "status_message": cfg.status_message,
    }


@router.put("/obsidian/config")
def update_obsidian_config(req: UpdateObsidianConfigRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    svc = ObsidianConnectorService(db)
    cfg = svc.get_config()
    cfg.is_enabled = req.is_enabled
    if req.endpoint_url is not None:
        cfg.endpoint_url = req.endpoint_url
    if req.auth_token is not None:
        from app.services.secret_storage import encrypt_secret
        cfg.auth_token = encrypt_secret(req.auth_token.strip()) if req.auth_token.strip() else ""
    if req.vault_name is not None:
        cfg.vault_name = req.vault_name
    if req.vault_local_path is not None:
        cfg.vault_local_path = req.vault_local_path
    if req.read_permission is not None:
        cfg.read_permission = req.read_permission
    if req.write_permission is not None:
        cfg.write_permission = req.write_permission
    cfg.last_verified_at = datetime.now(timezone.utc)
    db.commit()
    return get_obsidian_config(db)


@router.post("/obsidian/export")
async def export_to_obsidian_endpoint(
    req: ObsidianExportRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    svc = ObsidianConnectorService(db)
    return await svc.export_to_obsidian(
        export_type=req.export_type,
        entity_id=req.entity_id,
        target_vault_dir=req.target_vault_dir,
        allow_overwrite=req.allow_overwrite,
    )


@router.get("/obsidian/sync-preview")
def get_obsidian_sync_preview(target_vault_dir: Optional[str] = None, db: Session = Depends(get_db)) -> dict[str, Any]:
    return ObsidianConnectorService(db).generate_sync_preview(target_vault_dir)


# ---------------------------------------------------------------------------
# 10. n8n Local Automation & Backups Endpoints (Test H)
# ---------------------------------------------------------------------------
@router.get("/automation/status")
async def get_automation_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    return await N8nAutomationService(db).check_connectivity()


@router.post("/automation/workflows/{workflow_key}/execute")
async def execute_automation_workflow(
    workflow_key: str,
    payload: Optional[dict[str, Any]] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return await N8nAutomationService(db).execute_workflow(workflow_key, payload or {})


@router.get("/system/backups")
def list_backups(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    records = db.query(BackupRecord).order_by(BackupRecord.created_at.desc()).all()
    return [
        {
            "id": b.id,
            "backup_type": b.backup_type,
            "folder_path": b.folder_path,
            "size_bytes": b.size_bytes,
            "item_count": b.item_count,
            "triggered_by": b.triggered_by,
            "notes_summary": b.notes_summary,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in records
    ]


@router.post("/system/backups")
def create_backup_endpoint(db: Session = Depends(get_db)) -> dict[str, Any]:
    rec = N8nAutomationService(db).create_dated_backup(triggered_by="manual_ui")
    return {
        "id": rec.id,
        "backup_type": rec.backup_type,
        "folder_path": rec.folder_path,
        "size_bytes": rec.size_bytes,
        "item_count": rec.item_count,
        "notes_summary": rec.notes_summary,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
    }
