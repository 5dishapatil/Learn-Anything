# Axiom OS — Comprehensive Whole-Website UI/UX Audit & Organization Plan

**Date**: November 2026  
**Auditor**: Principal Product Architect & Lead UX Designer  
**Scope**: Entire frontend interface (Sidebar, Top Chrome, Home Dashboard, Explore, Scholar Road, Builder Road, Research Library, Projects, Experiment Lab, My Knowledge, Think Deeper, and Settings).

---

## 1. Executive Summary & Root Visual Problems

A review of the live application and user feedback demonstrates that the interface suffers from **severe visual clutter, micro-typography (tiny 10px–12px text everywhere), container congestion ("box-inside-a-box" card fatigue), and cognitive fragmentation**.

The primary symptoms identified across all views:
1. **Microscopic Typography**: Over 70% of UI elements use `text-xs` (12px), `text-[11px]`, or `text-[10px]`. This forces the user to squint and makes the interface look like a dense, unformatted system log rather than a modern, high-end learning environment.
2. **Container Clutter & Border Saturation**: Almost every paragraph, metric, task, and button is wrapped in a high-contrast dark border (`border border-slate-800 bg-slate-900/80`). Pages have up to 4 levels of nested boxes, creating visually heavy, boxed-in rectangles that compete for attention.
3. **Sidebar Congestion**: 11 flat navigation items with badges, tiny text, and no visual categorization.
4. **Header Chrome Overload**: Dropdowns, road switchers, provider tags, search bars, theme toggles, and notification banners are all crammed into a single top header.
5. **Lack of Negative Space & Hierarchy**: Content blocks are packed edge-to-edge without the generous spacing (padding/margins) required for sustained focus, study, and reading.

---

## 2. Universal Design System & Typographic Overhaul Rules

### 2.1 Typographic Scale Standard
Every page will be elevated to the following readable standard:

| Element | Old Size | New Standard Size | Line Height | Font Family |
|:---|:---|:---|:---|:---|
| **Page / Hero Title** | 24px–28px (`text-2xl`) | **32px–36px** (`text-3xl` / `text-4xl`) | 1.25 | Sans / Serif |
| **Section Headings** | 16px–18px (`text-base` / `text-lg`) | **22px–26px** (`text-xl` / `text-2xl`) | 1.35 | Sans / Serif |
| **Subsection Headings**| 14px (`text-sm`) | **17px–19px** (`text-lg` / `text-[18px]`) | 1.4 | Sans |
| **Body Reading Text** | 12px–14px (`text-xs` / `text-sm`) | **17px–18px** (`text-[17.5px]` / `text-lg`) | **1.75–1.8** | **Source Serif 4** |
| **UI Body / Inputs** | 12px (`text-xs`) | **15px–16px** (`text-base` / `text-[15px]`) | 1.5 | **Inter** |
| **Secondary / Meta** | 10px–11px (`text-[10px]`) | **13px–14px** (`text-sm` / `text-[13.5px]`) | 1.4 | Inter |
| **Code & Technical Tokens**| 12px (`text-xs`) | **14px–15px** (`text-sm` / `text-[14.5px]`) | 1.6 | **JetBrains Mono** |

*Rule: No user-facing text shall be smaller than 13px anywhere in the application.*

---

## 3. Systematic Page-by-Page Audit & Reorganization Plan

### 3.1 Global Navigation & Sidebar
- **Problem**: 11 flat buttons in a dense column (`text-xs`, tight `p-2.5`).
- **Redesign**:
  - Group into 4 clean visual sections with generous vertical spacing:
    1. **WORKSPACE**: `Dashboard` (Home), `Explore & New Journey`
    2. **ACTIVE ROAD**: `Scholar Road` (Theory & Research), `Builder Road` (Code & Engineering)
    3. **KNOWLEDGE**: `Research Library`, `Personal Notes & Graph`, `Think Deeper`, `Experiment Lab`
    4. **SYSTEM**: `Settings & AI Telemetry`
  - Enlarge link font to **14.5px–15px** with comfortable padding (`py-3 px-3.5`).
  - Subtle active state (soft background highlight) instead of harsh saturated solid blocks.

### 3.2 Top Header Chrome
- **Problem**: 6 distinct widgets packed in a single row with a full-bleed banner.
- **Redesign**:
  - Keep the header clean and spacious: Active Journey Selector (styled cleanly without heavy border), Quick Road Toggle, Global Command Search (`Ctrl+K`), and Theme Toggle.
  - Remove redundant telemetry badges from the main header and place them into the Settings/Footer area where they belong.

