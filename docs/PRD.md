# Product Requirements Document (PRD)
## Axiom OS — Personal AI Research, Learning & Creation OS

---

## 1. Executive Summary & Vision

**Axiom OS** is a local-first, AI-powered personal environment designed for ambitious learners, researchers, and engineers who want to learn from first principles (like Andrej Karpathy), think critically like a scientist, and build working software systems independently.

**Core Thesis**:  
> *An intelligent personal environment where curiosity becomes understanding, understanding becomes implementation, implementation leads to experimentation, and experimentation creates new knowledge.*

Unlike passive course platforms, generic roadmaps, or one-shot chatbots, Axiom OS unifies personalised learning journeys, source-grounded academic research, interactive Feynman reconstruction, Socratic higher-order reasoning (**Think Deeper**), guided sequential project building, a scientific **Experiment Lab**, a connected **Personal Knowledge Workspace**, **Obsidian** integration, and optional local **n8n** workflow automation.

---

## 2. Target User Problems Solved

1. **Deciding what to learn & identifying prerequisites**: Automated prerequisite discovery with `Essential`, `Recommended`, and `Optional` dependency mapping.
2. **Finding credible, genuinely free resources**: Live multi-provider discovery across arXiv, OpenAlex, GitHub, Hugging Face, MIT OCW, Stanford, and YouTube with transparent free-access classification.
3. **Understanding complex technical subjects**: Multi-stage Deep Explanation Engine with `Concise`, `Detailed`, and `Research depth` modes, mathematical derivations, worked numerical examples, and diagrams.
4. **Bridging abstract theory and implementation**: Seamless context switching between **Scholar Road** (theory & papers) and **Builder Road** (architecture, code, debugging, tests) over a shared concept graph.
5. **Building substantial projects without getting lost**: Sequential milestones (Mission -> Why It Matters -> Prerequisites -> Research -> Architecture -> Step-by-Step Implementation -> Code Understanding -> Testing -> Experimentation -> Break It -> Deliverable -> Reflection -> Think Deeper).
6. **Maintaining context across weeks of work**: Persistent 5-tier AI memory (Learner, Knowledge, Research, Project, Session) and intelligent session resume summaries.
7. **Debugging & experimenting independently**: Progressive 5-level hints and a structured Experiment Lab recording hypotheses, variables, procedures, and outcomes.
8. **Long-term retention & deep synthesis**: 6-stage Feynman Learning Engine, transparent spaced repetition (SM-2 inspired multi-evidence scheduling), and bidirectional Obsidian knowledge synchronisation.

---

## 3. Core Product Experience: Two Interconnected Roads

| Dimension | Road A: SCHOLAR (Understand Deeply) | Road B: BUILDER (Create Independently) |
| :--- | :--- | :--- |
| **Primary Goal** | First-principles theoretical mastery & research synthesis | Designing, implementing, testing & breaking real systems |
| **Core Unit** | Concept Node + Deep Multi-Stage Lesson | Project Blueprint + Sequential Engineering Milestone |
| **Verification** | Feynman 6-Stage Reconstruction + Active Recall + Think Deeper | Working Code Artifact + Edge-Case Tests + Controlled Failure ("Break It") + Experiments |
| **Shared Layer** | Unified Concept Graph, Citations, Resource Shelf, Notes, Reflections, AI Memory | Unified Concept Graph, Citations, Resource Shelf, Notes, Reflections, AI Memory |

Users can select **Scholar Only**, **Builder Only**, or **Hybrid Mode** during onboarding or journey creation, and switch between roads on any concept without losing context.

---

## 4. Functional Requirements by Module

### 4.1 Onboarding & Journey Creation
- Collect topic or project intent, experience level (`Beginner`, `Intermediate`, `Advanced`, `Researcher`), daily time commitment, target duration, road mode (`Scholar`, `Builder`, `Hybrid`), preferred learning format (`Combined`, `Written`, `Research-paper-first`, `Video-first`, `Lecture-first`), existing knowledge, and optional final project deliverable.
- Zero entrance examinations; immediate generation of an interactive **Research & Build Blueprint**.

