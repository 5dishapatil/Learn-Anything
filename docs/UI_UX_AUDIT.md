# Axiom OS — Comprehensive UI/UX Design & Usability Audit

**Date**: November 2026  
**Auditor**: Principal Product Architect & Senior UX/UI Engineer  
**Scope**: Full application interface, navigation architecture, Scholar reading experience, Builder workspace, Feynman & Think Deeper workflows, and design system.

---

## Executive Summary

Axiom OS possesses an ambitious, feature-complete foundational architecture (18 specialised services, dual Scholar/Builder roads, FTS5 search, Obsidian export, and SM-2 spaced repetition). However, the current visual presentation and user experience suffer from severe **cognitive overload, visual clutter, fragmented navigation, and poor reading ergonomics**.

Instead of feeling like a calm, intellectually stimulating research sanctuary (reminiscent of Obsidian, Notion, or an academic monograph), the current interface feels like an overwhelming SaaS analytics dashboard packed with competing colored badges, bordered cards, nested containers, and dense tables.

Crucially, **the Scholar Road—the primary reading and research interface—lacks long-form typography standards**. Reading complex theoretical explanations inside multi-column bordered cards in a generic sans-serif font discourages sustained, deep study.

---

## 1. Top-Level Visual & Usability Problems

### 1.1 Navigation Fragmentation & Flat Information Architecture
- **Problem**: The global sidebar exposes **11 distinct top-level navigation items** (`Home`, `Explore`, `Journeys`, `Scholar`, `Builder`, `Library`, `Projects`, `Experiments`, `Knowledge`, `Think Deeper`, `Settings`).
- **Impact**: The user is forced to mentally categorize whether they want to look at "Scholar" vs "Journeys" vs "Projects" vs "Experiments". Scholar and Builder are treated as disconnected global sections rather than the two integrated facets of a single learning journey.
- **Solution**: Streamline to a 5-pillar global navigation:
  1. **Home**: Calm dashboard focusing on "Next Best Action", active journey resume card, and streak/stats.
  2. **Explore**: Clean, distraction-free journey creation ("What are you curious about?").
  3. **My Work**: Unified view of Journeys, Projects, and Experiments.
  4. **Knowledge**: Consolidated Resource Library, Personal Notes, Knowledge Graph, and Flashcards.
  5. **Settings**: AI Models (Ollama/Gemini), Obsidian integration, n8n automations, and Backups.
  - *Contextual Navigation*: When viewing an active journey, provide clean contextual tabs: `Overview`, `Scholar Road`, `Builder Road`, `Resources`, and `Notes`.

### 1.2 Information Overload & Container Clutter ("Card Fatigue")
- **Problem**: Almost every element is wrapped in a high-contrast container (`rounded-2xl border border-slate-800 bg-slate-900/80 p-5`). Sections are split into 2-column or 3-column card grids with glowing badges, progress bars, and icon pills.
- **Impact**: Eye fatigue and cognitive friction. The user's eye doesn't know where to land first. Crucial conceptual text is drowned out by metadata boxes, pipeline provenance banners, and epistemic tags.
- **Solution**: Adopt an 8-point spacing system with generous white space (negative space). Remove superfluous borders and backgrounds. Use subtle typographic hierarchy and dividing lines instead of wrapping every sentence in a card.

### 1.3 Typography & Long-Form Reading Ergonomics
- **Problem**:
  - The application relies exclusively on a single sans-serif font family (`Inter`) for UI controls, navigation, and 2,000-word theoretical derivations.
  - No serif font is configured for reading.
  - Paragraphs often stretch across wide cards or get cramped into tight multi-column boxes.
  - Line-height is standard (`leading-relaxed` ~ 1.5), which is too tight for sustained technical reading.
  - Mathematical notation and equations are rendered either as raw strings or within dense cards without proper display math blocks.
