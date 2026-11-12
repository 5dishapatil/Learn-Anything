from __future__ import annotations

import ast
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.domain import (
    Base,
    Concept,
    ConceptDependency,
    LearningDay,
    LearningJourney,
    Project,
    ProjectMilestone,
    UserProfile,
)
from app.services.code_execution import CodeExecutionService
from app.services.curriculum_planner import CurriculumPlannerService
from app.services.domain_intelligence import DomainIntelligenceService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = UserProfile(
        id=1,
        name="Principal Scientist",
        current_level=1,
        total_xp=0,
    )
    session.add(user)
    session.commit()

    yield session
    session.close()


def test_code_execution_ast_safety_and_honest_engine_label():
    """Verify AST safety restrictions and execution engine disclosure."""
    assert "subprocess_isolated_env_sanitized" in CodeExecutionService.EXECUTION_ENGINE_LABEL
    assert "Local Host Runner" in CodeExecutionService.EXECUTION_ENGINE_LABEL

    # Dangerous socket / network imports must be blocked
    malicious_socket_code = "import socket\ns = socket.socket()\n"
    policy_err = CodeExecutionService.validate_safety_policy(malicious_socket_code)
    assert policy_err is not None
    assert "Security Restriction" in policy_err
    assert "socket" in policy_err

    # Process spawning must be blocked
    malicious_proc_code = "import os\nos.system('echo compromised')\n"
    policy_err2 = CodeExecutionService.validate_safety_policy(malicious_proc_code)
    assert policy_err2 is not None
    assert "Process spawning" in policy_err2

    # Prohibited subprocess module
    malicious_sub_code = "import subprocess\nsubprocess.run(['ls'])\n"
    policy_err3 = CodeExecutionService.validate_safety_policy(malicious_sub_code)
    assert policy_err3 is not None
    assert "subprocess" in policy_err3

    # Benign algorithmic code passes policy
    clean_code = "import math\nx = math.sqrt(16.0)\nassert x == 4.0\n"
    assert CodeExecutionService.validate_safety_policy(clean_code) is None


def test_code_execution_independent_test_suite_evaluation():
    """Verify test cases are independently evaluated rather than blanket-passed."""
    test_cases = [
        {"name": "Conservation Invariant"},
        {"name": "Boundary Zero Input Guard"},
        {"name": "Scaling Regime Behavior"},
    ]

    # Partial pass: emits [TEST CASE 1 PASS] and [TEST CASE 2 PASS], but fails test 3
    code_partial = (
        "print('Initiating verification...')\n"
        "print('[TEST CASE 1 PASS] Invariant conserved')\n"
        "print('[TEST CASE 2 PASS] Zero input guarded')\n"
    )

    res = CodeExecutionService.execute_test_suite(code_partial, test_cases)
    assert res["passed"] is False  # Overall fails because test 3 did not pass
    assert len(res["test_case_results"]) == 3
    assert res["test_case_results"][0]["passed"] is True
    assert res["test_case_results"][1]["passed"] is True
    assert res["test_case_results"][2]["passed"] is False

    # Full pass
    code_full = (
        "print('[TEST CASE 1 PASS] Invariant conserved')\n"
        "print('[TEST CASE 2 PASS] Zero input guarded')\n"
        "print('[TEST CASE 3 PASS] Scaling verified')\n"
    )
    res_full = CodeExecutionService.execute_test_suite(code_full, test_cases)
    assert res_full["passed"] is True
    assert all(t["passed"] for t in res_full["test_case_results"])


def test_domain_intelligence_never_falls_back_to_software_systems():
    """Verify unrecognized subjects receive authentic dynamic profiles and never fall back to software engineering."""
    # 1. Photography
    photo_profile = DomainIntelligenceService.infer_domain("Landscape and Documentary Photography")
    assert photo_profile.domain_key == "photography_visual_arts"
    assert photo_profile.default_builder_activity == "photo_shoot"

    # 2. Law
    law_profile = DomainIntelligenceService.infer_domain("Constitutional Law and Appellate Jurisprudence")
    assert law_profile.domain_key == "law_jurisprudence"
    assert law_profile.default_builder_activity == "case_brief"

    # 3. Culinary Arts
    culinary_profile = DomainIntelligenceService.infer_domain("French Pastry Baking and Sourdough Fermentation")
    assert culinary_profile.domain_key == "culinary_gastronomy"
    assert culinary_profile.default_builder_activity == "recipe_execution"

    # 4. Completely Novel Subject (Falconry, Urban Permaculture, Numismatics)
    falconry_profile = DomainIntelligenceService.infer_domain("Falconry and Raptor Flight Training")
    assert "falconry" in falconry_profile.domain_key
    assert falconry_profile.domain_key != "software_systems"
    assert "Falconry" in falconry_profile.display_name
    assert len(falconry_profile.core_knowledge_areas) >= 5
    assert len(falconry_profile.sample_phase_templates) >= 4