### 3.3 Home Dashboard
- **Problem**: 4 dark stat boxes in a row, session resume box with 3 competing buttons, today's tasks crammed into small boxes with 11px text.
- **Redesign**:
  - **Spacious Welcome & Next Action**: Clean greeting with active journey title in **32px font**, 16px description, and a single prominent "Resume Session" button.
  - **Progress Metrics**: Clean, unbordered stat widgets with large numbers (**32px**) and readable 14px labels.
  - **Daily Focus List**: Clean checklist items with 15px readable text and comfortable padding without heavy card enclosures.
  - **Concept Constellation**: Clean, well-spaced preview.

### 3.4 Explore & Onboarding Wizard
- **Problem**: Full-bleed form assaulting user with 8 dropdowns, tiny inputs, and unorganized preset pills.
- **Redesign**:
  - Distraction-free, centered studio layout (`max-w-3xl mx-auto`).
  - Large prompt title: *"What are you curious about?"* (32px font).
  - Spacious input box with 16px text and placeholder.
  - Curated, elegant inspiration pills (Quantum, Transformers, BCI, Raft, Compilers).
  - Progressive disclosure: Essential options visible; advanced knobs collapsed cleanly under an "Advanced Configuration" toggle.

### 3.5 Scholar Road Workspace
- **Problem**: Left sidebar concept list text is 12px; right drawer text is 12px; reading column can feel cramped if sidebars are open.
- **Redesign**:
  - Left concept sidebar text enlarged to **14px** with clear active indicators.
  - Center reading column: Enforced **Source Serif 4** font at **18px** (`text-lg`) with `leading-[1.8]`, generous 80px paragraph spacing, clear section headings (26px), KaTeX math blocks with subtle backgrounds, and clean pull-quotes.
  - Right companion drawer: Enlarged text (14px–15px) for Feynman draft, feedback, and Think Deeper questions.

### 3.6 Builder Road Workspace
- **Problem**: Milestone stepper has 4 cramped cards with `text-[11px]` descriptions. Below that, a dual-column layout with 6 sections crammed into dense boxes.
- **Redesign**:
  - Clean horizontal milestone tabs with 14px font and clear state indicators (Active, Locked, Completed).
  - Tabbed workspace for the active milestone:
    1. **Architecture & Guide** (Mission, why it matters, system invariants in 16px font, Mermaid diagram)
    2. **Implementation & Tests** (Clean code editor with 14.5px font, diff preview, sandbox test runner)
    3. **Break-It Lab & Reflection** (Controlled failure exercises and learning reflections)

### 3.7 Research Library
- **Problem**: Search bar has no breathing room; cards use tiny 11px font for authors, venue, and descriptions.
- **Redesign**:
  - Centered clean search input (16px font) with filter chips: `All`, `arXiv Papers`, `Books & Textbooks`, `GitHub Repositories`, `Courses`.
  - Spacious resource cards: 18px title, 14px description, prominent free/open-source badges, and clean external links.

### 3.8 My Knowledge & Notes
- **Problem**: Notes list is packed with tiny text; markdown editor lacks clear margins.
- **Redesign**:
  - Obsidian-like 2-pane notes studio: Note list on left with 14px titles; clean markdown editor on right with 16px body font, tag pills, and instant Obsidian export button.

### 3.9 Think Deeper & Experiment Lab
- **Problem**: Dense cards packed edge-to-edge.
- **Redesign**:
  - Focus mode: Displays high-order inquiry questions with 18px serif font, spacious textareas for learner reasoning, and progressive Socratic critiques.

---

## 4. Execution Steps

1. **Global CSS & Typography**: Update `frontend/src/index.css` to enforce a clean 16px base font, spacious reading defaults, and remove heavy borders.
2. **Global Navigation & Layout**: Refactor `frontend/src/App.tsx` layout structure:
   - Spacious, categorized sidebar with 14.5px typography.
   - Clean, uncluttered top header.
   - Redesign Home dashboard with generous white space and enlarged typography.
   - Redesign Explore view into a minimalist, elegant studio.
   - Redesign Library, Projects, Experiments, Knowledge, and Think Deeper views.
3. **Scholar Reader Polish**: Enlarge all typography in `ScholarWorkspaceView.tsx` to 14px (sidebar/drawer) and 18px (reading column).
4. **Builder Workspace Polish**: Elevate typography and spacing in `BuilderWorkspaceView.tsx`.
5. **Verify with Playwright Screenshots & Tests**: Run frontend tests, production build, and capture new screenshots.