- **Solution**:
  - Implement a dual-font typographic system: **Inter** for UI, buttons, and metadata; **Source Serif 4 / Charter** for long-form reading, derivations, and research papers; **JetBrains Mono** for code, tokens, and mathematical invariants.
  - Enforce an optimal reading column of **65–75 characters** (`max-w-prose` / `max-w-3xl`) with generous line-height (`1.75–1.8`).
  - Provide reading preference controls (font size adjustment, serif/sans toggle, distraction-free reading mode).

### 1.4 Hardcoded & Pervasive Operating System Demonstration Content
- **Problem**: The new journey input field (`App.tsx:89`) default state is prefilled with: *"I want to understand how operating systems work and eventually build my own tiny operating system."* Furthermore, startup seed scripts unconditionally inject Journey 1 (TinyGPT) and Journey 2 (Operating Systems), causing every dashboard, card, and default dropdown to be dominated by operating system concepts regardless of the learner's actual intent.
- **Impact**: Creates the false impression that Axiom OS is a fixed Operating Systems course rather than an open, universal AI learning and research OS.
- **Solution**:
  - Remove all prepopulated demo text from form fields. Replace with an inspiring placeholder (e.g., *"e.g., Quantum Computing from first principles, Distributed Consensus, or BCI neural signal processing"*).
  - Stop unconditionally seeding demo journeys on fresh database creation; present a welcoming empty state with quick-start exploration prompts.
  - Clean existing unrequested seed journeys from the database while strictly preserving genuine user-created journeys and notes.

---

## 2. Page-by-Page Audit

### 2.1 Home View
- **Current State**: Stacks 4 stat cards, an "Active Journey" card with multiple nested badges, a full-bleed "Start New Journey" form with 8 form controls, and recent activity logs.
- **Identified Deficiencies**:
  - The "Start New Journey" form is rendered directly on the home dashboard, competing with the user's active journey progress.
  - No clear visual call-to-action for "Resume where I left off".
- **Redesign Direction**:
  - Hero card: "Continue Learning" highlighting the current concept or milestone, estimated time to complete, and a single prominent "Resume Session" button.
  - Secondary widgets: Learning streak & weekly activity summary, upcoming spaced-repetition reviews, and recent Obsidian notes.
  - Move new journey creation to a dedicated, focused "Explore" page or a clean modal.

### 2.2 Scholar Road Workspace
- **Current State**: Top bar with 4 dropdowns/buttons, 4 sub-tabs, a pipeline provenance banner ("Multi-Stage Generation Pipeline Complete 13/13"), an epistemic legend grid, and 18-point cards arranged in 2 columns.
- **Identified Deficiencies**:
  - The reader has to scroll past nearly 600px of UI chrome before reaching the first sentence of the concept explanation.
  - The explanation itself is broken into fragmented cards ("1. What Problem Are We Solving", "2. Intuition from First Principles", "3. Expandable Sections").
  - The experience feels like filling out or grading a form rather than reading a masterpiece of technical explanation.
- **Redesign Direction**:
  - **3-Pane Research Reader**:
    - **Left Sidebar** (collapsible): Concept hierarchy & chapter outline with completion checkmarks.
    - **Center Column**: Distraction-free, centered reading column in Source Serif 4 typography. Features clean section headings, pull-quotes, inline/display LaTeX math, clear diagrams, and collapsible research footnotes.
    - **Right Drawer** (collapsible): Contextual companion containing Feynman prompt, Think Deeper challenge, Active Recall cards, and Obsidian quick-notes.

### 2.3 Feynman Technique & Think Deeper Workflows
- **Current State**:
  - Feynman workflow displays 6 stages as dense card steps with multiple textareas and JSON feedback displays.
  - Think Deeper displays a list of question cards with raw score percentages and multi-select options.
- **Identified Deficiencies**:
  - Does not feel like a Socratic dialogue. It feels like an automated grading form.
