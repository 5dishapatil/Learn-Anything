from __future__ import annotations

import hashlib
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
import httpx
from sqlalchemy.orm import Session

from app.config import WORKSPACE_DIR, settings
from app.models.domain import (
    Concept,
    Experiment,
    FeynmanExplanation,
    IntegrationConfig,
    Lesson,
    Note,
    Project,
    ThinkDeeperResponse,
)


SUGGESTED_OBSIDIAN_STRUCTURE = [
    "Learning OS/00 - Dashboard",
    "Learning OS/01 - Learning Journeys",
    "Learning OS/02 - Concepts",
    "Learning OS/03 - Research Papers",
    "Learning OS/04 - Resources",
    "Learning OS/05 - Projects",
    "Learning OS/06 - Experiments",
    "Learning OS/07 - Reflections",
    "Learning OS/08 - Think Deeper",
    "Learning OS/09 - Daily Logs",
]


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


class ObsidianConnectorService:
    """
    3-Stage Obsidian Integration:
      - Stage 1: Clean Markdown export with YAML frontmatter, [[wikilinks]], and obsidian:// URI generation.
      - Stage 2: Optional Obsidian Local REST API connector.
      - Stage 3: Safe, folder-scoped two-way synchronisation with conflict detection (never silently overwrites).
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_config(self) -> IntegrationConfig:
        cfg = (
            self.db.query(IntegrationConfig)
            .filter(IntegrationConfig.integration_type == "obsidian")
            .first()
        )
        if not cfg:
            default_sandbox_vault = (WORKSPACE_DIR / "backend" / "backups" / "obsidian_vault_staging").as_posix()
            cfg = IntegrationConfig(
                integration_type="obsidian",
                display_name="Obsidian Personal Knowledge Vault",
                is_enabled=True,
                endpoint_url=settings.OBSIDIAN_REST_URL,
                auth_token=settings.OBSIDIAN_API_TOKEN,
                vault_name=settings.OBSIDIAN_DEFAULT_VAULT or "Learning OS",
                vault_local_path=default_sandbox_vault,
                approved_folders_json=list(SUGGESTED_OBSIDIAN_STRUCTURE),
                read_permission=True,
                write_permission=True,
                status_message="Stage 1 URI & Staging Vault Active. Configure Local REST API or custom vault path in Settings.",
            )
            self.db.add(cfg)
            self.db.commit()
            self.db.refresh(cfg)
        return cfg

    def build_obsidian_uri(self, vault_name: str, file_relative_path: str, content: Optional[str] = None) -> dict[str, str]:
        encoded_vault = urllib.parse.quote(vault_name)
        encoded_file = urllib.parse.quote(file_relative_path.removesuffix(".md"))
        open_uri = f"obsidian://open?vault={encoded_vault}&file={encoded_file}"
        new_uri = open_uri
        if content is not None:
            encoded_content = urllib.parse.quote(content[:3500])
            new_uri = f"obsidian://new?vault={encoded_vault}&file={encoded_file}&content={encoded_content}"
        return {
            "open_uri": open_uri,
            "new_uri": new_uri,
        }

    def format_entity_markdown(
        self,
        export_type: str,
        entity_id: int,
    ) -> tuple[str, str, str]:
        """
        Generate clean Obsidian Markdown with YAML frontmatter, [[wikilinks]], and backlinks.
        Returns (title, relative_vault_path, markdown_content).
        """
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        if export_type == "concept":
            concept = self.db.query(Concept).filter(Concept.id == entity_id).first()
            if not concept:
                raise ValueError(f"Concept {entity_id} not found")
            lesson = self.db.query(Lesson).filter(Lesson.concept_id == concept.id).first()
            feynman = (
                self.db.query(FeynmanExplanation)
                .filter(FeynmanExplanation.concept_id == concept.id)
                .order_by(FeynmanExplanation.version_number.desc())
                .first()
            )
            rel_path = f"Learning OS/02 - Concepts/{concept.slug}.md"
            md = f"""---
title: "{concept.title}"
type: concept_note
category: "{concept.category}"
prerequisite_level: "{concept.prerequisite_level}"
mastery_status: "{concept.mastery_status}"
exported_at: "{now_iso}"
tags:
  - axiom-os
  - scholar-road
  - {concept.category}
---

# {concept.title}

> **Summary**: {concept.summary}

## 1. First-Principles Intuition (`CORE`)
{lesson.first_principles_intuition if lesson else concept.summary}

