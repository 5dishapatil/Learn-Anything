# Security & Privacy Architecture
## Axiom OS — Local-First Personal Knowledge & Engineering Security

---

## 1. Local-First Privacy Posture

1. **Localhost Binding by Default**: Both the FastAPI backend (`127.0.0.1:8000`) and frontend dev/preview server (`127.0.0.1:5173`) bind to localhost by default.
2. **Zero Mandatory Cloud Transmission**: By default, `allow_cloud_ai` is `false`. All AI prompts, Feynman explanations, Think Deeper reflections, and project code stay on the user's machine (processed via local Ollama on the RTX A4500 GPU).
3. **Granular Data Egress Controls**: Even if the user explicitly configures an optional Gemini API key, Settings provides explicit toggles controlling whether:
   - Personal Notes / Obsidian content may be sent to cloud AI (`default: false`)
   - Project Source Code may be sent to cloud AI (`default: false`)
   - Research queries may be sent to cloud AI (`default: true when Gemini active`)

---

## 2. Secret & Credential Protection

- **Environment Variables**: Configured via `.env` (git-ignored) with a safe `.env.example` template committed to version control.
- **Backend-Only Secrets**: API keys for Gemini, Obsidian Local REST API, n8n webhook secrets, GitHub, and YouTube are stored exclusively on the backend. API responses mask secrets (e.g., `••••••••••••a9f2`) and never expose raw tokens to frontend JavaScript bundles.

---

## 3. File System & Code Execution Guardrails

1. **Workspace Path Traversal Protection**: Any file export, backup, or approved Obsidian folder operation validates resolved paths via `Path.resolve()` against an explicit allowlist of approved directories. Path traversal (`..`) is rejected with HTTP 403.
2. **No Silent Project File Modification**: In the Builder Workspace, editing code updates the internal `ProjectArtifact` database record first and shows a clear diff preview before any optional sync to a user-connected project directory.
3. **Controlled Sandbox Verification**: Code verification in the Builder Workspace runs only upon explicit user click with clear security disclosure, strictly bounded timeouts (5 seconds), and isolated working directories.
4. **Prompt Injection & XSS Defense**: External resource abstracts (arXiv, GitHub, OpenAlex) are sanitised before rendering in Markdown and wrapped in untrusted-data delimiters when passed to AI synthesis services so embedded prompt instructions cannot hijack application state.
