# Testing & Verification Plan
## Axiom OS — Unit, Integration & End-to-End Acceptance Suite

---

## 1. Testing Pyramid

1. **Backend Unit & Integration Tests (`pytest`)**:
   - Validates all 38+ SQLAlchemy models, FTS5 full-text search, hardware detection, Ollama/AI provider abstraction, multi-stage explanation generation, Feynman 6-stage progression, spaced repetition scheduling, Think Deeper Socratic evaluation, Builder milestones, Experiment Lab records, Resource Intelligence classification, Obsidian safe export/sync, and n8n webhook resilience.
2. **Critical End-to-End Acceptance Tests (`backend/tests/test_acceptance_e2e.py`)**:
   - **Test A — Learn a Subject**: `"I want to learn artificial intelligence from scratch in 30 days, spending 30 minutes daily."` -> Intent parsing, prerequisite discovery, concept roadmap, Scholar + Builder roads, resource recommendations, blueprint modification, and DB persistence.
   - **Test B — Feynman Learning**: Open concept -> First-principles intuition -> Submit user explanation -> AI gap analysis with evidence -> Targeted Socratic follow-ups -> Reconstructed explanation -> Versioned history persisted.
   - **Test C — Think Deeper**: Generate 3–5 high-order questions -> Select question -> Submit reasoning -> AI evaluates assumptions & perspectives + Socratic follow-up -> Unlock model discussion -> Persisted.
   - **Test D — Build a Project**: `"I want to build a tiny GPT from scratch."` -> Architecture, prerequisites, 13-part sequential milestones, progressive hints, code artifacts, test verification, Break It challenge, Experiment Lab logging, and session resume.
   - **Test E — Switch Roads**: Start in Scholar (study concept) -> Switch to Builder (implement corresponding milestone) -> Return to Scholar -> Verify shared concept graph, notes, and context preservation.
   - **Test F — Research Resources**: Query technical subject -> Retrieve authentic resources across arXiv, OpenAlex, GitHub, Hugging Face, MIT/Stanford -> Verify URLs, provider badges, free-access classification (`Completely free`, etc.), metadata, and quota fallback.
   - **Test G — Obsidian Integration**: Enable integration with sandboxed test vault -> Export Markdown note with `[[wikilinks]]` and `obsidian://` URI -> Verify file written to sandbox vault -> Verify existing note conflict protection never overwrites user content.
   - **Test H — n8n Automation**: Verify connectivity check -> Trigger Daily Learning Digest & Knowledge Backup workflows -> Handle offline n8n gracefully without degrading main application.
   - **Test I — Resume Learning**: Complete tasks -> Simulate app restart / new session -> Call session resume service -> Reconstruct exact road, concept, milestone, and next action.
   - **Test J — Definition of Success (Operating Systems)**: `"I want to understand how operating systems work and eventually build my own tiny operating system."` -> Full end-to-end verification across all 16 success criteria.
3. **Frontend Component & Build Verification (`vitest` + `tsc` + `vite build`)**:
   - Type safety verification across all TypeScript interfaces and components.
   - Component tests for navigation, road switching, Feynman cycle, Think Deeper, and Experiment Lab.
