# Resource Intelligence Engine Specification
## Axiom OS — Authentic Multi-Provider Discovery & Free-Access Verification

---

## 1. Core Principles

1. **Zero Hallucinated Citations**: The Resource Intelligence Engine queries real public APIs and curated institutional catalogues first. It never fabricates paper titles, DOIs, arXiv IDs, authors, or GitHub URLs.
2. **Honest Free-Access Classification**: Every resource is assigned an explicit `access_status`:
   - `Completely free` (arXiv papers, OpenAlex open-access works, GitHub repos, Hugging Face models/datasets, MIT OCW, Stanford SEE, official documentation, YouTube educational videos).
   - `Free audit` (Verified university courses on Coursera/edX where full lecture material is accessible via audit mode).
   - `Free learning, paid certificate` (Courses offering free content with optional paid certification).
   - `Free preview only` (Commercial courses offering only introductory previews).
   - `Paid` (Commercial courses/books requiring payment).
   - `Unverified` (External links whose access tier has not yet been confirmed).
3. **Default Filter**: By default, only genuinely free learning resources (`Completely free`, `Free audit`, `Free learning, paid certificate`) are recommended in Primary, Supplementary, and Practical Repository slots.

---

## 2. Provider Adapters (`backend/app/services/resource_discovery.py`)

| Provider | Official Public Interface Used | Metadata Extracted | Quota & Resilience Strategy |
| :--- | :--- | :--- | :--- |
| **arXiv** | `http://export.arxiv.org/api/query` (Atom XML API) | Title, Authors, Published Date, Abstract, PDF & Abs URL, Primary Category | Local SQLite cache + 3s polite timeout; zero API key required |
| **OpenAlex** | `https://api.openalex.org/works` (REST JSON API) | Title, Authorships, Publication Year, Open Access URL, Citation Count, Concepts, DOI | Polite pool header (`mailto`), cached in SQLite; zero API key required |
| **GitHub** | `https://api.github.com/search/repositories` | Full Name, Description, HTML URL, Language, Stars, Last Updated, License | Unauthenticated (60 req/hr) or optional `GITHUB_TOKEN` (5,000 req/hr) + SQLite caching |
| **Hugging Face** | `https://huggingface.co/api/models` & `/api/datasets` | Model/Dataset ID, Downloads, Likes, Pipeline Tag, Library, URL | Public Hub API; zero API key required |
| **YouTube** | Official YouTube Data API v3 (if `YOUTUBE_API_KEY` set) + Curated Verified Academic Lecture Index (MIT/Stanford/Karpathy/3Blue1Brown) | Video Title, Channel, Duration, Thumbnail, Official Embed URL | Respects quota limits; falls back to verified university lecture index when API key is not configured |
| **MIT OCW & Stanford SEE** | Verified Institutional Catalogue & Public Course Feeds (`ocw.mit.edu`, `see.stanford.edu`, `cs231n.stanford.edu`, `cs229.stanford.edu`) | Course Number, Title, Instructors, Syllabus/Lecture Notes URL, Department | Verified institutional URLs with direct deep-links |
| **Official Docs & Free Courses** | Verified Technical Documentation & Open Course Index (`docs.python.org`, `pytorch.org/docs`, `rust-lang.org`, `osdev.org`, `fast.ai`, `huggingface.co/learn`) | Title, Maintainer, URL, Access Classification (`Completely free` / `Free audit`) | Curated + live HTTP HEAD verification |

---

## 3. Recommendation Structure & Ranking Algorithm

For each learning objective or milestone, the engine groups discovered resources into:
1. **Primary Resource** (1 item): Highest composite score combining relevance, foundational clarity, and `Completely free` access.
2. **Supplementary Resources** (2 items): Complementary formats (e.g., an academic paper from arXiv/OpenAlex + a university lecture from MIT OCW/Stanford).
3. **Practical Repository / Implementation Example** (1 item): High-credibility GitHub repository or Hugging Face implementation.
4. **Explore More Shelf**: Additional verified papers, documentation, and courses.

### Composite Ranking Formula
$$\text{Score} = 0.35 \cdot \text{Relevance} + 0.25 \cdot \text{Credibility} + 0.20 \cdot \text{FreeAccessibility} + 0.10 \cdot \text{PracticalUsefulness} + 0.10 \cdot \text{RecencyFit}$$

All discovered resources are cached in the `resources` table with `last_verified_at` timestamps so repeated lookups or offline sessions never fail.
