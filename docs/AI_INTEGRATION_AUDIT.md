# Axiom OS — Comprehensive AI Integration & Dynamic Generation Audit

**Date**: November 2026  
**Auditor**: Principal AI Systems Engineer & Product Architect  
**Scope**: LLM connectivity, Ollama integration, prompt pipelines, curriculum generation, fallback architecture, Feynman analysis, Think Deeper evaluation, and resource intelligence.

---

## Executive Summary

While Axiom OS was engineered with an elegant 18-service architectural blueprint and includes providers for local Ollama (`qwen3.5:4b`, `gemma3:4b`) and optional Google Gemini, **the actual execution flow was largely bypassing live model generation in favor of static dictionary templates and heuristic string checks**.

Most critically:
1. **Curriculum generation was 100% hardcoded**: Requesting a learning journey did not prompt Ollama. Instead, an `archetype` keyword matcher in `_build_domain_curriculum` returned static, pre-authored concept lists and milestones. Unrecognized topics fell back to a generic machine learning/gradient descent template.
2. **`generate_with_fallback` defaulted to `use_live_llm=False`**: Calls to the AI provider bypassed the live engine by default, immediately returning static fallback strings.
3. **Feynman, Think Deeper, and Recall used heuristic keyword matching**: Feynman evaluations were scored based on string length and checking for words like "because" or "magic", rather than calling the LLM for deep pedagogical reasoning.
4. **Resource search defaulted to Operating Systems**: When a query yielded no hits in the curated list, `ResourceIntelligenceService` defaulted to slicing `CURATED_INSTITUTIONAL_CATALOGUE[:4]`, which consists exclusively of Operating Systems courses and books.
5. **Startup seed script populated unrequested journeys**: Every fresh database initialization auto-injected Journey 1 (Transformers/TinyGPT) and Journey 2 (Operating Systems).

These factors collectively caused the application to feel static, canned, and perpetually dominated by operating system content, directly contradicting the core mission of an intelligent, universal research companion.

---

## 1. Detailed Deficiencies in AI Architecture

### 1.1 Static Curriculum Generation in `AIOrchestrationService`
- **Location**: `backend/app/services/ai_orchestrator.py` (`parse_intent`, `_build_domain_curriculum`, `create_full_learning_journey`)
- **Mechanism**:
  - `parse_intent` inspected keywords (`if "operating system" in lower...`).
  - `_build_domain_curriculum` returned static Python dictionaries of 5–6 concepts and 4 milestones for `operating_systems`, `tiny_gpt`, `database_engine`, and `ai_foundations`.
  - For any novel domain (e.g., "Brain Computer Interfaces" or "Quantum Error Correction"), it loaded a static fallback curriculum containing "Loss Functions, Gradient Descent & Optimisation Dynamics" and "Multilayer Perceptrons".
- **Impact**: The user never received a tailored curriculum. All custom topics received machine-learning concepts regardless of relevance.
- **Required Fix**:
  - Replace static dictionary lookup with genuine Ollama structured JSON generation using `qwen3.5:4b`.
  - Prompt the model to analyze user intent, prerequisite levels, domain-specific foundational concepts (with mathematical intuition), practical Builder milestones, and edge-case verification tasks.
  - Implement strict JSON schema parsing with validation and retry mechanics.

### 1.2 The `use_live_llm=False` Default in Provider Router
- **Location**: `backend/app/providers/router.py` (lines 102–120) and `backend/app/services/ai_orchestrator.py` (line 1309)
- **Mechanism**:
  - In `ProviderRouter.generate_with_fallback`, the signature was:
    ```python
    async def generate_with_fallback(..., use_live_llm: bool = False)
    ```
  - When `use_live_llm` was `False`, the method never even invoked `provider.generate()`; it instantly returned `GenerationResult(content=fallback_content, model="fallback", is_local=True)`.
  - In `ai_orchestrator.py`, `generate_or_update_deep_explanation` had `use_live_llm: bool = False` as default.
- **Impact**: Even when Ollama was running on `http://127.0.0.1:11434`, the application chose not to call it unless explicitly overridden.
- **Required Fix**:
  - Change default to `use_live_llm: bool = True`.
  - Attempt live generation first. If Ollama is unreachable, return a transparent diagnostic error stating that the local model is offline, along with instructions to run `ollama serve`. Never return fake AI content.

