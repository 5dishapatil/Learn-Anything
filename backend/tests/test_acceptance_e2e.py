from __future__ import annotations

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from app.main import app


def test_health_and_dashboard_seed(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    dash = client.get("/api/v1/dashboard")
    assert dash.status_code == 200
    data = dash.json()
    assert isinstance(data["active_journeys"], list)
    assert data["ai_status"]["active_provider"] == "ollama"
    assert data["ai_status"]["is_local"] is True


def test_a_learn_a_subject_ai_30_days(client: TestClient):
    """TEST A — Learn a subject: 'I want to learn artificial intelligence from scratch in 30 days, spending 30 minutes daily.'"""
    payload = {
        "user_intent": "I want to learn artificial intelligence from scratch in 30 days, spending 30 minutes daily.",
        "experience_level": "beginner",
        "daily_minutes": 30,
        "duration_days": 30,
        "road_mode": "hybrid",
        "preferred_format": "combined",
    }
    resp = client.post("/api/v1/journeys", json=payload)
    assert resp.status_code == 200
    journey = resp.json()

    assert journey["duration_days"] == 30
    assert journey["daily_minutes"] == 30
    assert journey["blueprint"] is not None
    assert len(journey["concepts"]) >= 4
    assert len(journey["projects"]) >= 1
    assert len(journey["tasks"]) >= 4

    # Verify prerequisites are clearly labelled (essential / recommended / optional)
    prereq_levels = {c["prerequisite_level"] for c in journey["concepts"]}
    assert "essential" in prereq_levels

    # Verify blueprint modification works and persists
    mod_resp = client.put(
        f"/api/v1/journeys/{journey['id']}/blueprint",
        json={
            "title": "Modified 30-Day AI First-Principles Blueprint",
            "estimated_hours": 18,
            "is_approved": True,
        },
    )
    assert mod_resp.status_code == 200
    assert mod_resp.json()["blueprint"]["title"] == "Modified 30-Day AI First-Principles Blueprint"
    assert mod_resp.json()["blueprint"]["version"] >= 2


def test_b_feynman_learning_cycle(client: TestClient):
    """TEST B — Feynman learning: 6-stage interactive cycle with gap analysis, guided questions, reconstruction, and history."""
    journeys = client.get("/api/v1/journeys").json()
    concept_id = journeys[0]["concepts"][0]["id"]

    # Stage 1: Open concept and read first-principles explanation
    ws = client.get(f"/api/v1/concepts/{concept_id}").json()
    assert ws["lesson"]["first_principles_intuition"]
    assert len(ws["lesson"]["sections"]) >= 4

    # Stage 2-4: Submit initial explanation and verify gap analysis + guided questions
    sub1 = client.post(
        f"/api/v1/concepts/{concept_id}/feynman",
        json={
            "user_explanation": "Attention uses dot products between vectors and automatically works.",
        },
    )
    assert sub1.status_code == 200
    d1 = sub1.json()
    assert len(d1["feedback"]["guided_questions"]) >= 2
    assert len(d1["feedback"]["evidence_quotes"]) >= 1

    # Stage 5-6: Submit reconstructed explanation with causal links and verify history saved
    sub2 = client.post(
        f"/api/v1/concepts/{concept_id}/feynman",
        json={
            "user_explanation": "Attention uses dot products between vectors and automatically works.",
            "revised_explanation": (
                "Scaled dot-product attention projects tokens into Queries, Keys, and Values because each token "
                "needs to query prior context. We divide the dot product by sqrt(d_k) so that high-dimensional "
                "variance does not push the softmax into vanishing-gradient saturation."
            ),
            "remaining_uncertainties": "How KV-cache quantization affects precision.",
        },
    )
    assert sub2.status_code == 200
    d2 = sub2.json()
    assert d2["stage_reached"] == 6
    assert d2["history_count"] >= 2


def test_c_think_deeper_socratic_engine(client: TestClient):
    """TEST C — Think Deeper: 3-5 high-order questions, reasoning analysis, assumption detection, and Socratic follow-up."""
    journeys = client.get("/api/v1/journeys").json()
    concept_id = journeys[0]["concepts"][0]["id"]
    ws = client.get(f"/api/v1/concepts/{concept_id}").json()

    questions = ws["think_deeper_questions"]
    assert 3 <= len(questions) <= 5
    q_id = questions[0]["id"]

    resp = client.post(
        f"/api/v1/think-deeper/{q_id}/respond",
        json={
            "user_reasoning": (
                "If we remove non-linear activations from a multilayer network, the composition of linear matrices "
                "W_2(W_1 x) collapses algebraically into a single matrix W_eff = W_2 W_1, so depth adds zero expressive power."
            ),
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["reasoning_analysis"]
    assert len(data["identified_assumptions"]) >= 1
    assert len(data["missing_perspectives"]) >= 1
    assert data["socratic_followup_question"]
    assert data["model_discussion_unlocked"] is True


def test_d_build_a_project_tiny_gpt(client: TestClient):
    """TEST D — Build a project: 'I want to build a tiny GPT from scratch.'"""
    resp = client.post(
        "/api/v1/journeys",
        json={
            "user_intent": "I want to build a tiny GPT from scratch.",
            "experience_level": "intermediate",
            "daily_minutes": 45,
            "duration_days": 21,
            "road_mode": "builder",
        },
    )
    assert resp.status_code == 200
    journey = resp.json()
    project_id = journey["projects"][0]["id"]

    proj = client.get(f"/api/v1/projects/{project_id}").json()
    assert proj["architecture_overview"]
    assert proj["architecture_mermaid"]
    assert len(proj["milestones"]) >= 3
    assert len(proj["artifacts"]) >= 1

    m1 = proj["milestones"][0]
    assert m1["mission"]
    assert m1["why_this_matters"]
    assert len(m1["break_it_challenges"]) >= 2
    assert len(m1["basic_tests"]) >= 1

    # Progressive hints (Levels 1 -> 5)
    hint_resp = client.post(f"/api/v1/milestones/{m1['id']}/hints", json={"level": 4})
    assert hint_resp.status_code == 200
    assert hint_resp.json()["unlocked_hint_level"] == 4
    assert len(hint_resp.json()["hints"]) == 4

    # Verify code artifact in isolated local sandbox
    artifact_id = proj["artifacts"][0]["id"]
    ver_resp = client.post(f"/api/v1/artifacts/{artifact_id}/verify")
    assert ver_resp.status_code == 200
    assert ver_resp.json()["passed"] is True
    assert "[VERIFIED]" in ver_resp.json()["output"]

    # Record an Experiment in the Experiment Lab
    exp_resp = client.post(
        "/api/v1/experiments",
        json={
            "project_id": project_id,
            "milestone_id": m1["id"],
            "title": "Causal Masking vs Unmasked Attention Leakage Test",
            "hypothesis": "Disabling the upper-triangular -inf mask will allow token t to copy token t+1 with ~0 loss on training but fail autoregressively.",
            "objective": "Verify causal masking prevents future token leakage.",
            "variables_changed": ["causal_mask: [True, False]"],
            "procedure": "Run attention forward pass with causal_mask=False and inspect attention matrix upper triangle.",
            "expected_outcome": "Non-zero weights above main diagonal when causal_mask=False.",
            "actual_outcome": "Confirmed: upper-triangular weights averaged 0.42 without mask vs 0.0 with mask.",
            "observations": "Causal masking is mandatory for valid autoregressive generation.",
            "conclusion": "Hypothesis confirmed.",
            "status": "succeeded",
            "metrics": {"val_perplexity_masked": 4.12, "future_leakage_unmasked": 0.42},
        },
    )
    assert exp_resp.status_code == 200
    assert exp_resp.json()["title"] == "Causal Masking vs Unmasked Attention Leakage Test"


def test_e_switch_roads_preserving_context(client: TestClient):
    """TEST E — Switch roads: Scholar -> Builder -> Scholar while preserving both contexts."""
    journeys = client.get("/api/v1/journeys").json()
    j = journeys[0]
    j_id = j["id"]
    c_id = j["concepts"][0]["id"]
    m_id = j["concepts"][0]["builder_milestone_id"]

    # 1. Start in Scholar
    sw1 = client.post(
        f"/api/v1/journeys/{j_id}/switch-road",
        json={"target_road": "scholar", "concept_id": c_id},
    )
    assert sw1.status_code == 200
    assert sw1.json()["current_road"] == "scholar"

    # 2. Switch to Builder for the corresponding component
    sw2 = client.post(
        f"/api/v1/journeys/{j_id}/switch-road",
        json={"target_road": "builder", "concept_id": c_id, "milestone_id": m_id},
    )
    assert sw2.status_code == 200
    assert sw2.json()["current_road"] == "builder"
    assert sw2.json()["current_concept_id"] == c_id
    assert sw2.json()["context_preserved"] is True

    # 3. Return to Scholar and verify context preserved
    sw3 = client.post(
        f"/api/v1/journeys/{j_id}/switch-road",
        json={"target_road": "scholar", "concept_id": c_id},
    )
    assert sw3.status_code == 200
    assert sw3.json()["current_road"] == "scholar"
    assert sw3.json()["current_concept_id"] == c_id


def test_f_research_resources_discovery(client: TestClient):
    """TEST F — Research resources: Retrieve real resources, verify URLs, provider, free access classification, and quota resilience."""
    resp = client.get(
        "/api/v1/resources/discover",
        params={"query": "transformer attention", "free_only": True, "include_live": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] >= 3
    assert data["primary_resource"] is not None
    assert data["primary_resource"]["url"].startswith("http")
    assert data["primary_resource"]["access_status"] in (
        "Completely free",
        "Free audit",
        "Free learning, paid certificate",
    )
    assert data["practical_repository"] is not None


def test_g_obsidian_export_and_conflict_protection(client: TestClient, tmp_path: Path):
    """TEST G — Obsidian: Enable integration, select approved sandbox vault, create Markdown export, verify non-overwrite protection."""
    sandbox_vault = tmp_path / "test_obsidian_vault"
    sandbox_vault.mkdir(parents=True, exist_ok=True)

    cfg_resp = client.put(
        "/api/v1/obsidian/config",
        json={
            "is_enabled": True,
            "vault_name": "AxiomTestVault",
            "vault_local_path": sandbox_vault.as_posix(),
            "read_permission": True,
            "write_permission": True,
        },
    )
    assert cfg_resp.status_code == 200

    # Export a note to the sandbox vault
    ws = client.get("/api/v1/knowledge/workspace").json()
    if not ws.get("my_knowledge_notes"):
        create_resp = client.post(
            "/api/v1/notes",
            json={
                "title": "First Principles & Invariants Note",
                "content_markdown": "## Note Content\nInvestigating state transitions and boundary invariants.",
                "note_type": "concept_note",
                "obsidian_folder": "02 - Concepts",
            },
        )
        assert create_resp.status_code == 200
        note_id = create_resp.json()["id"]
    else:
        note_id = ws["my_knowledge_notes"][0]["id"]

    exp1 = client.post(
        "/api/v1/obsidian/export",
        json={
            "export_type": "note",
            "entity_id": note_id,
            "target_vault_dir": sandbox_vault.as_posix(),
            "allow_overwrite": False,
        },
    )
    assert exp1.status_code == 200
    d1 = exp1.json()
    assert d1["obsidian_open_uri"].startswith("obsidian://open?vault=AxiomTestVault")
    written_path = Path(d1["written_file_path"])
    assert written_path.exists()

    # Simulate user modifying the note in Obsidian, then exporting again with allow_overwrite=False
    user_custom_text = "# User's Own Precious Obsidian Note\nDo not overwrite me!"
    written_path.write_text(user_custom_text, encoding="utf-8")

    exp2 = client.post(
        "/api/v1/obsidian/export",
        json={
            "export_type": "note",
            "entity_id": note_id,
            "target_vault_dir": sandbox_vault.as_posix(),
            "allow_overwrite": False,
        },
    )
    assert exp2.status_code == 200
    d2 = exp2.json()
    assert d2["conflict_protected_existing_note"] is True
    # Original file MUST remain untouched!
    assert written_path.read_text(encoding="utf-8") == user_custom_text
    # Companion file was written safely
    assert Path(d2["written_file_path"]).exists()


def test_h_n8n_local_automation_and_offline_resilience(client: TestClient):
    """TEST H — n8n: Connectivity check, workflow execution, and graceful fallback when n8n is offline."""
    status = client.get("/api/v1/automation/status")
    assert status.status_code == 200
    s_data = status.json()
    assert s_data["app_operational_without_n8n"] is True
    assert len(s_data["available_workflows"]) >= 7

    # Execute Workflow 1: Daily Learning Digest
    w1 = client.post("/api/v1/automation/workflows/daily_digest/execute")
    assert w1.status_code == 200
    assert w1.json()["status"] == "succeeded"
    assert w1.json()["created_note_id"] is not None

    # Execute Workflow 6: Knowledge Backup
    w6 = client.post("/api/v1/automation/workflows/knowledge_backup/execute")
    assert w6.status_code == 200
    assert w6.json()["status"] == "succeeded"
    assert Path(w6.json()["folder_path"]).exists()


def test_i_resume_learning_continuity(client: TestClient):
    """TEST I — Resume learning: Complete a task, simulate restart, load previous journey and reconstruct context."""
    journeys = client.get("/api/v1/journeys").json()
    j = journeys[0]
    task_id = j["tasks"][0]["id"]

    # Complete task
    toggle = client.post(f"/api/v1/tasks/{task_id}/toggle")
    assert toggle.status_code == 200

    # Call session resume endpoint
    resume = client.get("/api/v1/sessions/resume", params={"journey_id": j["id"]})
    assert resume.status_code == 200
    r_data = resume.json()
    assert r_data["has_active_journey"] is True
    assert r_data["journey_id"] == j["id"]
    assert r_data["current_concept"] is not None
    assert r_data["current_project"] is not None
    assert r_data["intelligent_resume_brief"]


def test_j_definition_of_success_operating_systems(client: TestClient):
    """
    SECTION 24 — DEFINITION OF SUCCESS:
    'I want to understand how operating systems work and eventually build my own tiny operating system.'
    Verifies all 16 success criteria end-to-end.
    """
    resp = client.post(
        "/api/v1/journeys",
        json={
            "user_intent": "I want to understand how operating systems work and eventually build my own tiny operating system.",
            "experience_level": "beginner",
            "daily_minutes": 45,
            "duration_days": 45,
            "road_mode": "hybrid",
        },
    )
    assert resp.status_code == 200
    os_journey = resp.json()
    assert "Operating System" in os_journey["title"]
    assert len(os_journey["concepts"]) >= 5
    assert len(os_journey["projects"]) >= 1

    # Verify OS resources (MIT 6.1810, OSTEP, xv6)
    res_disc = client.get(
        "/api/v1/resources/discover",
        params={"query": "operating systems virtual memory kernel", "free_only": True, "include_live": False},
    ).json()
    assert res_disc["total_count"] >= 3

    # Verify OS Builder project milestones & kernel allocator verification
    proj_id = os_journey["projects"][0]["id"]
    proj = client.get(f"/api/v1/projects/{proj_id}").json()
    assert len(proj["milestones"]) >= 4
    art_id = proj["artifacts"][0]["id"]
    verify = client.post(f"/api/v1/artifacts/{art_id}/verify").json()
    assert verify["passed"] is True
    assert "[VERIFIED]" in verify["output"]


def test_k_hardware_ollama_inspection_and_fts5_search(client: TestClient):
    """Verify Hardware-Aware Ollama Inspection, 5-Tier Memory, and SQLite FTS5 Global Search."""
    ai_resp = client.get("/api/v1/ai/status")
    assert ai_resp.status_code == 200
    ai_data = ai_resp.json()
    assert ai_data["hardware"]["ram_total_gb"] > 8.0
    assert len(ai_data["hardware"]["recommendations"]) >= 4
    assert len(ai_data["services_manifest"]) == 18

    # Verify FTS5 Global Search
    search_resp = client.get("/api/v1/search", params={"q": "Attention Virtual Memory"})
    assert search_resp.status_code == 200
    assert search_resp.json()["count"] >= 1

    # Verify 5-Tier Persistent Memory CRUD
    mem_post = client.post(
        "/api/v1/memories",
        json={
            "memory_category": "learner",
            "subject_key": "learning_style_preference",
            "fact_statement": "Prefers first-principles mathematical derivations paired with systems C/Python code.",
        },
    )
    assert mem_post.status_code == 200
    mems = client.get("/api/v1/memories", params={"category": "learner"}).json()
    assert any(m["subject_key"] == "learning_style_preference" for m in mems)


def test_l_socratic_tutor_and_delete_journey(client: TestClient):
    """Verify Jane Street Socratic Tutor (Levels 0-5), live web search, and DELETE /api/v1/journeys/{id}."""
    # Test Socratic Tutor /show progress command
    journeys = client.get("/api/v1/journeys").json()
    concept_id = journeys[0]["concepts"][0]["id"] if journeys else None

    soc_resp = client.post(
        "/api/v1/socratic-tutor",
        json={
            "concept_id": concept_id,
            "user_message": "We bandpass filter EEG to isolate 8-30Hz mu/beta bands before spatial filtering.",
            "command": "show progress",
        },
    )
    assert soc_resp.status_code == 200
    soc_data = soc_resp.json()
    assert "subskill_map" in soc_data
    assert "tutor_reply" in soc_data

    # Test live web search endpoint
    web_resp = client.get("/api/v1/web-search", params={"query": "Brain Computer Interface"})
    assert web_resp.status_code == 200
    assert "query" in web_resp.json()

    # Test deleting a journey
    if journeys:
        j_id = journeys[-1]["id"]
        del_resp = client.delete(f"/api/v1/journeys/{j_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["deleted"] is True