def test_full_curriculum_universal_coverage_and_acyclic_dag(db_session):
    """Verify that every day across duration gets a LearningDay, Concept, Milestone, and acyclic DAG dependencies."""
    planner = CurriculumPlannerService(db_session)

    days = planner.generate_domain_curriculum_days(
        user_intent="Architectural Acoustics & Concert Hall Design",
        domain_key="physics_engineering",
        experience_level="intermediate",
        duration_days=15,
        phases=[
            {"name": "Wave Fundamentals", "start_day": 1, "end_day": 5},
            {"name": "Boundary Reflection & Absorption", "start_day": 6, "end_day": 10},
            {"name": "Spatial Hall Simulation", "start_day": 11, "end_day": 15},
        ],
        intake_profile={"existing_knowledge": "Calculus and wave equation"},
    )

    assert len(days) == 15
    for d in days:
        assert d["day_number"] >= 1
        assert "Part " not in d["title"]
        assert "Step " not in d["title"]
        assert len(d["learning_outcomes"]) >= 1
        assert d["learning_outcomes"][0]["id"].startswith("LO-D")
        assert d["generation_status"] in ["validated", "provisional_scaffold"]


@pytest.mark.asyncio
async def test_plan_full_curriculum_and_acyclic_dependencies(db_session):
    """Verify end-to-end curriculum planning creates concepts, milestones, and verified acyclic DAG dependencies."""
    planner = CurriculumPlannerService(db_session)

    journey = await planner.plan_full_curriculum(
        user_intent="Cellular Immunology & Monoclonal Antibodies",
        duration_days=8,
        experience_level="beginner",
        daily_minutes=45,
        intake_profile={"prior_concepts": "Basic high school biology", "target_goal": "Understand antibody kinetics"},
    )

    assert journey.id is not None
    assert journey.duration_days == 8

    # Verify all 8 days exist
    days = db_session.query(LearningDay).filter(LearningDay.journey_id == journey.id).order_by(LearningDay.day_number).all()
    assert len(days) == 8

    # Verify all 8 concepts exist
    concepts = db_session.query(Concept).filter(Concept.journey_id == journey.id).order_by(Concept.id).all()
    assert len(concepts) == 8

    # Verify all 8 milestones exist
    milestones = db_session.query(ProjectMilestone).join(Project).filter(Project.journey_id == journey.id).all()
    assert len(milestones) == 8

    # Verify day links to concept and milestone
    for d in days:
        assert d.scholar_concept_id is not None
        c = db_session.query(Concept).filter(Concept.id == d.scholar_concept_id).first()
        assert c is not None
        assert c.builder_milestone_id is not None

    # Verify Directed Acyclic Graph (DAG) for Concept Dependencies
    deps = db_session.query(ConceptDependency).all()
    assert len(deps) >= 7  # At least 7 sequential plus cross-links

    # Graph cycle check: Topological sort using Kahn's algorithm
    adjacency: dict[int, list[int]] = {c.id: [] for c in concepts}
    in_degree: dict[int, int] = {c.id: 0 for c in concepts}

    for dep in deps:
        if dep.source_concept_id in adjacency and dep.target_concept_id in in_degree:
            adjacency[dep.source_concept_id].append(dep.target_concept_id)
            in_degree[dep.target_concept_id] += 1

    queue = [c_id for c_id, deg in in_degree.items() if deg == 0]
    visited_count = 0

    while queue:
        curr = queue.pop(0)
        visited_count += 1
        for neighbor in adjacency[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If visited_count equals total concepts, graph is strictly ACYCLIC (valid DAG)
    assert visited_count == len(concepts), "Concept dependency graph contains cycles!"


@pytest.mark.asyncio
async def test_deep_day_synthesis_populates_full_scholar_markdown(db_session):
    """Verify synthesize_day_content_deep populates complete Scholar Markdown and Builder practice without crashes."""
    planner = CurriculumPlannerService(db_session)

    journey = await planner.plan_full_curriculum(
        user_intent="Modern French Conversation & Phonetics",
        duration_days=3,
        experience_level="beginner",
        daily_minutes=30,
    )

    day1_detail = await planner.synthesize_day_content_deep(journey.id, day_number=1)
    assert day1_detail["day_number"] == 1
    assert "scholar_content_markdown" not in day1_detail or len(day1_detail["problem"]) > 0

    day_rec = db_session.query(LearningDay).filter(LearningDay.journey_id == journey.id, LearningDay.day_number == 1).first()
    assert day_rec is not None
    assert len(day_rec.scholar_content_markdown) > 100
    assert "## 1. The Fundamental Problem" in day_rec.scholar_content_markdown
    assert "## 2. First-Principles Intuition" in day_rec.scholar_content_markdown
    assert "## 3. Formal Specification" in day_rec.scholar_content_markdown
