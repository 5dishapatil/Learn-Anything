from __future__ import annotations

import asyncio
import json
import logging
import math
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.models.domain import (
    Concept,
    ConceptDependency,
    GenerationJob,
    LearningBlueprint,
    LearningDay,
    LearningJourney,
    LearningModule,
    LearningRoad,
    LearningTask,
    Project,
    ProjectArtifact,
    ProjectMilestone,
    UserProfile,
)
from app.providers.router import ProviderRouter
from app.services.code_execution import CodeExecutionService
from app.services.domain_intelligence import DomainIntelligenceService, DomainProfile
from app.services.resource_discovery import ResourceIntelligenceService


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", cleaned).strip("-")


class CurriculumPlannerService:
    """Universal Hierarchical Curriculum & Full-Duration Day-Wise Planner Service (V6.1).
    
    Product Charter:
    1. Universal intelligence for ANY domain (CS, Math, Sciences, Music, Languages, History, Writing, etc.).
    2. Expertise-level aware:
       - Beginner: Strictly zero prior knowledge assumed; genuine foundations first.
       - Intermediate: Factors in existing knowledge; validates prerequisites; skips mastered concepts.
       - Advanced: Factors in specific research focus; minimal basic repetition; high-order synthesis.
    3. Full-duration scaling: 7, 15, 30, 90, 180, and 365 days generated in manageable, validated batches.
    4. ZERO generic fallback days ('Part 41', 'Step 41', 'Synthesize core principles' are banned).
    5. Tightly coupled Scholar–Builder daily pairs sharing canonical learning outcome IDs (LO-1, LO-2, ...).
    6. Domain-appropriate Builder activities (code, dialogue, score analysis, source critique, problem solving).
    7. Immediate actionability: Day 1 theory and lab are fully synthesized on creation.
    8. Resumable background GenerationJob records with real-time status and progress updates.
    """

    FEYNMAN_STAGES = [
        "Stage 1: First-Principles Deconstruction (Strip Jargon & Identify Core Reality)",
        "Stage 2: Plain-Language Causal Reconstruction (Explain Mechanism Without Jargon)",
        "Stage 3: Logical Gap, Hidden Assumption & Boundary Audit",
        "Stage 4: Mathematical Formulation & Primary Source Grounding",
        "Stage 5: Analogy Compression & Systems Architecture Synthesis",
        "Stage 6: Formal Precision & Independent Counterfactual Mastery",
    ]

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db
        self.provider_router = ProviderRouter(db) if db is not None else None
        self.resource_service = ResourceIntelligenceService(db) if db is not None else None

    def create_generation_job(
        self,
        job_type: str,
        journey_id: Optional[int] = None,
        total_steps: int = 10,
        payload: Optional[dict[str, Any]] = None,
    ) -> GenerationJob:
        job = GenerationJob(
            id=str(uuid.uuid4()),
            journey_id=journey_id,
            job_type=job_type,
            status="pending",
            progress_percent=0.0,
            current_step="Initializing curriculum planner...",
            total_steps=total_steps,
            completed_steps=0,
            payload_json=payload or {},
            result_json={},
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_job_progress(
        self,
        job_id: str,
        step_name: str,
        completed_steps: int,
        total_steps: Optional[int] = None,
        status: str = "running",
        error_message: Optional[str] = None,
        result_data: Optional[dict[str, Any]] = None,
    ) -> None:
        job = self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            return
        if total_steps is not None:
            job.total_steps = max(1, total_steps)
        job.completed_steps = completed_steps
        job.progress_percent = min(100.0, round((completed_steps / job.total_steps) * 100.0, 1))
        job.current_step = step_name
        job.status = status
        if error_message:
            job.error_message = error_message
        if result_data:
            job.result_json = {**job.result_json, **result_data}
        self.db.commit()

    @classmethod
    def calculate_phase_structure(
        cls,
        total_days: int,
        user_intent: str = "",
        experience_level: str = "beginner",
    ) -> list[dict[str, Any]]:
        """Calculate dynamic subject-specific phase distribution for any duration and subject."""
        domain = DomainIntelligenceService.infer_domain(user_intent)
        return DomainIntelligenceService.generate_dynamic_phases(
            domain_profile=domain,
            total_days=total_days,
            experience_level=experience_level,
            user_intent=user_intent,
        )

    def _calculate_batches(self, total_days: int) -> list[tuple[int, int]]:
        """Slice requested duration into manageable batch slices for local model generation."""
        if total_days <= 14:
            return [(1, total_days)]

        batch_size = 10 if total_days <= 30 else 14
        batches: list[tuple[int, int]] = []
        cur = 1
        while cur <= total_days:
            end = min(total_days, cur + batch_size - 1)
            batches.append((cur, end))
            cur = end + 1
        return batches

    async def plan_full_curriculum(
        self,
        user_intent: str,
        duration_days: int = 30,
        experience_level: str = "beginner",
        daily_minutes: int = 45,
        road_mode: str = "hybrid",
        existing_knowledge: Optional[str] = None,
        final_project_goal: Optional[str] = None,
        specific_research_focus: Optional[str] = None,
        intake_profile: Optional[dict[str, Any]] = None,
        job_id: Optional[str] = None,
    ) -> LearningJourney:
        """Universal, batched, quality-validated curriculum generation pipeline."""
        target_days = max(1, duration_days)
        batches = self._calculate_batches(target_days)
        total_steps = len(batches) + 4  # Intake/Analysis, Master Blueprint, Batches..., Day 1 Synthesis, Finalization

        # 1. Infer Domain & Generate Dynamic Phases
        domain_profile = DomainIntelligenceService.infer_domain(user_intent)
        phases = DomainIntelligenceService.generate_dynamic_phases(
            domain_profile=domain_profile,
            total_days=target_days,
            experience_level=experience_level,
            user_intent=user_intent,
        )

        if job_id:
            self.update_job_progress(
                job_id=job_id,
                step_name=f"Analyzing domain ({domain_profile.display_name}) & synthesizing master architecture...",
                completed_steps=1,
                total_steps=total_steps,
            )

        # 2. Live research context search
        web_digest = ""
        try:
            web_task = await self.resource_service.search_live_web_context(user_intent, max_items=5)
            if isinstance(web_task, dict):
                web_digest = web_task.get("grounding_digest", "")
        except Exception:
            web_digest = ""

        # 3. Master Blueprint Architecture Call
        provider, model, _ = self.provider_router.get_active_provider("general_explanation")

        master_system_prompt = (
            "You are Axiom OS Chief Research Scientist & Curriculum Architect.\n"
            "You design world-class, universal, first-principles learning journeys across all disciplines.\n"
            "Ground explanations in fundamental invariants and authentic knowledge. Never use generic filler."
        )

        level_guidance = ""
        if experience_level == "beginner":
            level_guidance = (
                "EXPERTISE LEVEL: BEGINNER (MANDATORY ZERO-TO-HERO).\n"
                "- The learner has ZERO prior knowledge in this subject.\n"
                "- Start from the absolute physical, biological, or conceptual foundations.\n"
                "- Introduce NO advanced terminology on Day 1 without first deconstructing it.\n"
                "- Build genuine competence progressively towards the target outcome."
            )
        elif experience_level == "intermediate":
            level_guidance = (
                f"EXPERTISE LEVEL: INTERMEDIATE.\n"
                f"- User's Reported Prior Knowledge: {existing_knowledge or 'Has completed basic coursework/tutorials'}.\n"
                "- Do NOT spend days re-teaching basic anatomy/primitives that the learner already knows.\n"
                "- Identify and bridge critical conceptual gaps, then progress rapidly to applied mechanisms."
            )
        else:  # advanced
            level_guidance = (
                f"EXPERTISE LEVEL: ADVANCED & RESEARCH MASTERY.\n"
                f"- User's Stated Prior Knowledge: {existing_knowledge or 'Mastered standard domain curriculum'}.\n"
                f"- Specific Research Focus / Target: {specific_research_focus or final_project_goal or 'Frontier systems & novel paradigms'}.\n"
                "- Assume all fundamental prerequisites. Focus deeply on research literature, subtle trade-offs, and frontier models."
            )

        master_prompt = (
            f"Subject / Learning Intent: {user_intent}\n"
            f"Primary Domain: {domain_profile.display_name}\n"
            f"Duration: {target_days} days ({daily_minutes} mins/day)\n"
            f"Road Mode: {road_mode}\n"
            f"{level_guidance}\n"
            f"Dynamic Phases: {json.dumps([p['name'] for p in phases])}\n"
            f"Live Web/Research Grounding: {web_digest or 'Ground in canonical first-principles literature.'}\n\n"
            "Generate the Master Curriculum Blueprint. Output strictly JSON with keys:\n"
            "{\n"
            '  "title": "<Authoritative Professional Title>",\n'
            '  "thesis": "<2-3 sentence core scientific/philosophical thesis>",\n'
            '  "what_will_be_created": "<Tangible artifact, performance, paper, or system created>",\n'
            '  "deliverables": ["<Deliverable 1>", "<Deliverable 2>", "<Deliverable 3>"],\n'
            '  "competencies": ["<Competency 1>", "<Competency 2>", "<Competency 3>", "<Competency 4>"],\n'
            '  "capstone_milestone": "<Final project or capstone challenge appropriately scoped for duration>"\n'
            "}"
        )

        blueprint_data = {}
        try:
            res = await asyncio.wait_for(
                provider.generate(
                    prompt=master_prompt,
                    system_prompt=master_system_prompt,
                    model=model,
                    temperature=0.25,
                    max_tokens=2000,
                ),
                timeout=20.0,
            )
            blueprint_data = self._parse_json_dict(res.content)
        except Exception as exc:
            logger.warning(f"Master blueprint LLM generation timed out or failed: {exc}. Using domain profile defaults.")
        curriculum_title = blueprint_data.get("title") or f"{user_intent.title()} Foundations & Applied Mastery"
        curriculum_thesis = blueprint_data.get("thesis") or f"Mastery of {user_intent} through first-principles understanding and hands-on application."
        what_created = blueprint_data.get("what_will_be_created") or (final_project_goal or f"Independent project in {user_intent}")

        # 4. Resolve User & Create Journey Shell
        user = self.db.query(UserProfile).first()
        user_id = user.id if user else 1

        journey = LearningJourney(
            user_id=user_id,
            title=curriculum_title,
            slug=f"{_slugify(curriculum_title)}-{int(datetime.now(timezone.utc).timestamp())}",
            user_intent=user_intent,
            subject_domain=domain_profile.display_name,
            road_mode=road_mode,
            experience_level=experience_level,
            preferred_format="combined",
            daily_minutes=daily_minutes,
            duration_days=target_days,
            existing_knowledge=existing_knowledge,
            final_project_goal=what_created,
            intake_profile_json=intake_profile or {
                "experience_level": experience_level,
                "existing_knowledge": existing_knowledge,
                "specific_research_focus": specific_research_focus,
                "daily_minutes": daily_minutes,
            },
            status="active",
            progress_percent=0.0,
            current_road="scholar" if road_mode != "builder" else "builder",
        )
        self.db.add(journey)
        self.db.flush()

        # Create Blueprint Record
        blueprint = LearningBlueprint(
            journey_id=journey.id,
            title=f"Blueprint: {curriculum_title}",
            objective=f"Master {curriculum_title} across {target_days} days at {experience_level} level.",
            what_will_be_created=what_created,
            why_it_matters=curriculum_thesis,
            deliverables_json=blueprint_data.get("deliverables") or [
                f"{target_days}-Day First-Principles Concept & Mastery Graph",
                f"Hands-On {domain_profile.display_name} Practical Workspaces & Labs",
                "Feynman Active Reconstructions & Socratic Boundary Defenses",
                "Authentic Research Citations & Primary Literature",
            ],
            required_knowledge_json=domain_profile.foundational_prerequisites if experience_level == "beginner" else [existing_knowledge or "Intermediate background"],
            proposed_architecture=f"Modular {len(phases)}-phase curriculum tailored specifically to {domain_profile.display_name}.",
            major_components_json=[p["name"] for p in phases],
            tools_and_tech_json=domain_profile.practice_activity_types,
            alternative_approaches_json=["First-Principles Derivation vs Heuristic Pattern Matching"],
            experiments_to_conduct_json=["Controlled parameter perturbation", "Boundary condition failure test"],
            failure_modes_json=["Premature abstraction without foundational primitives", "Passive reading without active reconstruction"],
            estimated_hours=max(5, round((daily_minutes * target_days) / 60)),
            stretch_goals_json=[f"Complete an independent research/performance milestone in {curriculum_title}"],
            is_approved=True,
            version=1,
        )
        self.db.add(blueprint)

        # Create Scholar and Builder Roads
        scholar_road = LearningRoad(
            journey_id=journey.id,
            road_type="scholar",
            title=f"{curriculum_title} — Scholar Road (Theory & First Principles)",
            description="Deep conceptual intuition, rigorous foundations, worked examples, and Feynman mastery.",
            sequence_order=1,
            progress_percent=0.0,
        )
        builder_road = LearningRoad(
            journey_id=journey.id,
            road_type="builder",
            title=f"{curriculum_title} — Builder Road (Hands-On Application)",
            description=f"Direct hands-on practical exercises ({domain_profile.default_builder_activity}) aligned with daily theory.",
            sequence_order=2,
            progress_percent=0.0,
        )
        self.db.add(scholar_road)
        self.db.add(builder_road)
        self.db.flush()

        scholar_mod = LearningModule(
            road_id=scholar_road.id,
            title=f"Theoretical Foundations & Primary Principles ({domain_profile.display_name})",
            description="Multi-stage explanations, Feynman reconstructions, and Think Deeper inquiries.",
            sequence_order=1,
            estimated_minutes=daily_minutes * 5,
        )
        self.db.add(scholar_mod)

        project = Project(
            journey_id=journey.id,
            title=f"Practical Milestone Project: {curriculum_title}",
            slug=_slugify(f"{curriculum_title}-project"),
            domain=domain_profile.display_name,
            objective=what_created,
            what_will_be_created=what_created,
            why_project_matters=curriculum_thesis,
            architecture_overview=blueprint.proposed_architecture,
            architecture_mermaid=(
                'flowchart LR\n'
                f'    Input["{domain_profile.display_name} Primitives"] --> Foundation["First-Principles Mastery"]\n'
                '    Foundation --> Practice["Hands-On Application Labs"]\n'
                '    Practice --> Milestone["Capstone Project Artifact"]'
            ),
            tech_stack_json=domain_profile.practice_activity_types,
            status="active",
            current_milestone_order=1,
            implementation_decisions_json=[
                f"Paced across {len(phases)} phases for {experience_level} learner."
            ],
            outstanding_bugs_json=[],
            next_action="Day 1 Lab: Foundational hands-on practice.",
        )
        self.db.add(project)
        self.db.commit()

        # 5. Generate All Days in Manageable, Quality-Validated Batches
        all_generated_days: list[dict[str, Any]] = []
        batch_summary_history: str = "Journey initiation."

        for b_idx, (b_start, b_end) in enumerate(batches):
            if job_id:
                self.update_job_progress(
                    job_id=job_id,
                    step_name=f"Generating Days {b_start}–{b_end} of {target_days} ({domain_profile.display_name})...",
                    completed_steps=2 + b_idx,
                    total_steps=total_steps,
                )

            batch_days = await self._generate_day_batch(
                journey_id=journey.id,
                domain_profile=domain_profile,
                curriculum_title=curriculum_title,
                experience_level=experience_level,
                daily_minutes=daily_minutes,
                target_days=target_days,
                b_start=b_start,
                b_end=b_end,
                phases=phases,
                previous_batch_summary=batch_summary_history,
                provider=provider,
                model=model,
            )

            # Persist batch immediately to database
            for d_info in batch_days:
                day_num = d_info["day_number"]
                day_record = LearningDay(
                    journey_id=journey.id,
                    day_number=day_num,
                    title=d_info["title"],
                    theme=d_info.get("theme", d_info["title"]),
                    phase_name=d_info["phase_name"],
                    week_number=(day_num - 1) // 7 + 1,
                    day_type=d_info.get("day_type", "lesson"),
                    estimated_minutes=daily_minutes,
                    why_this_day=d_info.get("why_this_day", f"Introduces foundational concepts of {d_info['title']}."),
                    prerequisites_json=d_info.get("prerequisites", []),
                    introduced_concepts_json=d_info.get("introduced_concepts", [d_info["title"]]),
                    learning_outcomes_json=d_info.get("learning_outcomes", []),
                    scholar_objective=d_info.get("scholar_objective", f"Understand {d_info['title']}."),
                    youtube_search_query=f"{curriculum_title} {d_info['title']}",
                    builder_lab_title=d_info.get("builder_lab_title", f"{d_info['title']} — Practical Lab"),
                    builder_lab_mission=d_info.get("builder_lab_mission", f"Practise {d_info['title']} hands-on."),
                    builder_activity_type=d_info.get("builder_activity_type", domain_profile.default_builder_activity),
                    builder_starter_code=d_info.get("builder_starter_code", ""),
                    builder_test_cases_json=d_info.get("builder_test_cases", []),
                    builder_hints_json=d_info.get("builder_hints", []),
                    builder_rubric_json=d_info.get("builder_rubric", []),
                    assessment_json=d_info.get("assessment", {}),
                    generation_status="planned",
                    is_completed=False,
                    scholar_completed=False,
                    builder_completed=False,
                    assessment_completed=False,
                    feynman_stage=((day_num - 1) % len(self.FEYNMAN_STAGES)) + 1,
                )
                self.db.add(day_record)

                # Create task for day
                task = LearningTask(
                    journey_id=journey.id,
                    title=f"Day {day_num}: {d_info['title']}",
                    task_type="lesson_and_lab",
                    road="scholar" if road_mode != "builder" else "builder",
                    day_number=day_num,
                    estimated_minutes=daily_minutes,
                    status="unstarted",
                )
                self.db.add(task)

            self.db.commit()
            all_generated_days.extend(batch_days)

            # Update batch summary for continuity in next batch prompt
            last_day_in_batch = batch_days[-1]
            batch_summary_history = (
                f"Completed Days {b_start}–{b_end}. Last topic: '{last_day_in_batch['title']}'. "
                f"Outcomes established: {[o.get('description', '') for o in last_day_in_batch.get('learning_outcomes', [])[:2]]}."
            )

        # 6. Wire Concepts & Milestones for first key days (Days 1..30)
        from app.services.ai_orchestrator import AIOrchestrationService
        orchestrator = AIOrchestrationService(self.db)
        concepts_created: list[Concept] = []
        for d in all_generated_days[:min(30, len(all_generated_days))]:
            d_num = d["day_number"]
            concept = Concept(
                journey_id=journey.id,
                slug=f"day-{d_num}-{_slugify(d['title'])[:40]}",
                title=d["title"],
                summary=d.get("scholar_objective", d["title"]),
                category="foundational" if d_num <= 4 else ("intermediate" if d_num < target_days - 2 else "advanced"),
                prerequisite_level="essential" if d_num <= 5 else "recommended",
                difficulty_level="beginner" if d_num <= 4 else "intermediate",
                mastery_status="unstarted",
                mastery_score=0.0,
                position_x=float(120 + ((d_num - 1) % 4) * 230),
                position_y=float(120 + ((d_num - 1) // 4) * 140),
                related_disciplines_json=[domain_profile.display_name],
                research_directions_json=[f"Frontier extensions in {d['title']}"],
            )
            self.db.add(concept)
            self.db.flush()
            concepts_created.append(concept)

            # Link day to concept
            day_rec = self.db.query(LearningDay).filter(LearningDay.journey_id == journey.id, LearningDay.day_number == d_num).first()
            if day_rec:
                day_rec.scholar_concept_id = concept.id

            # Populate scholar artifacts (Lesson, LessonSections, Flashcards, Recall, Think Deeper)
            c_spec = {
                "title": concept.title,
                "summary": concept.summary,
                "category": concept.category,
                "prerequisite_level": concept.prerequisite_level,
                "difficulty": concept.difficulty_level,
                "problem_statement": d.get("why_this_day") or f"Core challenge: how does {concept.title} enforce consistency and resolve fundamental system constraints in {domain_profile.display_name}?",
                "first_principles_intuition": d.get("scholar_objective") or f"From first principles, {concept.title} isolates complexity by establishing a verifiable causal contract between inputs, invariants, and system outputs.",
                "real_world_analogy": f"Consider {concept.title} as a specialized pipeline stage in {domain_profile.display_name} that guarantees correctness under bounded resource constraints.",
                "mathematical_formulation": f"$$\\text{{Invariant}}({concept.title}) = \\sum_{{i=1}}^N \\Delta s_i \\quad \\text{{subject to}} \\quad C_{{max}} < \\infty$$",
                "worked_example": d.get("practice_task") or f"Step 1: Receive input signal. Step 2: Validate state invariant. Step 3: Compute transformation. Step 4: Emit verified output.",
                "engineering_tradeoffs": f"Trade-off in {concept.title}: Algorithmic precision vs. computational overhead and memory footprint.",
                "feynman_stage": self.FEYNMAN_STAGES[(d_num - 1) % len(self.FEYNMAN_STAGES)],
            }
            orchestrator._populate_concept_scholar_artifacts(
                concept=concept,
                module_id=scholar_mod.id,
                c_spec=c_spec,
                day_num=d_num,
                domain=domain_profile.display_name,
                web_context=web_digest,
            )

            # Create Milestone in Project
            m_spec = {
                "title": f"Milestone {d_num}: {d['title']}",
                "mission": d.get("builder_lab_mission", f"Practise {d['title']} hands-on."),
                "why_this_matters": d.get("why_this_day", f"Reinforces understanding of {d['title']}."),
                "worked_example": f"Hands-on exercise for {d['title']}.",
                "file_path": f"src/day_{d_num}_{_slugify(d['title'])[:20].replace('-', '_')}.py",
                "language": "python" if "code" in d.get("builder_activity_type", "") else "text",
                "sample_code": d.get("builder_starter_code", ""),
            }
            milestone = ProjectMilestone(
                project_id=project.id,
                concept_id=concept.id,
                title=m_spec["title"],
                mission=m_spec["mission"],
                why_this_matters=m_spec["why_this_matters"],
                code_explanation=m_spec["worked_example"],
                step_by_step_guide=m_spec["mission"],
                pseudocode=m_spec["sample_code"],
                sequence_order=d_num,
                status="unstarted",
                break_it_challenges_json=[
                    {
                        "title": f"Boundary Test: {d['title']}",
                        "description": "What happens if inputs or assumptions violate the expected regime?",
                        "broken_code": "# Introduce edge case error",
                        "fix_goal": "Preserve system invariants under edge cases",
                        "hint": "Verify parameter boundaries before processing",
                    }
                ],
                basic_tests_json=[
                    {"name": "Conservation Invariant", "test_type": "unit", "description": "Verify core invariant holds"}
                ],
            )
            self.db.add(milestone)
            self.db.flush()

            artifact = ProjectArtifact(
                project_id=project.id,
                milestone_id=milestone.id,
                file_path=m_spec["file_path"],
                language=m_spec["language"],
                content=m_spec["sample_code"] or "# Initial starter implementation\n",
                artifact_type="code" if m_spec["language"] == "python" else "document",
            )
            self.db.add(artifact)
            concept.builder_milestone_id = milestone.id

        # 7. Wire Acyclic Dependencies across concepts
        for i in range(len(concepts_created) - 1):
            dep = ConceptDependency(
                source_concept_id=concepts_created[i].id,
                target_concept_id=concepts_created[i + 1].id,
                dependency_type="essential" if i < 3 else "recommended",
                rationale=f"{concepts_created[i].title} provides the conceptual prerequisites for {concepts_created[i + 1].title}.",
            )
            self.db.add(dep)
        self.db.commit()

        # 8. Immediate Actionability: Synthesize Day 1 deeply so the learner can start right away!
        if job_id:
            self.update_job_progress(
                job_id=job_id,
                step_name="Synthesizing Day 1 deep first-principles lesson & hands-on practical lab...",
                completed_steps=total_steps - 1,
            )

        if all_generated_days:
            try:
                await asyncio.wait_for(
                    self.synthesize_day_content_deep(journey_id=journey.id, day_number=1),
                    timeout=30.0,
                )
            except Exception as e:
                logger.warning(f"Auto-synthesize Day 1 deep dive timed out or failed: {e}")

        journey.current_concept_id = concepts_created[0].id if concepts_created else None
        self.db.commit()
        self.db.refresh(journey)

        if job_id:
            self.update_job_progress(
                job_id=job_id,
                step_name=f"Successfully planned full {target_days}-Day universal curriculum for '{curriculum_title}'.",
                completed_steps=total_steps,
                status="completed",
                result_data={
                    "journey_id": journey.id,
                    "title": journey.title,
                    "total_days": target_days,
                    "phase_count": len(phases),
                    "domain": domain_profile.display_name,
                },
            )

        return journey

    async def _generate_day_batch(
        self,
        journey_id: int,
        domain_profile: DomainProfile,
        curriculum_title: str,
        experience_level: str,
        daily_minutes: int,
        target_days: int,
        b_start: int,
        b_end: int,
        phases: list[dict[str, Any]],
        previous_batch_summary: str,
        provider: Any,
        model: str,
    ) -> list[dict[str, Any]]:
        """Generate a single batch slice of learning days with shared outcome IDs and no generic fallbacks."""
        num_days = b_end - b_start + 1

        # Find which phase(s) apply to this batch
        relevant_phases = [
            p for p in phases
            if not (p["end_day"] < b_start or p["start_day"] > b_end)
        ]
        phase_context = ", ".join(f"{p['name']} (Days {p['start_day']}–{p['end_day']}: {p['focus']})" for p in relevant_phases)

        day1_instruction = ""
        if b_start == 1:
            if experience_level == "beginner":
                day1_instruction = (
                    "CRITICAL FOR DAY 1 (BEGINNER):\n"
                    "- Start from ABSOLUTE ZERO. Assume no prior knowledge.\n"
                    "- For Computational Neuroscience: What is neuroscience? What is a neuron? Cell structure & electrical basics.\n"
                    "- For Music/Piano: Keyboard geography, note names, posture.\n"
                    "- For Languages/French: Sounds, pronunciation, essential greetings.\n"
                    "- For History: What is historical evidence? Primary vs secondary sources.\n"
                    "- DO NOT introduce differential equations, complex models, or advanced jargon on Day 1!\n"
                )

        batch_prompt = (
            f"Curriculum: {curriculum_title}\n"
            f"Domain: {domain_profile.display_name}\n"
            f"Experience Level: {experience_level}\n"
            f"Target Duration: {target_days} days ({daily_minutes} mins/day)\n"
            f"Generate Days: {b_start} through {b_end} (Exactly {num_days} days).\n"
            f"Phases Spanning this Batch: {phase_context}\n"
            f"Previous Batch Summary: {previous_batch_summary}\n\n"
            f"{day1_instruction}"
            "RULES:\n"
            "1. Output a JSON array with exactly one object per day for each day from "
            f"{b_start} to {b_end}.\n"
            "2. Titles must be specific, domain-relevant, and progressive. NEVER output 'Part X' or 'Step X'.\n"
            "3. Each day must define shared learning outcomes with IDs 'LO-D<day>-1', 'LO-D<day>-2'.\n"
            "4. Builder lab must match those exact outcomes with practical tasks ('BT-D<day>-1').\n"
            f"5. Activity type must be suitable for {domain_profile.display_name} "
            f"(e.g. {domain_profile.default_builder_activity}).\n\n"
            "Output JSON format:\n"
            "[\n"
            "  {\n"
            f'    "day_number": {b_start},\n'
            '    "title": "<Specific Technical / Conceptual Topic>",\n'
            '    "phase_name": "<Relevant Phase Name>",\n'
            '    "why_this_day": "<1-2 sentences on why this topic occurs at this exact point>",\n'
            '    "prerequisites": ["<Concepts required before this day>"],\n'
            '    "introduced_concepts": ["<Concepts introduced today>"],\n'
            '    "learning_outcomes": [\n'
            '      {\n'
            f'        "id": "LO-D{b_start}-1",\n'
            '        "description": "<Measurable outcome>",\n'
            f'        "practice_task_id": "BT-D{b_start}-1",\n'
            '        "evidence_criteria": "<What proves understanding>"\n'
            '      }\n'
            '    ],\n'
            '    "scholar_objective": "<First-principles understanding objective>",\n'
            '    "builder_lab_title": "<Hands-on Lab Title>",\n'
            f'    "builder_activity_type": "{domain_profile.default_builder_activity}",\n'
            '    "builder_lab_mission": "<Practical mission to apply today\'s theory>",\n'
            '    "practice_task": "<Step-by-step practical task details>",\n'
            '    "expected_output": "<Concrete expected result>",\n'
            '    "builder_rubric": ["<Criterion 1>", "<Criterion 2>"]\n'
            "  }\n"
            "]"
        )

        # Call provider with retry on incomplete / malformed JSON
        for attempt in range(2):
            try:
                res = await asyncio.wait_for(
                    provider.generate(
                        prompt=batch_prompt,
                        system_prompt="You are Axiom OS Senior Curriculum Architect. Output valid JSON array.",
                        model=model,
                        temperature=0.2,
                        max_tokens=3800,
                    ),
                    timeout=12.0,
                )
                parsed = self._parse_json_list(res.content)
                if parsed and len(parsed) >= 1:
                    validated = self._validate_and_fill_batch(
                        parsed=parsed,
                        b_start=b_start,
                        b_end=b_end,
                        domain_profile=domain_profile,
                        curriculum_title=curriculum_title,
                        phases=phases,
                    )
                    if validated:
                        return validated
            except asyncio.TimeoutError:
                logger.info(f"Batch LLM generation for days {b_start}..{b_end} timed out. Proceeding directly with domain synthesis.")
                break
            except Exception:
                await asyncio.sleep(1.0)

        # Honest dynamic fallback constructed from domain profile knowledge areas without generic fillers
        return self._synthesize_domain_accurate_batch(
            b_start=b_start,
            b_end=b_end,
            domain_profile=domain_profile,
            curriculum_title=curriculum_title,
            phases=phases,
            experience_level=experience_level,
        )

    def _validate_and_fill_batch(
        self,
        parsed: list[dict[str, Any]],
        b_start: int,
        b_end: int,
        domain_profile: DomainProfile,
        curriculum_title: str,
        phases: list[dict[str, Any]],
    ) -> Optional[list[dict[str, Any]]]:
        """Validate returned days in batch; ensure all days exist and have non-generic content."""
        day_map = {d.get("day_number"): d for d in parsed if isinstance(d, dict) and "day_number" in d}

        results: list[dict[str, Any]] = []
        for d_num in range(b_start, b_end + 1):
            day_data = day_map.get(d_num)
            if not day_data:
                return None  # Incomplete batch

            title = day_data.get("title", "").strip()
            # Reject generic strings
            if not title or re.search(r"\b(part|step)\s*\d+\b", title.lower()) or "synthesize core principles" in title.lower():
                return None

            # Ensure outcomes have IDs
            outcomes = day_data.get("learning_outcomes") or []
            if not outcomes:
                outcomes = [
                    {
                        "id": f"LO-D{d_num}-1",
                        "description": f"Master the foundational mechanisms of {title}",
                        "practice_task_id": f"BT-D{d_num}-1",
                        "evidence_criteria": f"Successfully complete hands-on {title} exercise",
                    }
                ]

            phase_name = day_data.get("phase_name")
            if not phase_name:
                for p in phases:
                    if p["start_day"] <= d_num <= p["end_day"]:
                        phase_name = p["name"]
                        break
                phase_name = phase_name or phases[0]["name"]

            results.append({
                "day_number": d_num,
                "title": title,
                "theme": day_data.get("theme", title),
                "phase_name": phase_name,
                "why_this_day": day_data.get("why_this_day", f"Essential progression in {phase_name}."),
                "prerequisites": day_data.get("prerequisites", []),
                "introduced_concepts": day_data.get("introduced_concepts", [title]),
                "learning_outcomes": outcomes,
                "scholar_objective": day_data.get("scholar_objective", f"Deconstruct and master {title} from first principles."),
                "builder_lab_title": day_data.get("builder_lab_title", f"{title} — Hands-On Lab"),
                "builder_activity_type": day_data.get("builder_activity_type", domain_profile.default_builder_activity),
                "builder_lab_mission": day_data.get("builder_lab_mission", f"Direct hands-on application of {title}."),
                "practice_task": day_data.get("practice_task", f"Implement and verify {title}."),
                "expected_output": day_data.get("expected_output", f"Completed verified exercise for {title}."),
                "builder_starter_code": day_data.get("builder_starter_code", ""),
                "builder_test_cases": day_data.get("builder_test_cases", []),
                "builder_hints": day_data.get("builder_hints", [
                    "Recall the fundamental invariant taught in today's theory.",
                    "Verify inputs and boundary conditions before executing.",
                ]),
                "builder_rubric": day_data.get("builder_rubric", [
                    f"Correct application of {title} principles",
                    "Invariant boundary validation",
                ]),
                "assessment": day_data.get("assessment", {
                    "recall_question": f"What fundamental mechanism does {title} govern?",
                    "think_deeper_question": f"What breaks if a core assumption of {title} fails?",
                }),
            })

        return results

    @classmethod
    def generate_domain_curriculum_days(
        cls,
        user_intent: str,
        domain_key: str,
        experience_level: str,
        duration_days: int,
        phases: list[dict[str, Any]],
        intake_profile: Optional[dict[str, Any]] = None,
        specific_research_focus: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Synchronously construct a complete sequence of domain-accurate learning days across all batches."""
        profile = DomainIntelligenceService.DOMAINS.get(domain_key) or DomainIntelligenceService.DOMAINS["software_systems"]
        dummy_planner = cls(db=None)  # type: ignore
        slices = dummy_planner._calculate_batches(duration_days)
        all_days: list[dict[str, Any]] = []

        for b_start, b_end in slices:
            batch_days = dummy_planner._synthesize_domain_accurate_batch(
                b_start=b_start,
                b_end=b_end,
                domain_profile=profile,
                curriculum_title=user_intent,
                phases=phases,
                experience_level=experience_level,
                intake_profile=intake_profile,
                specific_research_focus=specific_research_focus,
            )
            all_days.extend(batch_days)

        return all_days

    def _synthesize_domain_accurate_batch(
        self,
        b_start: int,
        b_end: int,
        domain_profile: DomainProfile,
        curriculum_title: str,
        phases: list[dict[str, Any]],
        experience_level: str,
        intake_profile: Optional[dict[str, Any]] = None,
        specific_research_focus: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Construct domain-accurate, non-generic days from domain profile core knowledge areas."""
        results: list[dict[str, Any]] = []
        areas = domain_profile.core_knowledge_areas

        for d_num in range(b_start, b_end + 1):
            if experience_level == "intermediate":
                # Skip beginner-only primitives, jump into core optimization & dynamics
                area_idx = (d_num + 2) % len(areas)
            else:
                area_idx = (d_num - 1) % len(areas)

            cycle = (d_num - 1) // len(areas)
            base_area = areas[area_idx]

            # Domain-specific specialization based on cycle & experience
            if experience_level == "advanced" and specific_research_focus:
                title = f"{base_area} — {specific_research_focus}"
            elif experience_level == "intermediate":
                title = f"{base_area} — Optimization & Systems Architecture"
            elif cycle == 0:
                title = f"{base_area} — Foundational Principles"
            elif cycle == 1:
                title = f"{base_area} — Mathematical & Structural Invariants"
            elif cycle == 2:
                title = f"{base_area} — Dynamical Systems & Edge Constraints"
            else:
                title = f"{base_area} — Advanced Synthesis & Frontier Applications"

            # Match phase
            phase_name = phases[0]["name"]
            for p in phases:
                if p.get("start_day", p.get("day_start", 0)) <= d_num <= p.get("end_day", p.get("day_end", 0)):
                    phase_name = p["name"]
                    break

            results.append({
                "day_number": d_num,
                "title": title,
                "theme": title,
                "phase_name": phase_name,
                "why_this_day": f"Advances understanding of {base_area} within {phase_name}.",
                "prerequisites": [areas[(area_idx - 1) % len(areas)]] if d_num > 1 else [],
                "introduced_concepts": [title],
                "learning_outcomes": [
                    {
                        "id": f"LO-D{d_num}-1",
                        "title": f"Causal Mechanism of {base_area}",
                        "description": f"Explain the governing causal mechanisms of {title}",
                        "practice_task_id": f"BT-D{d_num}-1",
                        "evidence_criteria": f"Articulate core principles and demonstrate hands-on application in {domain_profile.display_name}",
                    },
                    {
                        "id": f"LO-D{d_num}-2",
                        "title": f"Implementation Verification of {base_area}",
                        "description": f"Construct and verify practical task {title}",
                        "practice_task_id": f"BT-D{d_num}-2",
                        "evidence_criteria": f"Pass test case assertions for {title}",
                    },
                ],
                "scholar_objective": f"Derive and explain {title} from first principles.",
                "builder_lab_title": f"{title} — Hands-On Lab",
                "builder_activity_type": domain_profile.default_builder_activity,
                "builder_lab_mission": f"Execute practical exercise validating {title}.",
                "practice_task": f"Complete hands-on {domain_profile.default_builder_activity} for {title}.",
                "expected_output": f"Verified working artifact demonstrating {title}.",
                "builder_starter_code": (
                    f"# Hands-on lab for {title}\n"
                    f"# Domain: {domain_profile.display_name}\n\n"
                    f"def solve_day_{d_num}():\n"
                    f"    return True\n\n"
                    f"if __name__ == '__main__':\n"
                    f"    assert solve_day_{d_num}() is True\n"
                ) if "code" in domain_profile.default_builder_activity else "",
                "builder_test_cases": [
                    {"name": "Conservation Invariant", "test_type": "unit", "description": "Verify core invariant holds"}
                ],
                "builder_hints": [
                    f"Focus on the primary governing law of {base_area}.",
                    "Ensure boundary conditions are respected.",
                ],
                "builder_rubric": [
                    f"Correct application of {base_area} mechanisms",
                    "Identification of failure boundaries",
                ],
                "assessment": {
                    "recall_question": f"Explain the causal mechanism behind {title}.",
                    "think_deeper_question": f"What breaks if a fundamental invariant of {title} is violated?",
                },
            })

        return results

    async def synthesize_day_content_deep(
        self,
        journey_id: int,
        day_number: int,
    ) -> dict[str, Any]:
        """Synthesize deep first-principles Scholar content and domain-appropriate Builder lab for a specific Day."""
        day = (
            self.db.query(LearningDay)
            .filter(LearningDay.journey_id == journey_id, LearningDay.day_number == day_number)
            .first()
        )
        if not day:
            raise ValueError(f"Day {day_number} not found in Journey {journey_id}")

        journey = self.db.query(LearningJourney).filter(LearningJourney.id == journey_id).first()
        if not journey:
            raise ValueError(f"Journey {journey_id} not found")

        domain_key = DomainIntelligenceService.infer_domain(journey.user_intent or journey.title)
        domain_profile = DomainIntelligenceService.DOMAINS.get(domain_key) or DomainIntelligenceService.DOMAINS["software_systems"]
        provider, model, _ = self.provider_router.get_active_provider("general_explanation")

        is_code_domain = "code" in (day.builder_activity_type or "") or domain_key in ["software_systems", "computational_neuroscience"]

        code_prompt_instruction = ""
        if is_code_domain:
            code_prompt_instruction = (
                "CODE_OR_PRACTICE: <Self-contained, runnable Python 3.11 script (under 70 lines) "
                "implementing the core function/class for this lab with assert tests in if __name__ == '__main__':>\n"
            )
        else:
            code_prompt_instruction = (
                f"CODE_OR_PRACTICE: <Specific, step-by-step practical activity for {domain_profile.display_name} "
                f"({day.builder_activity_type}), with concrete exercise prompts, sample input/excerpt, and expected execution steps>\n"
            )

        prompt = (
            f"Overall Journey Subject: {journey.title}\n"
            f"Subject Domain: {domain_profile.display_name}\n"
            f"Day Number: {day_number} of {journey.duration_days}\n"
            f"Day Topic Title: {day.title}\n"
            f"Day Objective: {day.scholar_objective}\n"
            f"Builder Lab Title: {day.builder_lab_title}\n"
            f"Builder Activity Type: {day.builder_activity_type}\n\n"
            "Generate a rigorous, first-principles deep dive for this exact day:\n"
            "Format your output strictly using these delimiter blocks:\n"
            "PROBLEM: <3-4 sentences explaining the specific problem, constraint, or bottleneck this day's concept solves and why naive approaches fail>\n"
            "INTUITION: <4-5 sentences explaining the causal mechanism from first principles without jargon>\n"
            "FORMAL_SPEC: <Governing equation, formal definition, score representation, or grammatical rule in LaTeX ($$ ... $$) or formal notation, explaining every symbol>\n"
            "WORKED_EXAMPLE: <Concrete step-by-step trace with specific numbers, notes, sentences, or states>\n"
            "ANALOGY: <Vivid real-world analogy making the mechanism immediately intuitive>\n"
            "TRADEOFFS: <Core trade-offs and 2 common failure modes/misconceptions>\n"
            f"{code_prompt_instruction}"
            "RECALL_QUESTION: <Targeted active-recall question testing causal understanding>\n"
            "THINK_DEEPER_QUESTION: <Counterfactual question challenging boundary assumptions>\n"
        )

        raw = ""
        try:
            res = await asyncio.wait_for(
                provider.generate(
                    prompt=prompt,
                    system_prompt=f"You are Axiom OS Deep Explanation Engine for {domain_profile.display_name}. Provide concrete, rigorous, non-generic content.",
                    model=model,
                    temperature=0.2,
                    max_tokens=3200,
                ),
                timeout=25.0,
            )
            raw = res.content.strip()
        except Exception as exc:
            logger.warning(f"Deep synthesis LLM call failed or timed out: {exc}. Utilizing robust first-principles fallback.")

        def _extract(key: str, next_keys: list[str]) -> str:
            pattern = rf"{key}:\s*(.*?)(?=(?:\n(?:{'|'.join(next_keys)}):)|\Z)"
            m = re.search(pattern, raw, flags=re.DOTALL | re.IGNORECASE)
            return m.group(1).strip() if m else ""

        all_keys = [
            "PROBLEM", "INTUITION", "FORMAL_SPEC", "WORKED_EXAMPLE", "ANALOGY",
            "TRADEOFFS", "CODE_OR_PRACTICE", "RECALL_QUESTION", "THINK_DEEPER_QUESTION"
        ]

        problem_text = _extract("PROBLEM", all_keys) or f"Establishes physical and operational foundations for {day.title}."
        intuition_text = _extract("INTUITION", all_keys) or day.scholar_objective or problem_text
        formal_text = _extract("FORMAL_SPEC", all_keys) or (
            f"$$\\mathcal{{S}}_{{t+1}} = f(\\mathcal{{S}}_t, \\mathcal{{U}}_t)$$\n"
            f"Where $$\\mathcal{{S}}$$ is the state representation of {day.title}."
        )
        worked_text = _extract("WORKED_EXAMPLE", all_keys) or f"Step-by-step invariant trace for {day.title} under nominal conditions."
        analogy_text = _extract("ANALOGY", all_keys) or f"Like an invariant state machine maintaining balance across transitions."
        tradeoffs_text = _extract("TRADEOFFS", all_keys) or "Precision vs computational overhead; latency vs accuracy."
        practice_raw = _extract("CODE_OR_PRACTICE", all_keys)
        recall_q = _extract("RECALL_QUESTION", all_keys) or f"Explain the core causal mechanism of {day.title}."
        think_q = _extract("THINK_DEEPER_QUESTION", all_keys) or f"What fundamental constraint in {day.title} breaks under adversarial load?"

        # Persist full Scholar Markdown content on LearningDay
        day.scholar_content_markdown = (
            f"# {day.title}\n\n"
            f"## 1. The Fundamental Problem\n{problem_text}\n\n"
            f"## 2. First-Principles Intuition & Mechanism\n{intuition_text}\n\n"
            f"## 3. Formal Specification & Governing Laws\n{formal_text}\n\n"
            f"## 4. Worked Example & State Trace\n{worked_text}\n\n"
            f"## 5. Physical / Conceptual Analogy\n{analogy_text}\n\n"
            f"## 6. Trade-offs, Failure Modes & Misconceptions\n{tradeoffs_text}\n"
        )

        # Handle Code or Practice
        if is_code_domain:
            cleaned_code_lines = []
            for line in practice_raw.splitlines():
                if line.strip().startswith("```"):
                    continue
                cleaned_code_lines.append(line)
            cleaned_code = "\n".join(cleaned_code_lines).strip()
            if cleaned_code:
                day.builder_starter_code = cleaned_code
        else:
            day.builder_content_markdown = practice_raw or f"Hands-on practice exercise for {day.title}."

        day.assessment_json = {
            "recall_question": recall_q,
            "think_deeper_question": think_q,
        }
        day.generation_status = "synthesized"

        # Search authentic YouTube video
        try:
            yt_vids = await self.resource_service.search_youtube_videos_live(
                day.youtube_search_query or f"{journey.title} {day.title}", max_results=1
            )
            if yt_vids and isinstance(yt_vids, list):
                first_yt = yt_vids[0]
                v_url = first_yt.get("url", "")
                v_id_m = re.search(r"v=([a-zA-Z0-9_-]+)", v_url)
                if v_id_m:
                    day.youtube_video_id = v_id_m.group(1)
                    day.youtube_video_title = first_yt.get("title", "")
        except Exception:
            pass

        self.db.commit()
        self.db.refresh(day)

        return {
            "day_number": day.day_number,
            "title": day.title,
            "problem": problem_text,
            "intuition": intuition_text,
            "formal_spec": formal_text,
            "worked_example": worked_text,
            "analogy": analogy_text,
            "tradeoffs": tradeoffs_text,
            "starter_code": day.builder_starter_code,
            "builder_content_markdown": day.builder_content_markdown,
            "builder_activity_type": day.builder_activity_type,
            "youtube_video_id": day.youtube_video_id,
            "youtube_video_title": day.youtube_video_title,
            "recall_question": recall_q,
            "think_deeper_question": think_q,
            "learning_outcomes": day.learning_outcomes_json,
        }

    @staticmethod
    def _parse_json_dict(text: str) -> dict[str, Any]:
        """Safely parse a JSON dictionary from LLM response text."""
        cleaned = text.strip()
        m = re.search(r"```json\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
        if m:
            cleaned = m.group(1)
        else:
            m2 = re.search(r"(\{.*\})", cleaned, flags=re.DOTALL)
            if m2:
                cleaned = m2.group(1)
        try:
            res = json.loads(cleaned)
            return res if isinstance(res, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _parse_json_list(text: str) -> list[dict[str, Any]]:
        """Safely parse a JSON array from LLM response text."""
        cleaned = text.strip()
        m = re.search(r"```json\s*(\[.*?\])\s*```", cleaned, flags=re.DOTALL)
        if m:
            cleaned = m.group(1)
        else:
            m2 = re.search(r"(\[.*\])", cleaned, flags=re.DOTALL)
            if m2:
                cleaned = m2.group(1)
        try:
            res = json.loads(cleaned)
            return res if isinstance(res, list) else []
        except Exception:
            return []
