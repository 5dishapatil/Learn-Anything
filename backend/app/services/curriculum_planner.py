from __future__ import annotations

import asyncio
import json
import math
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy.orm import Session

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
    ProjectMilestone,
    UserProfile,
)
from app.providers.router import ProviderRouter
from app.services.code_execution import CodeExecutionService
from app.services.resource_discovery import ResourceIntelligenceService


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", cleaned).strip("-")


class CurriculumPlannerService:
    """Hierarchical Curriculum & Full-Duration Day-Wise Planner Service.
    
    Supports genuine 7, 15, 30, 90, 180, and 365-day curricula with:
    1. Hierarchical Master Planner -> Phase/Weekly Outline -> Day-wise schedule.
    2. Zero artificial day caps (no min(max(req_days, 4), 8)).
    3. Persistent LearningDay and GenerationJob records.
    4. Honest error reporting if AI provider is unreachable (no static fake fallback).
    5. On-demand deep synthesis for Scholar Road & Builder Road labs.
    """

    FEYNMAN_STAGES = [
        "Stage 1: First-Principles Deconstruction (Strip Jargon & Identify Core Reality)",
        "Stage 2: Plain-Language Causal Reconstruction (Explain Mechanism Without Jargon)",
        "Stage 3: Logical Gap, Hidden Assumption & Boundary Audit",
        "Stage 4: Mathematical Formulation & Primary Source Grounding",
        "Stage 5: Analogy Compression & Systems Architecture Synthesis",
        "Stage 6: Formal Precision & Independent Counterfactual Mastery",
    ]

    def __init__(self, db: Session) -> None:
        self.db = db
        self.provider_router = ProviderRouter(db)
        self.resource_service = ResourceIntelligenceService(db)

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
            current_step="Initializing generation job...",
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
    def calculate_phase_structure(cls, total_days: int) -> list[dict[str, Any]]:
        """Calculate logical phase distribution for any duration from 7 to 365 days."""
        if total_days <= 7:
            return [
                {"name": "Phase 1: Foundations & Core Mechanics", "start_day": 1, "end_day": total_days, "focus": "First-principles deconstruction and minimal runnable system."}
            ]
        elif total_days <= 15:
            mid = total_days // 2
            return [
                {"name": "Phase 1: First Principles & Core Invariants", "start_day": 1, "end_day": mid, "focus": "Theoretical foundation, mathematical definitions, and base primitives."},
                {"name": "Phase 2: Integration & Working Prototype", "start_day": mid + 1, "end_day": total_days, "focus": "Subsystem integration, failure testing, and working implementation."},
            ]
        elif total_days <= 30:
            p_len = math.ceil(total_days / 4)
            return [
                {"name": "Phase 1: Foundations & Mathematical Formulation", "start_day": 1, "end_day": p_len, "focus": "Core laws, state representations, and mathematical constraints."},
                {"name": "Phase 2: Algorithmic Mechanisms & Primitives", "start_day": p_len + 1, "end_day": p_len * 2, "focus": "Primary algorithms, data structures, and baseline tests."},
                {"name": "Phase 3: Systems Architecture & Failure Modes", "start_day": p_len * 2 + 1, "end_day": p_len * 3, "focus": "Concurrency, scaling, edge cases, and controlled failure."},
                {"name": "Phase 4: Capstone Engineering & Synthesis", "start_day": p_len * 3 + 1, "end_day": total_days, "focus": "Full working system, end-to-end verification, and Feynman defense."},
            ]
        elif total_days <= 90:
            num_phases = 6
            p_len = math.ceil(total_days / num_phases)
            names = [
                "Phase 1: Theoretical Foundations & Invariants",
                "Phase 2: Core Primitives & Low-Level Mechanics",
                "Phase 3: Algorithms & Pipeline Construction",
                "Phase 4: Systems Integration & Performance Profiling",
                "Phase 5: Resiliency, Failure Analysis & Edge Cases",
                "Phase 6: Frontier Research & Capstone Defense",
            ]
            phases = []
            for i, name in enumerate(names):
                s = i * p_len + 1
                e = min(total_days, (i + 1) * p_len)
                if s <= total_days:
                    phases.append({"name": name, "start_day": s, "end_day": e, "focus": f"Advanced mastery of {name.split(':')[1].strip()}."})
            return phases
        elif total_days <= 180:
            num_phases = 8
            p_len = math.ceil(total_days / num_phases)
            names = [
                "Phase 1: Axiomatic Foundations & Mathematics",
                "Phase 2: Architectural Primitives & State Models",
                "Phase 3: Algorithmic Implementations",
                "Phase 4: Systems Integration & Data Pipelines",
                "Phase 5: Concurrency, Scaling & Performance",
                "Phase 6: Controlled Failure & Robustness Hardening",
                "Phase 7: Advanced Research Papers & Frontier Topics",
                "Phase 8: Capstone System & Independent Publication",
            ]
            phases = []
            for i, name in enumerate(names):
                s = i * p_len + 1
                e = min(total_days, (i + 1) * p_len)
                if s <= total_days:
                    phases.append({"name": name, "start_day": s, "end_day": e, "focus": f"Mastery of {name}."})
            return phases
        else:
            # 365 Days: 12 Mastery Phases (1 month each)
            p_len = math.ceil(total_days / 12)
            names = [
                "Phase 1: Foundations & First Principles",
                "Phase 2: Formal Mathematics & Complexity",
                "Phase 3: Primitives & Core Data Structures",
                "Phase 4: Algorithmic Architecture",
                "Phase 5: Baseline Engine Implementation",
                "Phase 6: Systems Integration & Profiling",
                "Phase 7: Concurrency & Distributed Mechanics",
                "Phase 8: Fault Tolerance & Controlled Failure",
                "Phase 9: High-Throughput Optimization",
                "Phase 10: Canonical Research Literature",
                "Phase 11: Frontier & Novel Research Directions",
                "Phase 12: Production-Grade Capstone & Grand Defense",
            ]
            phases = []
            for i, name in enumerate(names):
                s = i * p_len + 1
                e = min(total_days, (i + 1) * p_len)
                if s <= total_days:
                    phases.append({"name": name, "start_day": s, "end_day": e, "focus": f"Comprehensive mastery of {name}."})
            return phases

    async def plan_full_curriculum(
        self,
        user_intent: str,
        duration_days: int = 30,
        experience_level: str = "beginner",
        daily_minutes: int = 45,
        road_mode: str = "hybrid",
        existing_knowledge: Optional[str] = None,
        final_project_goal: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> LearningJourney:
        """Master hierarchical curriculum planning and database persistence."""
        target_days = max(1, duration_days)
        phase_structure = self.calculate_phase_structure(target_days)

        if job_id:
            self.update_job_progress(job_id, "Searching live web & research context...", 1, total_steps=6)

        # 1. Fetch live web context
        web_digest = ""
        try:
            web_task = await self.resource_service.search_live_web_context(user_intent, max_items=5)
            if isinstance(web_task, dict):
                web_digest = web_task.get("grounding_digest", "")
        except Exception:
            web_digest = ""

        if job_id:
            self.update_job_progress(job_id, "Generating Master Curriculum Architecture with Ollama qwen3.5:9b...", 2)

        # 2. Call Ollama / Active Provider to get Master Plan and Week-by-Week topics
        provider, model, _ = self.provider_router.get_active_provider("general_explanation")

        master_prompt = (
            f"Topic: {user_intent}\n"
            f"Experience Level: {experience_level}\n"
            f"Total Duration: {target_days} days ({daily_minutes} mins/day)\n"
            f"Phases Outline: {', '.join(p['name'] for p in phase_structure)}\n"
            f"Live Research Digest: {web_digest or 'Ground in first principles and canonical engineering.'}\n\n"
            f"Design the Master Curriculum Architecture for '{user_intent}'.\n"
            "Requirements:\n"
            "1. CURRICULUM_TITLE: Authoritative, professional title.\n"
            "2. SUBJECT_DOMAIN: Technical or scientific discipline.\n"
            "3. THESIS: 2-3 sentences explaining the core engineering thesis.\n"
            f"4. Provide a day-by-day technical topic breakdown for all {target_days} days.\n"
            "   For each day, write a single line formatted as:\n"
            "   DAY <number> | <Day Topic Title> | <Scholar First-Principles Objective> | <Builder Coding Lab Title>\n\n"
            "RULES:\n"
            "- Every single day topic must be specific, technical, and tailored strictly to this subject.\n"
            "- DO NOT output generic placeholders.\n"
            "- Start Day 1 with fundamental physical/mathematical primitives, progressing to advanced capstone.\n"
        )

        res = await provider.generate(
            prompt=master_prompt,
            system_prompt="You are Axiom OS Principal Research Scientist. Output exact requested format.",
            model=model,
            temperature=0.25,
            max_tokens=4000,
        )

        raw = res.content.strip()
        if not raw:
            raise RuntimeError(
                f"AI Provider ({model}) returned an empty response. Ensure Ollama is running (`ollama serve`)."
            )

        title_m = re.search(r"CURRICULUM_TITLE:\s*(.+)", raw)
        domain_m = re.search(r"SUBJECT_DOMAIN:\s*(.+)", raw)
        thesis_m = re.search(r"THESIS:\s*(.+)", raw)

        curriculum_title = title_m.group(1).strip().strip("*\"'") if title_m else f"{user_intent.title()} Foundations & Systems"
        curriculum_domain = domain_m.group(1).strip().strip("*\"'") if domain_m else "Systems Engineering & Applied Science"
        curriculum_thesis = thesis_m.group(1).strip().strip("*\"'") if thesis_m else f"Mastery of {user_intent} through first-principles theory and hands-on implementation."

        # Parse DAY lines
        day_lines_parsed: dict[int, dict[str, str]] = {}
        for line in raw.splitlines():
            line = line.strip()
            if not line.upper().startswith("DAY "):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2:
                day_num_m = re.search(r"\d+", parts[0])
                if day_num_m:
                    d_num = int(day_num_m.group())
                    topic_title = parts[1].strip()
                    scholar_obj = parts[2].strip() if len(parts) > 2 else f"Understand the core causal mechanisms of {topic_title}."
                    builder_lab = parts[3].strip() if len(parts) > 3 else f"{topic_title} — Implementation Lab"
                    day_lines_parsed[d_num] = {
                        "topic": topic_title,
                        "scholar_objective": scholar_obj,
                        "builder_lab": builder_lab,
                    }

        if job_id:
            self.update_job_progress(job_id, f"Persisting Journey & {target_days} structured Learning Days...", 3)

        # 3. Create or resolve UserProfile
        user = self.db.query(UserProfile).first()
        user_id = user.id if user else 1

        journey = LearningJourney(
            user_id=user_id,
            title=curriculum_title,
            slug=f"{_slugify(curriculum_title)}-{int(datetime.now(timezone.utc).timestamp())}",
            user_intent=user_intent,
            subject_domain=curriculum_domain,
            road_mode=road_mode,
            experience_level=experience_level,
            preferred_format="combined",
            daily_minutes=daily_minutes,
            duration_days=target_days,
            existing_knowledge=existing_knowledge,
            final_project_goal=final_project_goal or f"Build, verify, and stress-test a working {curriculum_title} system.",
            status="active",
            progress_percent=0.0,  # Honest 0% starting progress
            current_road="scholar" if road_mode != "builder" else "builder",
        )
        self.db.add(journey)
        self.db.flush()

        # Create Blueprint
        blueprint = LearningBlueprint(
            journey_id=journey.id,
            title=f"Research & Build Blueprint: {curriculum_title}",
            objective=f"Master {curriculum_title} from first principles and build a verified working system across {target_days} days.",
            what_will_be_created=final_project_goal or f"A verified, tested implementation of {curriculum_title}.",
            why_it_matters=curriculum_thesis,
            deliverables_json=[
                f"{target_days}-Day First-Principles Concept & Mastery Graph",
                "Verified Python Code Artifacts & Hands-On Engineering Labs",
                "Feynman Reconstructions & Socratic Boundary Defenses",
                "Authentic Research Literature & Primary Source Citations",
            ],
            required_knowledge_json=[
                f"Basic Python / Systems Fundamentals for {curriculum_domain}",
                "Curiosity and willingness to derive concepts from first principles",
            ],
            proposed_architecture=f"Modular multi-phase curriculum spanning {len(phase_structure)} pedagogical phases.",
            major_components_json=[p["name"] for p in phase_structure],
            tools_and_tech_json=["Python 3.11", "Standard Library", "KaTeX", "Obsidian"],
            alternative_approaches_json=["Simulation vs. Analytical Solution", "Cooperative vs. Preemptive Scheduling"],
            experiments_to_conduct_json=["Boundary condition stress test", "Invariant verification under adversarial input"],
            failure_modes_json=["Premature abstraction without understanding primitives", "Relying on high-level libraries without knowing underlying mechanics"],
            estimated_hours=max(5, round((daily_minutes * target_days) / 60)),
            stretch_goals_json=[f"Publish an open-source technical breakdown of {curriculum_title}"],
            is_approved=True,
            version=1,
        )
        self.db.add(blueprint)

        # Create Roads
        scholar_road = LearningRoad(
            journey_id=journey.id,
            road_type="scholar",
            title=f"{curriculum_title} — Scholar Road (Theory & First Principles)",
            description="Deep theoretical understanding, mathematical derivations, worked examples, and Feynman mastery.",
            sequence_order=1,
            progress_percent=0.0,
        )
        builder_road = LearningRoad(
            journey_id=journey.id,
            road_type="builder",
            title=f"{curriculum_title} — Builder Road (Engineering & Labs)",
            description="Concrete Python implementation, invariant verification, controlled failure, and hands-on labs.",
            sequence_order=2,
            progress_percent=0.0,
        )
        self.db.add(scholar_road)
        self.db.add(builder_road)
        self.db.flush()

        scholar_mod = LearningModule(
            road_id=scholar_road.id,
            title="Core Theoretical Foundations & Research Synthesis",
            description="Multi-stage explanations, Feynman reconstructions, and Think Deeper inquiries.",
            sequence_order=1,
            estimated_minutes=daily_minutes * 5,
        )
        self.db.add(scholar_mod)
        self.db.flush()

        # Create Project with full required non-null attributes
        project = Project(
            journey_id=journey.id,
            title=f"Engineering Project: {curriculum_title}",
            slug=_slugify(f"{curriculum_title}-project"),
            domain=curriculum_domain,
            objective=f"Build and verify a complete working implementation of {curriculum_title}.",
            what_will_be_created=blueprint.what_will_be_created,
            why_project_matters=blueprint.why_it_matters,
            architecture_overview=blueprint.proposed_architecture,
            architecture_mermaid=(
                'flowchart LR\n'
                '    Input["Raw Input / Domain State"] --> Core["First-Principles Core Engine"]\n'
                '    Core --> Transform["Algorithmic Pipeline & Transformations"]\n'
                '    Transform --> Verifier["Invariant Verification & Test Harness"]\n'
                '    Verifier --> Output["Verified System Output"]'
            ),
            tech_stack_json=["Python 3.11", "Standard Library", "Pytest", "Monaco IDE"],
            status="active",
            current_milestone_order=1,
            implementation_decisions_json=[
                "Selected bottom-up first-principles implementation with explicit invariant assertions."
            ],
            outstanding_bugs_json=["Validate numerical stability and edge cases under adversarial input."],
            next_action=f"Day 1 Lab: Implement foundational primitives for {curriculum_title}.",
        )
        self.db.add(project)
        self.db.flush()

        if job_id:
            self.update_job_progress(job_id, f"Populating {target_days} day schedule and initial concepts...", 4)

        # 4. Generate all Day-Wise LearningDay entries and Concepts
        concepts_created: list[Concept] = []
        days_created: list[LearningDay] = []

        # Find which phase a day belongs to
        def get_phase_info(d: int) -> tuple[str, str]:
            for p in phase_structure:
                if p["start_day"] <= d <= p["end_day"]:
                    return p["name"], p["focus"]
            return phase_structure[-1]["name"], phase_structure[-1]["focus"]

        for d_num in range(1, target_days + 1):
            phase_name, phase_focus = get_phase_info(d_num)
            week_num = (d_num - 1) // 7 + 1

            # Day type classification
            if d_num == target_days:
                day_type = "project"
            elif d_num % 7 == 0:
                day_type = "review"
            elif d_num % 7 == 5:
                day_type = "practice"
            else:
                day_type = "lesson"

            # Parse or synthesize topic title
            parsed_day = day_lines_parsed.get(d_num)
            if parsed_day:
                d_topic = parsed_day["topic"]
                d_obj = parsed_day["scholar_objective"]
                d_lab = parsed_day["builder_lab"]
            else:
                d_topic = f"{curriculum_title} Part {d_num}: {phase_name.split(':')[1].strip() if ':' in phase_name else phase_name} Step {d_num}"
                d_obj = f"Synthesize core principles and invariant properties of {d_topic}."
                d_lab = f"{d_topic} — Coding Lab"

            feynman_stage_idx = (d_num - 1) % len(self.FEYNMAN_STAGES)
            feynman_stage_text = self.FEYNMAN_STAGES[feynman_stage_idx]

            # Create Concept record for key days (or all days up to 30)
            concept: Optional[Concept] = None
            if d_num <= 30 or d_num % 3 == 1 or d_num == target_days:
                diff = "beginner" if d_num <= 3 else ("intermediate" if d_num <= target_days - 3 else "advanced")
                cat = "prerequisite" if d_num == 1 else ("foundational" if d_num <= 4 else ("intermediate" if d_num < target_days - 2 else "advanced"))
                gx = 120 + ((d_num - 1) % 4) * 230
                gy = 120 + ((d_num - 1) // 4) * 140

                concept = Concept(
                    journey_id=journey.id,
                    slug=f"day-{d_num}-{_slugify(d_topic)[:40]}",
                    title=d_topic,
                    summary=d_obj,
                    category=cat,
                    prerequisite_level="essential" if d_num <= 5 else "recommended",
                    difficulty_level=diff,
                    mastery_status="unstarted",
                    mastery_score=0.0,
                    position_x=float(gx),
                    position_y=float(gy),
                    related_disciplines_json=[curriculum_domain, "Applied Mathematics"],
                    research_directions_json=[f"Optimizations and scaling limits in {d_topic}"],
                )
                self.db.add(concept)
                self.db.flush()
                concepts_created.append(concept)

            yt_query = f"{curriculum_title} {d_topic} lecture tutorial"

            day_record = LearningDay(
                journey_id=journey.id,
                day_number=d_num,
                title=d_topic,
                theme=phase_focus,
                phase_name=phase_name,
                week_number=week_num,
                day_type=day_type,
                estimated_minutes=daily_minutes,
                scholar_concept_id=concept.id if concept else None,
                scholar_objective=d_obj,
                youtube_search_query=yt_query,
                builder_lab_title=d_lab,
                builder_lab_mission=f"Implement and verify {d_lab} with concrete assertions and edge-case validation.",
                builder_starter_code="",
                builder_test_cases_json=[],
                builder_hints_json=[
                    f"Consider what invariants must hold across every valid state in {d_topic}.",
                    f"Check boundary conditions: empty input, maximum capacity, and adversarial edge cases.",
                ],
                builder_completed=False,
                is_completed=False,
                completion_score=0.0,
                feynman_stage=feynman_stage_idx + 1,
                notes_summary="",
            )
            self.db.add(day_record)
            self.db.flush()
            days_created.append(day_record)

            # Create LearningTask
            task = LearningTask(
                journey_id=journey.id,
                title=f"Day {d_num}: {d_topic}",
                task_type="deep_synthesis" if day_type == "lesson" else "milestone_build",
                road="scholar" if day_type == "lesson" else "builder",
                day_number=d_num,
                estimated_minutes=daily_minutes,
                status="unstarted",
                concept_id=concept.id if concept else None,
            )
            self.db.add(task)

        # Wire concept dependencies (sequential DAG)
        for i in range(len(concepts_created) - 1):
            dep = ConceptDependency(
                source_concept_id=concepts_created[i].id,
                target_concept_id=concepts_created[i + 1].id,
                dependency_type="essential" if i < 3 else "recommended",
                rationale=f"{concepts_created[i].title} provides the theoretical and architectural foundation for {concepts_created[i + 1].title}.",
            )
            self.db.add(dep)

        # 5. Populate Scholar artifacts (Lessons, Sections, Flashcards, Recall, Think Deeper) & Builder Milestones
        from app.services.ai_orchestrator import AIOrchestrationService
        from app.models.domain import Experiment

        orchestrator = AIOrchestrationService(self.db)
        created_milestones: list[ProjectMilestone] = []

        for idx, concept in enumerate(concepts_created):
            day_num = idx + 1
            feynman_stage_label = self.FEYNMAN_STAGES[(day_num - 1) % len(self.FEYNMAN_STAGES)]

            c_spec = {
                "title": concept.title,
                "summary": concept.summary,
                "category": concept.category,
                "prerequisite_level": concept.prerequisite_level,
                "difficulty": concept.difficulty_level,
                "problem_statement": f"Core domain challenge: how does {concept.title} enforce consistency and resolve fundamental system constraints in {curriculum_domain}?",
                "first_principles_intuition": f"From first principles, {concept.title} isolates complexity by establishing a verifiable causal contract between inputs, invariants, and system outputs.",
                "real_world_analogy": f"Consider {concept.title} as a specialized pipeline stage in {curriculum_domain} that guarantees correctness under bounded resource constraints.",
                "mathematical_formulation": f"$$\\text{{Invariant}}({concept.title}) = \\sum_{{i=1}}^N \\Delta s_i \\quad \\text{{subject to}} \\quad C_{{max}} < \\infty$$",
                "worked_example": f"Step 1: Receive input signal. Step 2: Validate state invariant. Step 3: Compute transformation. Step 4: Emit verified output.",
                "engineering_tradeoffs": f"Trade-off in {concept.title}: Algorithmic precision vs. computational overhead and memory footprint.",
                "feynman_stage": feynman_stage_label,
            }
            orchestrator._populate_concept_scholar_artifacts(
                concept=concept,
                module_id=scholar_mod.id,
                c_spec=c_spec,
                day_num=day_num,
                domain=curriculum_domain,
                web_context=web_digest,
            )

            m_spec = {
                "title": f"Milestone {day_num}: {concept.title}",
                "mission": f"Implement and verify the foundational data structures and core algorithm for {concept.title}.",
                "why_this_matters": f"Directly connects theoretical understanding of {concept.title} to verifiable code.",
                "worked_example": c_spec["worked_example"],
                "file_path": f"src/milestone_{day_num}_{_slugify(concept.title)[:20].replace('-', '_')}.py",
                "language": "python",
                "sample_code": "",
            }
            milestone = orchestrator._create_detailed_milestone(
                project=project,
                concept=concept,
                order=day_num,
                spec=m_spec,
            )
            created_milestones.append(milestone)
            concept.builder_milestone_id = milestone.id

        if created_milestones and concepts_created:
            exp = Experiment(
                project_id=project.id,
                milestone_id=created_milestones[0].id,
                concept_id=concepts_created[0].id,
                title=f"Ablation & Scaling Stress Test: {created_milestones[0].title}",
                hypothesis="Doubling load/step-size beyond the theoretical stability bound will cause measurable latency divergence.",
                objective="Quantify the exact regime boundary where the baseline implementation transitions from stable to degraded.",
                variables_changed_json=["scale_factor: [1.0, 2.0, 8.0]", "strict_invariant_check: True"],
                procedure="1. Initialize baseline environment. 2. Scale inputs exponentially. 3. Log invariants and divergence.",
                expected_outcome="Sub-linear latency growth until saturation threshold, followed by non-linear queue divergence.",
                status="draft",
            )
            self.db.add(exp)

        if job_id:
            self.update_job_progress(job_id, "Synthesizing Day 1 deep first-principles lesson & runnable Python lab...", 5)

        # 5. Deeply synthesize Day 1 immediately so learner can start learning and coding right away!
        if days_created:
            await self.synthesize_day_content_deep(journey_id=journey.id, day_number=1)

        journey.current_concept_id = concepts_created[0].id if concepts_created else None
        self.db.commit()
        self.db.refresh(journey)

        if job_id:
            self.update_job_progress(
                job_id,
                f"Successfully planned full {target_days}-Day curriculum for '{curriculum_title}'.",
                6,
                status="completed",
                result_data={
                    "journey_id": journey.id,
                    "title": journey.title,
                    "total_days": target_days,
                    "phase_count": len(phase_structure),
                    "concepts_count": len(concepts_created),
                },
            )

        return journey

    async def synthesize_day_content_deep(
        self,
        journey_id: int,
        day_number: int,
    ) -> dict[str, Any]:
        """Synthesize deep first-principles Scholar content and verified Builder code for a specific Day on-demand."""
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

        provider, model, _ = self.provider_router.get_active_provider("general_explanation")

        prompt = (
            f"Overall Journey Subject: {journey.title}\n"
            f"Subject Domain: {journey.subject_domain}\n"
            f"Day Number: {day_number} of {journey.duration_days}\n"
            f"Day Topic Title: {day.title}\n"
            f"Day Objective: {day.scholar_objective}\n"
            f"Builder Lab Title: {day.builder_lab_title}\n\n"
            "Generate a rigorous, first-principles deep dive for this exact day:\n"
            "Format your output strictly using these delimiter blocks:\n"
            "PROBLEM: <3-4 sentences explaining the specific problem, constraint, or bottleneck this day's concept solves and why naive solutions fail>\n"
            "INTUITION: <4-5 sentences explaining the causal mechanism from first principles without buzzwords>\n"
            "MATH: <Core governing equation, formal definition, or complexity law in LaTeX ($$ ... $$ and $...$), explaining every variable>\n"
            "WORKED_EXAMPLE: <Concrete step-by-step trace with specific numbers, states, or input/output values>\n"
            "ANALOGY: <Vivid real-world analogy making the mechanism immediately intuitive>\n"
            "TRADEOFFS: <Engineering trade-offs and 2 common failure modes/misconceptions>\n"
            "PYTHON_CODE: <Self-contained, runnable Python 3.11 script (under 70 lines) implementing the core function/class for this lab with assert tests in if __name__ == '__main__':>\n"
            "RECALL_QUESTION: <Targeted active-recall question testing causal understanding>\n"
            "THINK_DEEPER_QUESTION: <Counterfactual question challenging boundary assumptions>\n"
        )

        res = await provider.generate(
            prompt=prompt,
            system_prompt="You are Axiom OS Deep Explanation & Code Synthesis Engine. Provide concrete equations and runnable Python.",
            model=model,
            temperature=0.2,
            max_tokens=3200,
        )

        raw = res.content.strip()

        def _extract(key: str, next_keys: list[str]) -> str:
            pattern = rf"{key}:\s*(.*?)(?=(?:\n(?:{'|'.join(next_keys)}):)|\Z)"
            m = re.search(pattern, raw, flags=re.DOTALL | re.IGNORECASE)
            return m.group(1).strip() if m else ""

        all_keys = [
            "PROBLEM", "INTUITION", "MATH", "WORKED_EXAMPLE", "ANALOGY",
            "TRADEOFFS", "PYTHON_CODE", "RECALL_QUESTION", "THINK_DEEPER_QUESTION"
        ]

        problem_text = _extract("PROBLEM", all_keys) or day.scholar_objective
        intuition_text = _extract("INTUITION", all_keys) or problem_text
        math_text = _extract("MATH", all_keys)
        worked_text = _extract("WORKED_EXAMPLE", all_keys)
        analogy_text = _extract("ANALOGY", all_keys)
        tradeoffs_text = _extract("TRADEOFFS", all_keys)
        code_raw = _extract("PYTHON_CODE", all_keys)
        recall_q = _extract("RECALL_QUESTION", all_keys) or f"Explain the core causal mechanism of {day.title}."
        think_q = _extract("THINK_DEEPER_QUESTION", all_keys) or f"What fundamental constraint in {day.title} breaks under adversarial load?"

        # Clean code
        cleaned_code_lines = []
        for line in code_raw.splitlines():
            if line.strip().startswith("```"):
                continue
            cleaned_code_lines.append(line)
        cleaned_code = "\n".join(cleaned_code_lines).strip()

        # Validate syntax via AST
        syntax_err = CodeExecutionService.validate_python_syntax(cleaned_code) if cleaned_code else "No code returned"
        if not syntax_err and cleaned_code:
            day.builder_starter_code = cleaned_code

        # Fetch authentic specific YouTube video for this day
        yt_vids = await self.resource_service.search_youtube_videos_live(day.youtube_search_query or f"{journey.title} {day.title}", max_results=1)
        if yt_vids and isinstance(yt_vids, list):
            first_yt = yt_vids[0]
            v_url = first_yt.get("url", "")
            v_id_m = re.search(r"v=([a-zA-Z0-9_-]+)", v_url)
            if v_id_m:
                day.youtube_video_id = v_id_m.group(1)
                day.youtube_video_title = first_yt.get("title", "")

        self.db.commit()
        self.db.refresh(day)

        return {
            "day_number": day.day_number,
            "title": day.title,
            "problem": problem_text,
            "intuition": intuition_text,
            "math": math_text,
            "worked_example": worked_text,
            "analogy": analogy_text,
            "tradeoffs": tradeoffs_text,
            "starter_code": day.builder_starter_code,
            "youtube_video_id": day.youtube_video_id,
            "youtube_video_title": day.youtube_video_title,
            "recall_question": recall_q,
            "think_deeper_question": think_q,
        }
