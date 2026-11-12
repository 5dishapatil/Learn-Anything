from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.models.domain import LearningDay, LearningJourney
from app.services.curriculum_planner import CurriculumPlannerService
from app.services.domain_intelligence import (
    DomainIntelligenceService,
    DomainType,
)


# =====================================================================
# TEST A: BEGINNER 90-DAY COMPUTATIONAL NEUROSCIENCE
# =====================================================================
def test_a_beginner_90_day_computational_neuroscience():
    """
    Test A: Beginner 90-day journey in Computational Neuroscience:
    - Starts from scratch (cell structure, electricity, membrane physics before complex equations).
    - Day 1 does NOT introduce Hodgkin-Huxley differential equations or BCI spatial filters.
    - Exactly 90 continuous days.
    - Zero generic fallbacks (no 'Part 41: Step 41', 'Synthesize core principles').
    - Matching Scholar learning outcomes and Builder tasks.
    """
    phases = [
        {"name": "Neural Primitives & Bioelectricity", "day_start": 1, "day_end": 15},
        {"name": "Synaptic Transmission & Biophysics", "day_start": 16, "day_end": 30},
        {"name": "Small Neural Circuits & Networks", "day_start": 31, "day_end": 45},
        {"name": "Sensory Coding & Signal Transduction", "day_start": 46, "day_end": 60},
        {"name": "Population Dynamics & Rate Models", "day_start": 61, "day_end": 75},
        {"name": "Cognitive Models & System Synthesis", "day_start": 76, "day_end": 90},
    ]
    days = CurriculumPlannerService.generate_domain_curriculum_days(
        user_intent="Computational Neuroscience from absolute scratch",
        domain_key=DomainType.COMPUTATIONAL_NEUROSCIENCE,
        experience_level="beginner",
        duration_days=90,
        phases=phases,
        intake_profile={"experience_level": "beginner"},
        specific_research_focus=None,
    )

    assert len(days) == 90, f"Expected exactly 90 days, got {len(days)}"

    # Day 1 Verification: Starts from primitive concepts without advanced math/jargon
    day_1 = days[0]
    assert day_1["day_number"] == 1
    day_1_text = f"{day_1['title']} {day_1.get('why_this_day', '')} {day_1.get('scholar_objective', '')}".lower()
    
    # Must NOT start with advanced differential equations or spatial filtering
    assert "hodgkin-huxley" not in day_1["title"].lower()
    assert "common spatial pattern" not in day_1["title"].lower()

    # Must contain foundational biological or physical primitives
    foundational_terms = ["cell", "neuron", "membrane", "biology", "primitive", "introduction", "signal", "potential"]
    assert any(term in day_1_text for term in foundational_terms), f"Day 1 text should introduce foundations: {day_1['title']}"

    # Verify strict continuity and ordering: 1..90
    for idx, d in enumerate(days):
        expected_day = idx + 1
        assert d["day_number"] == expected_day, f"Expected day {expected_day}, got {d['day_number']}"

        # Banned generic placeholder checks
        title = d["title"]
        assert "part " not in title.lower() or "step " not in title.lower(), f"Generic 'Part X: Step Y' detected on Day {expected_day}: {title}"
        assert "synthesize core principles" not in title.lower(), f"Generic fallback detected on Day {expected_day}: {title}"

        # Verify coupled Scholar-Builder learning outcomes
        outcomes = d.get("learning_outcomes", [])
        assert len(outcomes) >= 2, f"Day {expected_day} must have at least 2 learning outcomes"
        for o in outcomes:
            assert o["id"].startswith(f"LO-D{expected_day}"), f"Outcome ID should match day: {o['id']}"
            assert o["practice_task_id"].startswith(f"BT-D{expected_day}"), f"Practice task ID should match day: {o['practice_task_id']}"