### 4.2 The Scholar Road & Deep Explanation Engine
- **Concept & Prerequisite Discovery**: Navigable visual knowledge graph with foundational, intermediate, and advanced concepts, mathematical foundations, and labelled dependencies (`Essential`, `Recommended`, `Optional`).
- **18-Point Deep Explanation Architecture**: Covers Problem Statement, Why It Exists, Historical Context, First-Principles Intuition, Real-World Analogies, Conceptual Explanation, Formal Technical Explanation, Mathematical Foundations & Derivations, Worked Numerical Examples, Mermaid Diagrams, Code Examples, Practical Applications, Engineering Trade-offs, Common Misconceptions, Limitations, Concept Connections, Research References, and Further Exploration.
- **Depth Control**: Switch or expand sections across `Concise`, `Detailed` (default), and `Research depth`.
- **Epistemic Labels**: Every major claim or section clearly tagged as `CORE`, `APPROXIMATE`, or `EXPLORATORY`.
- **Multi-Stage Generation**: Outlines, generates section-by-section, audits completeness, and supports resuming interrupted generation.

### 4.3 Feynman Learning Engine
- Interactive 6-stage cycle:
  1. **Build Intuition** (accessible first-principles framing)
  2. **Explain in Your Own Words** (learner teaching prompt)
  3. **Identify Gaps** (evidence-backed analysis of missing links, circular jargon, or flawed assumptions)
  4. **Guided Correction** (Socratic questions, counterexamples, and analogies without spoiling the full answer)
  5. **Reconstruct** (revised explanation with side-by-side diff/comparison against earlier drafts)
  6. **Technical Precision** (formal mathematical/systems definitions unlocked and consolidated)

### 4.4 Active Recall & Spaced Repetition
- Multi-format assessments: Free recall, flashcards, short-answer, concept reconstruction, multiple-choice, mathematical derivations, compare-and-contrast, explain-the-difference, and practical application challenges.
- Transparent spaced repetition scheduler tracking interval, ease factor, stability, and evidence diversity (never claiming mastery from a single multiple-choice pass).

### 4.5 Think Deeper (Signature Feature)
- Mandatory section on every substantial Scholar lesson and Builder milestone.
- Generates 3–5 higher-order questions targeting assumption analysis, counterfactuals, systems trade-offs, failure investigation, and cross-disciplinary synthesis.
- Provides optional hints, evaluates the user's reasoning and hidden assumptions, asks Socratic follow-ups, and only unlocks the model's research discussion after a genuine attempt.

### 4.6 The Builder Road, Coding Workspace & Experiment Lab
- **Editable Research & Build Blueprint**: Title, objective, deliverables, prerequisites, proposed architecture, milestones, tech stack, papers, experiments, failure modes, effort estimate, and stretch goals.
- **13-Part Sequential Milestones**: Mission (A) through Think Deeper (M), including **Break It (J)** controlled failure exercises.
- **5-Tier Adaptive Implementation Assistance**: (1) Conceptual Hint -> (2) Architectural Approach -> (3) Pseudocode -> (4) Small Illustrative Snippet -> (5) Guided Full Implementation.
- **Integrated Monaco Workspace**: Multi-file project artifacts, syntax highlighting, architecture diagrams, test suites, diff preview before saving, and controlled user-approved local execution/verification.
- **Experiment Laboratory**: Structured scientific records (Hypothesis, Objective, Variables Changed, Procedure, Expected vs. Actual Outcome, Observations, Results, Metrics/Visualisation, Conclusion, Next Experiment) with multi-experiment comparison.

### 4.7 Resource Intelligence Engine
- Live adapters for **arXiv**, **OpenAlex**, **GitHub**, **Hugging Face**, **YouTube**, **MIT OpenCourseWare**, **Stanford Engineering Everywhere**, and curated free courses/documentation.
- Strict free-access classification (`Completely free`, `Free audit`, `Free learning, paid certificate`, `Free preview only`, `Paid`, `Unverified`).
- Recommends 1 Primary Resource, 2 Supplementary Resources, and 1 Practical Repository per learning objective, plus an "Explore More" shelf.

### 4.8 Personal Knowledge Workspace, Obsidian & n8n
- Six workspace views: **My Knowledge**, **My Library**, **My Projects**, **My Experiments**, **My Questions**, **My Learning History** with SQLite FTS5 full-text search, tags, and bidirectional backlinks.
- **Obsidian Integration**: Stage 1 (Clean Markdown export with YAML frontmatter, `[[wikilinks]]`, and `obsidian://` URI launcher), Stage 2 (Optional Local REST API connector), Stage 3 (Safe previewed two-way folder sync that never overwrites user notes silently).
- **n8n Local Automation**: Optional connector with 7 ready-to-import workflow templates and local webhook receivers; full application functionality preserved when n8n is offline.

### 4.9 Adventure & Progression System
- Intellectual progression system featuring Knowledge Constellations, Exploration Trails, XP earned through verified synthesis/implementation, unlockable milestones, and non-punitive activity tracking (missed days never reset learning progress).
