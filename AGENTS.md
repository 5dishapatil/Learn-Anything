# AGENTS.md — Non-Negotiable Principles & Engineering Charter

**Project**: Axiom OS — Personal AI Research, Learning & Creation OS  
**Workspace**: `d:\Learn Anything`

---

## 1. Core Identity & Mission

Axiom OS is a local-first, zero-mandatory-cost AI-powered environment where **curiosity becomes first-principles understanding, understanding becomes implementation, implementation leads to experimentation, and experimentation creates new knowledge**.

We are **NOT** building a course marketplace, a video aggregator, a shallow roadmap generator, a generic AI chatbot, or a one-click code generator. Every feature must cultivate independent researchers and builders who think from first principles, question assumptions, and create original systems.

---

## 2. The Eight Foundational Principles (Non-Negotiable)

1. **First principles over memorisation**: Every explanation must start from the fundamental problem, physical/mathematical reality, or systems constraint before introducing jargon or formulas.
2. **Understanding over passive consumption**: Never let a learner passively read or watch without active reconstruction (Feynman Cycle, Active Recall, Think Deeper).
3. **Creation over tutorial watching**: Every theoretical concept connects to a tangible engineering artifact, milestone, or experiment on the Builder Road.
4. **Continuity over isolated lessons**: All journeys, roads, concepts, code artifacts, experiments, notes, and AI memories persist in a unified relational + FTS5 knowledge graph. Returning weeks later must restore full context immediately.
5. **Research-backed knowledge over unsupported AI claims**: Every claim and resource must distinguish established core facts (`CORE`), pedagogical simplifications (`APPROXIMATE`), and open hypotheses (`EXPLORATORY`). Never fabricate papers, authors, URLs, or quotes.
6. **Experimentation over unquestioned assumptions**: Every Builder project includes controlled failure ("Break It") and structured scientific experiments (Hypothesis -> Variables -> Procedure -> Expected vs. Actual -> Conclusion).
7. **AI assistance without AI dependency**: Use progressive hints (Conceptual -> Approach -> Pseudocode -> Illustrative Snippet -> Guided Full Implementation) and Socratic questioning before exposing solutions.
8. **Knowledge that accumulates and becomes more valuable over time**: Every note, Feynman revision, Think Deeper response, citation, and experiment links into the Personal Knowledge Workspace and exports cleanly to Obsidian.

---

## 3. Strict Operational Guardrails & Permissions

Autonomous agents and contributors working in this repository MUST obtain explicit user permission before:
- **Downloading large AI models** (never run `ollama pull` automatically without explicit user approval).
- **Sending private information to external AI providers** (cloud providers like Gemini are disabled by default and require explicit user opt-in and API key configuration).
- **Accessing the user's existing personal Obsidian vault** (use URI schemes, Markdown downloads, or user-authorized specific folders; automated tests must only use sandboxed test directories inside the workspace).
- **Modifying files outside `d:\Learn Anything`**.
- **Executing potentially destructive system commands**.
- **Enabling any external service that could incur financial charges**.

---

## 4. Technical & Architectural Rules

1. **Two Interconnected Learning Roads**:
   - **Scholar Road** (Understand deeply) and **Builder Road** (Create independently) share a single underlying `Concept` graph, `Resource` library, `Note` system, `Project` state, and `MemoryFact` store.
2. **Multi-Stage Deep Explanation Engine**:
   - Never rely on a single shallow prompt for substantial topics. Use structured multi-stage generation (Intent & Level -> Learning Objectives -> Source Grounding -> Section Outline -> Section-by-Section Deep Generation -> Derivations & Worked Examples -> Mermaid Diagrams -> Feynman & Think Deeper Synthesis -> Quality Audit).
3. **Signature Features Required on Every Substantial Concept/Milestone**:
   - **Feynman Learning Engine**: 6-stage interactive cycle with gap analysis, evidence-based feedback, Socratic guided correction, and versioned history.
   - **Think Deeper**: 3–5 high-order first-principles, counterfactual, and systems trade-off questions with Socratic evaluation (never immediately reveal model answers).
   - **Experiment Lab & Break It**: Structured hypothesis testing and controlled failure exercises on the Builder Road.
4. **Honest Resource Intelligence**:
   - Classify every external resource honestly (`Completely free`, `Free audit`, `Free learning, paid certificate`, `Free preview only`, `Paid`, `Unverified`). Default recommendations must prioritize genuinely free, authoritative resources (arXiv, OpenAlex, MIT OCW, Stanford SEE, GitHub, official docs).
5. **Local-First & Resilient**:
   - The application must operate with zero mandatory cost using SQLite + FTS5 and local Ollama (`http://localhost:11434`), and gracefully handle offline states, missing n8n instances, or external API rate limits with deterministic fallbacks and caching.