# =====================================================================
# TEST B: INTERMEDIATE MACHINE LEARNING JOURNEY
# =====================================================================
def test_b_intermediate_machine_learning_prior_knowledge():
    """
    Test B: Intermediate Machine Learning journey factors in prior knowledge:
    - User knows Python, calculus, linear regression.
    - Day 1 skips validated basics and begins with loss geometry / regularization or advanced optimization.
    - Bridges gaps to deep neural architectures.
    """
    intake = {
        "experience_level": "intermediate",
        "prior_topics_understood": "Linear regression, multivariate calculus, gradient descent, basic NumPy",
        "tools_and_languages_used": "Python, NumPy, scikit-learn",
        "specific_gaps_to_bridge": "Matrix calculus derivations for backprop, vanishing gradient proof",
    }
    phases = DomainIntelligenceService.generate_dynamic_phases(
        DomainType.SOFTWARE_SYSTEMS, 30, "intermediate"
    )
    days = CurriculumPlannerService.generate_domain_curriculum_days(
        user_intent="Deep Learning Architectures from Scratch",
        domain_key=DomainType.SOFTWARE_SYSTEMS,
        experience_level="intermediate",
        duration_days=30,
        phases=phases,
        intake_profile=intake,
    )

    assert len(days) == 30
    day_1 = days[0]
    day_1_title = day_1["title"].lower()

    # Should not teach basic "What is a Variable in Python"
    assert "what is python" not in day_1_title
    assert "hello world" not in day_1_title

    # Should introduce intermediate concepts (loss landscape, matrix calculus, optimization, backpropagation)
    assert any(
        term in day_1_title or term in day_1.get("why_this_day", "").lower()
        for term in ["optimization", "loss", "gradient", "regularization", "linear", "tensor", "matrix", "calculus", "systems"]
    )


# =====================================================================
# TEST C: ADVANCED RESEARCH-FOCUSED JOURNEY
# =====================================================================
def test_c_advanced_research_focus_computational_neuroscience():
    """
    Test C: Advanced journey focuses on frontier research:
    - Research focus: Predictive coding & biologically plausible credit assignment.
    - Skips elementary cell anatomy and elementary programming.
    - Cites research paradigms and models.
    """
    focus = "Predictive coding, dendritic computation, and biologically plausible credit assignment"
    phases = DomainIntelligenceService.generate_dynamic_phases(
        DomainType.COMPUTATIONAL_NEUROSCIENCE, 30, "advanced"
    )
    days = CurriculumPlannerService.generate_domain_curriculum_days(
        user_intent="Frontier Biologically Plausible Learning Models",
        domain_key=DomainType.COMPUTATIONAL_NEUROSCIENCE,
        experience_level="advanced",
        duration_days=30,
        phases=phases,
        intake_profile={"experience_level": "advanced", "specific_research_focus": focus},
        specific_research_focus=focus,
    )

    assert len(days) == 30
    all_titles_and_desc = " ".join([d["title"] + " " + d.get("scholar_objective", "") for d in days]).lower()

    # Verifies high-level research terms are present
    assert any(term in all_titles_and_desc for term in ["predictive", "credit assignment", "feedback alignment", "dendritic", "plasticity", "synaptic", "population", "coding"])
    # Elementary cell structure is not the primary focus
    assert "what is an animal cell" not in all_titles_and_desc