## 2. Formal Technical & Mathematical Explanation
{lesson.formal_technical_explanation if lesson else ""}

{lesson.mathematical_derivations if lesson else ""}

## 3. Worked Numerical Example
{lesson.worked_examples if lesson else ""}

## 4. My Feynman Reconstruction
{feynman.revised_explanation or feynman.user_explanation if feynman else "_Not yet recorded._"}

## 5. Connected Knowledge & Backlinks
- **Parent Journey**: [[Journey-{concept.journey_id}]]
- **Related Disciplines**: {", ".join(f"[[{d}]]" for d in (concept.related_disciplines_json or ["Computer Science"]))}
"""
            return concept.title, rel_path, md

        if export_type == "project":
            proj = self.db.query(Project).filter(Project.id == entity_id).first()
            if not proj:
                raise ValueError(f"Project {entity_id} not found")
            rel_path = f"Learning OS/05 - Projects/{proj.slug}.md"
            milestones_md = "\n".join(
                f"- [{'x' if m.status == 'completed' else ' '}] **M{m.sequence_order}: {m.title}** — {m.mission}"
                for m in proj.milestones
            )
            md = f"""---
title: "{proj.title}"
type: project_journal
domain: "{proj.domain}"
status: "{proj.status}"
exported_at: "{now_iso}"
tags:
  - axiom-os
  - builder-road
  - project
---

# {proj.title}

## Objective
{proj.objective}

## Architecture Overview
{proj.architecture_overview}

```mermaid
{proj.architecture_mermaid}
```

## Sequential Milestones
{milestones_md}

## Next Engineering Action
{proj.next_action}
"""
            return proj.title, rel_path, md

        if export_type == "experiment":
            exp = self.db.query(Experiment).filter(Experiment.id == entity_id).first()
            if not exp:
                raise ValueError(f"Experiment {entity_id} not found")
            slug = exp.title.lower().replace(" ", "-")[:60]
            rel_path = f"Learning OS/06 - Experiments/{slug}.md"
            md = f"""---
title: "{exp.title}"
type: experiment_record
status: "{exp.status}"
exported_at: "{now_iso}"
tags:
  - axiom-os
  - experiment-lab
---

# Experiment: {exp.title}

- **Hypothesis**: {exp.hypothesis}
- **Objective**: {exp.objective}
- **Variables Changed**: `{exp.variables_changed_json}`

## Procedure
{exp.procedure}

## Expected vs. Actual Outcome
- **Expected**: {exp.expected_outcome}
- **Actual**: {exp.actual_outcome}

## Observations & Conclusion
{exp.observations}

> **Conclusion**: {exp.conclusion}
"""
            return exp.title, rel_path, md

        if export_type == "think_deeper":
            td = self.db.query(ThinkDeeperResponse).filter(ThinkDeeperResponse.id == entity_id).first()
            if not td:
                raise ValueError(f"ThinkDeeperResponse {entity_id} not found")
            q_prompt = td.question.prompt if td.question else "Think Deeper Reflection"
            rel_path = f"Learning OS/08 - Think Deeper/think-deeper-{td.id}.md"
            md = f"""---
title: "Think Deeper #{td.id}"
type: think_deeper_dialogue
exported_at: "{now_iso}"
tags:
  - axiom-os
  - think-deeper
---

# Think Deeper Inquiry

## Question
> {q_prompt}

## My First-Principles Reasoning
{td.user_reasoning}

## Socratic Analysis & Uncovered Assumptions
{td.reasoning_analysis}

- **Follow-up Socratic Prompt**: {td.socratic_followup_question}
"""
            return f"Think Deeper #{td.id}", rel_path, md

        # Default: Note export
        note = self.db.query(Note).filter(Note.id == entity_id).first()
        if not note:
            raise ValueError(f"Note {entity_id} not found")
        folder = note.obsidian_folder or "02 - Concepts"
        rel_path = f"Learning OS/{folder}/{note.slug}.md"
        tag_list = [t.name for t in note.tags] or ["axiom-os", "knowledge-note"]
        tags_yaml = "\n".join(f"  - {t}" for t in tag_list)
        md = f"""---
title: "{note.title}"
type: "{note.note_type}"
exported_at: "{now_iso}"
tags:
{tags_yaml}
---

# {note.title}

{note.content_markdown}