### 1.3 Canned Evaluation in Feynman & Think Deeper Engines
- **Location**: `backend/app/services/ai_orchestrator.py` (`submit_feynman_explanation`, `submit_think_deeper_response`)
- **Mechanism**:
  - `submit_feynman_explanation` performed basic word-counting and substring matching (`"because" in lower`, `"magic" in lower`).
  - `submit_think_deeper_response` generated canned assumption arrays (`"Assumes failure modes are independent..."`) and never called the LLM.
- **Impact**: The learner received identical canned feedback regardless of what they wrote.
- **Required Fix**:
  - Send the concept summary, mathematical invariants, and the learner's actual text to Ollama.
  - Instruct the model to perform rigorous Socratic analysis: extract exact quotes demonstrating understanding, identify unstated assumptions or hand-waving, and formulate 2–3 precise follow-up questions.

### 1.4 Hardcoded Operating Systems Fallback in Resource Discovery
- **Location**: `backend/app/services/resource_discovery.py` (lines 423–435)
- **Mechanism**:
  ```python
  def _match_curated_catalogue(self, query: str) -> list[dict[str, Any]]:
      ...
      if not matched:
          matched = [dict(x) for x in CURATED_INSTITUTIONAL_CATALOGUE[:4]]
      return matched
  ```
  Items 0 through 3 in `CURATED_INSTITUTIONAL_CATALOGUE` are:
  - MIT 6.1810: Operating System Engineering
  - Operating Systems: Three Easy Pieces (OSTEP)
  - mit-pdos/xv6-riscv
  - Linux Kernel Documentation
- **Impact**: Any search on quantum computing, biology, or robotics that did not hit exact catalog keywords returned Operating Systems courses.
- **Required Fix**:
  - When curated keyword matching yields no hits, do NOT default to OS resources.
  - Rely on live queries to arXiv, OpenAlex, GitHub, and HuggingFace using search terms dynamically synthesized by the LLM from the user's intent.

### 1.5 Prepopulated Demonstration Journeys in Seed Data
- **Location**: `backend/app/seed/initial_data.py` (lines 65–92)
- **Mechanism**:
  - On first run, `ensure_seed_data` checked `if existing_journeys == 0:` and created Journey 1 (Transformers) and Journey 2 (Operating Systems).
  - Furthermore, `frontend/src/App.tsx` initialized `intentInput` with the Operating Systems prompt.
- **Impact**: Every new user was presented with pre-populated OS journeys.
- **Required Fix**:
  - Remove automatic journey creation from `initial_data.py`. Only seed the default UserProfile, UserSettings, and Provider configs.
  - Set the frontend default input to empty with a helpful placeholder.
  - Provide a clean, welcoming empty state for new users.

---

## 2. Verified Local Ollama Environment

The local machine has Ollama running and verified:
- **Endpoint**: `http://127.0.0.1:11434`
- **Installed Models**:
  - `qwen3.5:4b` (Primary reasoning, curriculum design, deep explanation, coding)
  - `gemma3:4b` (Classification, question generation, quick evaluation)
  - `nomic-embed-text:latest` (Embeddings)
- **Live Execution Test**: Verified via direct HTTP POST to `/api/generate`; model generates valid JSON and text in < 1.5 seconds.

---

## 3. Implementation Roadmap

1. **Refactor `AIOrchestrationService`**:
   - Implement `_generate_curriculum_with_llm(user_intent, ...)` using structured prompts to `qwen3.5:4b`.
   - Update `generate_or_update_deep_explanation` to call live Ollama and populate deep multi-stage sections dynamically.
   - Update `submit_feynman_explanation` and `submit_think_deeper_response` to run dynamic Socratic evaluation via Ollama.
2. **Refactor `ProviderRouter`**:
   - Set `use_live_llm=True` by default.
   - Return honest diagnostic error messages when models are unreachable rather than silent fake fallbacks.
3. **Refactor `ResourceIntelligenceService`**:
   - Remove the `[:4]` OS fallback in `_match_curated_catalogue`.
   - Dynamically synthesize external query parameters for arXiv, OpenAlex, and GitHub.
4. **Clean Seed Data & Database**:
   - Remove demo journeys from `initial_data.py`.
   - Prune unrequested test/seed journeys from `axiom.db` while strictly preserving user journeys (IDs 12 & 13) and user notes.
5. **Update Frontend UI**:
   - Clear hardcoded OS input defaults.
   - Connect live Ollama generation triggers and display real-time generation indicators.