# =====================================================================
# TEST D: CROSS-DOMAIN SCHOLAR-BUILDER ALIGNMENT
# =====================================================================
def test_d_cross_domain_scholar_builder_alignment():
    """
    Test D: Verify 6 distinct domains:
    1. Software/Systems -> code_lab
    2. Piano/Music -> piano_exercise or ear_training
    3. French/Languages -> dialogue_practice or translation_construction
    4. History -> source_analysis or historical_synthesis
    5. Mathematics -> proof_construction or derivation_lab
    6. Creative Writing -> creative_composition or prose_critique
    """
    test_domains = [
        ("Building a Distributed Raft Storage Engine in Rust", DomainType.SOFTWARE_SYSTEMS, "code_lab"),
        ("Classical Piano Technique, Scales, and Bach Inventions", DomainType.MUSIC_ARTS, "piano_exercise"),
        ("Conversational French: From Zero to Fluent", DomainType.LANGUAGES, "dialogue_practice"),
        ("The Fall of the Roman Republic and Primary Source Historiography", DomainType.HISTORY_HUMANITIES, "source_analysis"),
        ("Abstract Algebra and Galois Theory from First Principles", DomainType.MATHEMATICS, "proof_construction"),
        ("Craft of Literary Fiction & Narrative Voice", DomainType.WRITING_LITERATURE, "creative_composition"),
    ]

    for topic, expected_domain, expected_activity_prefix in test_domains:
        inferred_domain = DomainIntelligenceService.infer_domain(topic)
        assert inferred_domain == expected_domain, f"Failed domain inference for {topic}: got {inferred_domain}"

        phases = DomainIntelligenceService.generate_dynamic_phases(inferred_domain, 7, "beginner")
        assert len(phases) >= 1
        # Dynamic phase names must not use generic software engineering phases
        if expected_domain == DomainType.MUSIC_ARTS:
            assert any(term in p["name"] for term in ["Technique", "Harmony", "Aural", "Performance", "Sound", "Geography", "Posture"] for p in phases)
        elif expected_domain == DomainType.LANGUAGES:
            assert any(term in p["name"] for term in ["Phonetics", "Vocabulary", "Grammar", "Dialogue", "Pronunciation"] for p in phases)
        elif expected_domain == DomainType.HISTORY_HUMANITIES:
            assert any(term in p["name"] for term in ["Historiography", "Evidence", "Synthesis", "Sources"] for p in phases)

        days = CurriculumPlannerService.generate_domain_curriculum_days(
            user_intent=topic,
            domain_key=str(inferred_domain),
            experience_level="beginner",
            duration_days=7,
            phases=phases,
        )
        assert len(days) == 7
        domain_key_str = str(inferred_domain)
        for d in days:
            activity = d["builder_activity_type"]
            assert (
                expected_activity_prefix in activity
                or activity in DomainIntelligenceService.DOMAINS[domain_key_str].builder_activity_types
                or activity == DomainIntelligenceService.DOMAINS[domain_key_str].default_builder_activity
            ), f"Activity {activity} not appropriate for {expected_domain}"


# =====================================================================
# TEST E: DURATION SCALING ACROSS 7, 15, 30, 90, 180, 365 DAYS
# =====================================================================
def test_e_duration_scaling_all_intervals():
    """
    Test E: Duration scaling works across 7, 15, 30, 90, 180, 365 days
    without dropping days or producing missing sequences.
    """
    dummy_planner = CurriculumPlannerService(db=None)  # type: ignore
    for duration in [7, 15, 30, 90, 180, 365]:
        phases = DomainIntelligenceService.generate_dynamic_phases(
            DomainType.SOFTWARE_SYSTEMS, duration, "intermediate"
        )
        assert len(phases) >= 1, f"Failed phases for duration {duration}"
        assert phases[0]["start_day"] == 1
        assert phases[-1]["end_day"] == duration

        # Verify batch slicing covers exactly the duration
        slices = dummy_planner._calculate_batches(duration)
        total_sliced_days = sum(s[1] - s[0] + 1 for s in slices)
        assert total_sliced_days == duration, f"Slices did not sum to {duration}"