- **Redesign Direction**:
  - **Feynman**: Clean, sequential step-by-step conversational interface:
    - Stage 1: The Intuition Prompt ("Explain this to an intelligent beginner without jargon").
    - Stage 2: Drafting pane with word count and causality hints.
    - Stage 3: Socratic AI feedback highlighting identified logical gaps and hand-waving phrases with inline quotes.
    - Stage 4: Guided revision pane unlocking Stage 6 (Formal Precision & Mathematical Invariants).
  - **Think Deeper**: High-focus philosophical and systems challenge view with expandable model discussions revealed only after the learner submits their first-principles reasoning.

### 2.4 Builder Road Workspace
- **Current State**: Displays milestone cards with architecture notes, code editor box, progressive hints (levels 1–5), and Break It challenges in a single tall column.
- **Identified Deficiencies**:
  - Code snippets and test scripts are mixed together with explanatory text without clear separation between "Architectural Blueprint", "Working Implementation", and "Verification Suite".
- **Redesign Direction**:
  - Clean tabbed milestone interface:
    - **Overview & Architecture**: Mission statement, why it matters, system invariants, Mermaid diagram.
    - **Implementation**: Clean code viewer/editor with syntax highlighting and progressive hint drawer (Levels 1–5 unlocked sequentially).
    - **Verification & 'Break It'**: Scientific experiment harness, hypothesis formulation, edge-case unit tests, and controlled failure analysis.

### 2.5 Knowledge & Library Workspace
- **Current State**: Displays resources in a table-like card list with external links and credibility scores.
- **Identified Deficiencies**:
  - Lack of filter by medium (Papers vs Textbooks vs Repositories vs Lectures).
  - Search falls back to OS catalogue items if live query returns nothing.
- **Redesign Direction**:
  - Clean resource cards with honest tier badges (`Completely Free`, `Free Audit`, `Open Source`).
  - Integrated note editor with bidirectional linking and instant Markdown / Obsidian vault sync.

---

## 3. Design System Specifications

| Element | Specification |
|:---|:---|
| **UI Font** | `Inter`, -apple-system, BlinkMacSystemFont, sans-serif |
| **Reading Font** | `Source Serif 4`, `Charter`, `Georgia`, serif |
| **Monospace Font** | `JetBrains Mono`, `Fira Code`, monospace |
| **Color Palette** | **Background**: Slate-950 / Zinc-950 (`#090d16`); **Surface**: Slate-900/60 (`#0f172a`); **Border**: Slate-800/80; **Primary Accent**: Indigo-500 / Indigo-400; **Epistemic CORE**: Emerald-400; **Epistemic APPROXIMATE**: Amber-400; **Epistemic EXPLORATORY**: Purple-400 |
| **Typography Scale** | Title: 32px (`text-3xl`), font-serif; Section: 22px (`text-xl`), font-semibold; Body: 17px (`text-[17px]`), font-serif, `leading-[1.75]`; Code: 14px, font-mono |
| **Spacing System** | Strict 8pt grid (`p-2`, `p-4`, `p-6`, `p-8`, `gap-4`, `gap-6`, `gap-8`) |

---

## 4. Immediate Implementation Action Items

1. **Tailwind & CSS Configuration**: Configure `Source Serif 4` and refined color tokens in `frontend/tailwind.config.js` and `frontend/src/index.css`.
2. **Navigation Refactor**: Consolidate top-level routes into `Home`, `Explore`, `My Work`, `Knowledge`, and `Settings` in `App.tsx`.
3. **Scholar Reader Redesign**: Refactor `ScholarWorkspaceView.tsx` into a distraction-free, 3-pane reading environment with serif typography.
4. **Builder Workspace Polish**: Enhance `BuilderWorkspaceView.tsx` with clean tabs for Blueprint, Code, and Break It experiments.
5. **Form & State Cleanup**: Remove hardcoded operating-system strings from form defaults and empty states.