## Personal Understanding
{note.personal_understanding}
"""
        return note.title, rel_path, md

    async def export_to_obsidian(
        self,
        export_type: str,
        entity_id: int,
        target_vault_dir: Optional[str] = None,
        allow_overwrite: bool = False,
    ) -> dict[str, Any]:
        """
        Export an entity to Markdown + Obsidian URI, and safely write to an authorised vault directory
        without ever silently overwriting existing user-modified files.
        """
        cfg = self.get_config()
        title, rel_path, md_content = self.format_entity_markdown(export_type, entity_id)
        uris = self.build_obsidian_uri(cfg.vault_name, rel_path, md_content)

        vault_root_str = target_vault_dir or cfg.vault_local_path
        written_file_path: Optional[str] = None
        conflict_protected = False
        rest_api_pushed = False

        if vault_root_str:
            vault_root = Path(vault_root_str).resolve()
            dest_path = (vault_root / rel_path).resolve()
            # Path traversal security guard
            if not str(dest_path).startswith(str(vault_root)):
                raise PermissionError("Path traversal outside approved vault directory is forbidden.")

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if dest_path.exists() and not allow_overwrite:
                existing_text = dest_path.read_text(encoding="utf-8")
                if _sha256(existing_text) != _sha256(md_content):
                    # Never silently overwrite existing note! Create a non-destructive timestamped companion file.
                    conflict_protected = True
                    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
                    safe_dest = dest_path.with_name(f"{dest_path.stem}.axiom-export-{ts}.md")
                    safe_dest.write_text(md_content, encoding="utf-8")
                    written_file_path = safe_dest.as_posix()
                else:
                    written_file_path = dest_path.as_posix()
            else:
                dest_path.write_text(md_content, encoding="utf-8")
                written_file_path = dest_path.as_posix()

        # Optional Stage 2: Local REST API push if token configured
        if cfg.is_enabled and cfg.auth_token and cfg.endpoint_url:
            try:
                headers = {
                    "Authorization": f"Bearer {cfg.auth_token}",
                    "Content-Type": "text/markdown",
                }
                async with httpx.AsyncClient(timeout=3.0, verify=False) as client:
                    url = f"{cfg.endpoint_url.rstrip('/')}/vault/{ urllib.parse.quote(rel_path) }"
                    resp = await client.put(url, content=md_content.encode("utf-8"), headers=headers)
                    rest_api_pushed = resp.status_code in (200, 201, 204)
            except Exception:
                rest_api_pushed = False

        return {
            "title": title,
            "export_type": export_type,
            "entity_id": entity_id,
            "vault_name": cfg.vault_name,
            "relative_vault_path": rel_path,
            "written_file_path": written_file_path,
            "conflict_protected_existing_note": conflict_protected,
            "rest_api_pushed": rest_api_pushed,
            "obsidian_open_uri": uris["open_uri"],
            "obsidian_new_uri": uris["new_uri"],
            "markdown_preview": md_content,
            "suggested_folder_structure": SUGGESTED_OBSIDIAN_STRUCTURE,
        }

    def generate_sync_preview(self, target_vault_dir: Optional[str] = None) -> dict[str, Any]:
        """Stage 3: Generate a non-destructive preview of changes between Axiom OS Notes and the approved vault."""
        cfg = self.get_config()
        vault_root = Path(target_vault_dir or cfg.vault_local_path).resolve()
        vault_root.mkdir(parents=True, exist_ok=True)

        notes = self.db.query(Note).all()
        preview_items: list[dict[str, Any]] = []
        for note in notes:
            _, rel_path, md_content = self.format_entity_markdown("note", note.id)
            dest = vault_root / rel_path
            if not dest.exists():
                status = "NEW_EXPORT"
                detail = "Note does not yet exist in vault; safe to create."
            else:
                existing_md = dest.read_text(encoding="utf-8")
                if _sha256(existing_md) == _sha256(md_content):
                    status = "IN_SYNC"
                    detail = "Identical content hash."
                else:
                    status = "CONFLICT_PROTECTED"
                    detail = "Existing vault file differs; Axiom OS will preserve user file and write a companion version unless explicitly approved."
            preview_items.append(
                {
                    "note_id": note.id,
                    "title": note.title,
                    "relative_path": rel_path,
                    "sync_status": status,
                    "detail": detail,
                }
            )
        return {
            "vault_root": vault_root.as_posix(),
            "approved_folders": cfg.approved_folders_json or SUGGESTED_OBSIDIAN_STRUCTURE,
            "items": preview_items,
        }