# =====================================================================
# TEST F: BATCH TRUNCATION & QUALITY AUDIT
# =====================================================================
def test_f_batch_truncation_and_quality_audit():
    """
    Test F: Batch quality validator detects and rejects:
    - Truncated batches (missing expected days)
    - Generic placeholders ('Part 10: Step 10')
    - Duplicate day numbers
    """
    dummy_planner = CurriculumPlannerService(db=None)  # type: ignore
    profile = DomainIntelligenceService.DOMAINS["computational_neuroscience"]
    phases = [{"name": "Phase 1: Foundations", "start_day": 1, "end_day": 2}]

    valid_batch = [
        {
            "day_number": 1,
            "title": "Introduction to Biological Neurons",
            "theme": "Biophysics",
            "phase_name": "Phase 1: Foundations",
            "week_number": 1,
            "day_type": "theory_and_lab",
            "estimated_minutes": 60,
            "why_this_day": "Establishes physical basis of neural membrane potential.",
            "learning_outcomes": [
                {"id": "LO-D1-1", "title": "Membrane Nernst Potential", "description": "Derive the Nernst equilibrium equation.", "practice_task_id": "BT-D1-1"}
            ],
            "builder_activity_type": "code_lab",
            "builder_lab_title": "Simulate Nernst Resting Potential",
            "builder_lab_mission": "Compute equilibrium voltages across ion gradients.",
            "builder_starter_code": "def nernst_potential(z, cout, cin): return 0.0",
            "builder_test_cases": [{"name": "Equilibrium Voltage", "test_type": "unit"}],
        },
        {
            "day_number": 2,
            "title": "Voltage-Gated Ion Channel Dynamics",
            "theme": "Biophysics",
            "phase_name": "Phase 1: Foundations",
            "week_number": 1,
            "day_type": "theory_and_lab",
            "estimated_minutes": 60,
            "why_this_day": "Transitions from static membrane to dynamic channel conductance.",
            "learning_outcomes": [
                {"id": "LO-D2-1", "title": "Gating Probabilities", "description": "Formulate m, h, and n gate kinetics.", "practice_task_id": "BT-D2-1"}
            ],
            "builder_activity_type": "code_lab",
            "builder_lab_title": "Implement Ion Gating Kinetics",
            "builder_lab_mission": "Calculate channel open state probabilities.",
            "builder_starter_code": "def alpha_n(v): return 0.0",
            "builder_test_cases": [{"name": "Gating rate transitions", "test_type": "unit"}],
        },
    ]

    # Valid batch passes
    assert dummy_planner._validate_and_fill_batch(valid_batch, 1, 2, profile, "Neuroscience", phases) is not None

    # Truncated batch fails (only 1 day returned when 2 expected)
    assert dummy_planner._validate_and_fill_batch([valid_batch[0]], 1, 2, profile, "Neuroscience", phases) is None

    # Placeholder batch fails
    placeholder_batch = [
        dict(valid_batch[0], title="Part 1: Step 1 Introduction"),
        valid_batch[1],
    ]
    assert dummy_planner._validate_and_fill_batch(placeholder_batch, 1, 2, profile, "Neuroscience", phases) is None

    # Missing expected day number fails
    missing_day_batch = [
        valid_batch[0],
        dict(valid_batch[1], day_number=99),
    ]
    assert dummy_planner._validate_and_fill_batch(missing_day_batch, 1, 2, profile, "Neuroscience", phases) is None


# =====================================================================
# TEST G: PREREQUISITE GRAPH DAG ACYCLICITY (KAHN'S ALGORITHM)
# =====================================================================
def test_g_prerequisite_graph_dag_acyclicity():
    """
    Test G: Topological sort validates acyclicity of concept dependency graph.
    Detects circular dependencies cleanly.
    """
    # 1. Acyclic Graph
    acyclic_nodes = [
        {"id": "1", "prerequisites": []},
        {"id": "2", "prerequisites": ["1"]},
        {"id": "3", "prerequisites": ["1", "2"]},
        {"id": "4", "prerequisites": ["3"]},
    ]
    is_acyclic, order = DomainIntelligenceService.validate_prerequisite_graph_acyclic(acyclic_nodes)
    assert is_acyclic is True
    assert order == ["1", "2", "3", "4"]

    # 2. Cyclic Graph: 1 -> 2 -> 3 -> 1
    cyclic_nodes = [
        {"id": "1", "prerequisites": ["3"]},
        {"id": "2", "prerequisites": ["1"]},
        {"id": "3", "prerequisites": ["2"]},
    ]
    is_acyclic, order = DomainIntelligenceService.validate_prerequisite_graph_acyclic(cyclic_nodes)
    assert is_acyclic is False
    assert len(order) < len(cyclic_nodes)


# =====================================================================
# TEST H: INTEGRATED ENDPOINT & LEARNINGDAY SOURCE OF TRUTH
# =====================================================================
def test_h_journey_day_and_verify_lab_api(client: TestClient):
    """
    Test H: LearningDay as single source of truth:
    1. Journey creation generates LearningDays with intake profile.
    2. GET /api/v1/journeys/{id}/days returns day details with why_this_day, learning_outcomes, markdown.
    3. POST /api/v1/journeys/{id}/days/{day_number}/verify-lab runs code in isolated sandbox.
    4. Reports discrete test case results and honest sandbox label.
    5. POST /api/v1/journeys/{id}/days/{day_number}/complete updates day and journey progress.
    """
    payload = {
        "user_intent": "Quantum Qubit Computing & Algorithms",
        "experience_level": "beginner",
        "daily_minutes": 60,
        "duration_days": 7,
        "road_mode": "hybrid",
        "preferred_format": "combined",
        "intake_profile": {
            "experience_level": "beginner",
            "target_next_level_goal": "Simulate Grover search and Bell state entanglement",
        },
    }
    from unittest.mock import patch
    from app.providers.base import GenerationResult

    async def mock_generate(*args, **kwargs):
        return GenerationResult(
            content="""PROBLEM: Quantum superposition is fundamental to quantum advantage.
INTUITION: Qubits exist in linear combinations of orthonormal states |0> and |1>.
FORMAL_SPEC: $$|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$$ where $$|\\alpha|^2 + |\\beta|^2 = 1$$
WORKED_EXAMPLE: For Hadamard gate applied to |0>, state becomes (|0> + |1>)/sqrt(2).
ANALOGY: A spinning coin in flight having both probabilities before landing.
TRADEOFFS: Phase coherence vs environmental measurement noise.
CODE_OR_PRACTICE:
def compute_superposition():
    return 1.0 / (2.0 ** 0.5)

if __name__ == '__main__':
    amp = compute_superposition()
    assert abs(amp - 0.707106) < 0.001
    print('[TEST CASE 1 PASS]')
    print('[TEST CASE 2 PASS]')
    print('[TEST CASE 3 PASS]')
RECALL_QUESTION: What is the normalization condition of a pure qubit state vector?
THINK_DEEPER_QUESTION: Why does the No-Cloning theorem prohibit copying unknown quantum states?
""",
            provider="ollama",
            model="qwen3.5:9b",
            is_local=True,
            tokens_estimated=200,
            generation_status="completed",
        )

    with patch("app.providers.ollama_provider.OllamaProvider.generate", side_effect=mock_generate):
        resp = client.post("/api/v1/journeys", json=payload)
    assert resp.status_code == 200, f"Journey creation failed: {resp.text}"
    journey = resp.json()
    journey_id = journey["id"]

    assert journey["duration_days"] == 7
    assert len(journey["days"]) == 7

    # Verify Day 1 has deep synthesis data
    day_1 = journey["days"][0]
    assert day_1["day_number"] == 1
    assert "why_this_day" in day_1
    assert "learning_outcomes" in day_1
    assert len(day_1["learning_outcomes"]) >= 2

    # Verify Day 1 Lab Verification Endpoint with code
    python_lab_code = """
def compute_superposition():
    return 1.0 / (2.0 ** 0.5)

if __name__ == '__main__':
    amp = compute_superposition()
    assert abs(amp - 0.707106) < 0.001
    print('[TEST CASE 1 PASS]')
    print('[TEST CASE 2 PASS]')
    print('[TEST CASE 3 PASS]')
"""
    verify_resp = client.post(
        f"/api/v1/journeys/{journey_id}/days/1/verify-lab",
        json={"code": python_lab_code, "timeout_seconds": 10},
    )
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()

    assert verify_data["day_number"] == 1
    assert verify_data["passed"] is True
    assert "subprocess_isolated_env_sanitized" in verify_data["execution_engine"]
    assert len(verify_data["test_case_results"]) >= 1

    # Verify Day Completion endpoint
    comp_resp = client.post(f"/api/v1/journeys/{journey_id}/days/1/complete")
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert comp_data["is_completed"] is True
    assert comp_data["progress_percent"] > 0
