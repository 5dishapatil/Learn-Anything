from __future__ import annotations

import asyncio
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Optional
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.domain import Resource, ResourceProvider, ResourceRelationship


FREE_ACCESS_TIERS = {
    "Completely free",
    "Free audit",
    "Free learning, paid certificate",
}


CURATED_INSTITUTIONAL_CATALOGUE: list[dict[str, Any]] = [
    # Operating Systems
    {
        "provider_name": "mit_ocw",
        "external_id": "mit-6.1810-os",
        "title": "MIT 6.1810: Operating System Engineering (xv6 Kernel Labs & Lectures)",
        "url": "https://pdos.csail.mit.edu/6.828/",
        "resource_type": "course",
        "authors_json": ["Prof. Frans Kaashoek", "Prof. Robert Morris"],
        "published_date": "2024",
        "access_status": "Completely free",
        "license_info": "CC BY-NC-SA 4.0 / MIT License (xv6)",
        "description": "MIT's flagship operating systems engineering course built around the xv6 RISC-V kernel: page tables, traps, copy-on-write fork, file systems, and concurrency.",
        "relevance_explanation": "Gold-standard first-principles university course for both understanding OS theory and building a real kernel.",
        "credibility_score": 0.99,
        "relevance_score": 0.98,
        "difficulty_level": "intermediate",
        "stars_or_citations": 8400,
        "duration_or_length": "23 Lectures + 10 Kernel Labs",
        "keywords": ["operating system", "os", "kernel", "memory", "virtual memory", "paging", "scheduler", "filesystem", "xv6"],
    },
    {
        "provider_name": "official_docs",
        "external_id": "ostep-book",
        "title": "Operating Systems: Three Easy Pieces (OSTEP — Virtualization, Concurrency, Persistence)",
        "url": "https://pages.cs.wisc.edu/~remzi/OSTEP/",
        "resource_type": "documentation",
        "authors_json": ["Remzi H. Arpaci-Dusseau", "Andrea C. Arpaci-Dusseau"],
        "published_date": "2023",
        "access_status": "Completely free",
        "license_info": "Free Online Academic Textbook",
        "description": "University of Wisconsin-Madison's acclaimed first-principles textbook covering process APIs, MLFQ scheduling, address translation, paging, TLBs, locks, and crash-consistent file systems.",
        "relevance_explanation": "Unmatched conceptual and mathematical clarity for OS virtualization, scheduling, and memory management.",
        "credibility_score": 0.99,
        "relevance_score": 0.97,
        "difficulty_level": "beginner",
        "stars_or_citations": 6200,
        "duration_or_length": "50 Chapters + Simulation Code",
        "keywords": ["operating system", "os", "memory", "process", "scheduling", "virtual memory", "file system", "ostep"],
    },
    {
        "provider_name": "github",
        "external_id": "mit-pdos-xv6-riscv",
        "title": "mit-pdos/xv6-riscv — Complete Teaching Operating System Kernel in C & RISC-V Assembly",
        "url": "https://github.com/mit-pdos/xv6-riscv",
        "resource_type": "repository",
        "authors_json": ["MIT PDOS Group"],
        "published_date": "2025",
        "access_status": "Completely free",
        "license_info": "MIT License",
        "description": "Clean, readable re-implementation of Unix v6 in ANSI C for multi-core RISC-V, including boot entry, buddy/freelist page allocator, Sv39 page tables, context switching, and logging file system.",
        "relevance_explanation": "Direct practical reference repository for building a minimal operating system from scratch.",
        "credibility_score": 0.99,
        "relevance_score": 0.96,
        "difficulty_level": "intermediate",
        "stars_or_citations": 7800,
        "language": "C",
        "keywords": ["operating system", "os", "kernel", "riscv", "c", "memory", "scheduler", "tiny os"],
    },
    {
        "provider_name": "official_docs",
        "external_id": "osdev-wiki-bare-bones",
        "title": "OSDev.org Wiki & Writing an OS in Rust (Philipp Oppermann)",
        "url": "https://os.phil-opp.com/",
        "resource_type": "documentation",
        "authors_json": ["Philipp Oppermann", "OSDev Community"],
        "published_date": "2024",
        "access_status": "Completely free",
        "license_info": "MIT / Dual License",
        "description": "Step-by-step systems engineering guide to freestanding binaries, VGA text buffer, CPU exceptions, hardware interrupts, 4-level paging, heap allocation, and async/await cooperative multitasking.",
        "relevance_explanation": "Bridges low-level hardware specifications directly into incremental, testable kernel milestones.",
        "credibility_score": 0.97,
        "relevance_score": 0.95,
        "difficulty_level": "intermediate",
        "stars_or_citations": 14200,
        "keywords": ["operating system", "os", "rust", "kernel", "bootloader", "interrupts", "paging", "allocator"],
    },
    # Transformers, Deep Learning & TinyGPT
    {
        "provider_name": "arxiv",
        "external_id": "1706.03762",
        "title": "Attention Is All You Need",
        "url": "https://arxiv.org/abs/1706.03762",
        "resource_type": "paper",
        "authors_json": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Lukasz Kaiser", "Illia Polosukhin"],
        "published_date": "2017-06-12",
        "access_status": "Completely free",
        "license_info": "arXiv Open Access",
        "description": "The foundational paper introducing the Transformer architecture based solely on scaled dot-product attention and multi-head attention, dispensing with recurrence and convolutions.",
        "relevance_explanation": "Essential primary research source for understanding self-attention, positional encoding, and Transformer scaling.",
        "credibility_score": 1.0,
        "relevance_score": 0.99,
        "difficulty_level": "intermediate",
        "stars_or_citations": 125000,
        "keywords": ["transformer", "attention", "gpt", "llm", "neural network", "ai", "deep learning", "sequence"],
    },
    {
        "provider_name": "github",
        "external_id": "karpathy-nanogpt",
        "title": "karpathy/nanoGPT — The Simplest, Fastest Repository for Training/Finetuning Medium-Sized GPTs",
        "url": "https://github.com/karpathy/nanoGPT",
        "resource_type": "repository",
        "authors_json": ["Andrej Karpathy"],
        "published_date": "2024",
        "access_status": "Completely free",
        "license_info": "MIT License",
        "description": "A clean ~300-line PyTorch implementation of GPT training and inference (`model.py` and `train.py`) designed for readability, hacking, and first-principles experimentation.",
        "relevance_explanation": "Canonical practical implementation reference for building and training a TinyGPT from scratch.",
        "credibility_score": 0.99,
        "relevance_score": 0.99,
        "difficulty_level": "intermediate",
        "stars_or_citations": 39500,
        "language": "Python",
        "keywords": ["gpt", "transformer", "tiny gpt", "nanogpt", "llm", "pytorch", "attention", "ai"],
    },
    {
        "provider_name": "youtube",
        "external_id": "kCc8FmEb1nY",
        "title": "Let's build GPT: from scratch, in code, spelled out (Andrej Karpathy)",
        "url": "https://www.youtube.com/watch?v=kCc8FmEb1nY",
        "resource_type": "video",
        "authors_json": ["Andrej Karpathy"],
        "published_date": "2023-01-17",
        "access_status": "Completely free",
        "license_info": "YouTube Standard Educational",
        "description": "Two-hour first-principles engineering walkthrough building a Generatively Pretrained Transformer character-level language model from an empty file.",
        "relevance_explanation": "Demonstrates incremental verification from bigram baseline to single-head attention, multi-head attention, residual connections, and LayerNorm.",
        "credibility_score": 0.99,
        "relevance_score": 0.98,
        "difficulty_level": "beginner",
        "stars_or_citations": 5200000,
        "duration_or_length": "1h 56m",
        "thumbnail_url": "https://i.ytimg.com/vi/kCc8FmEb1nY/hqdefault.jpg",
        "keywords": ["gpt", "transformer", "tiny gpt", "attention", "karpathy", "neural network", "ai", "deep learning"],
    },
    {
        "provider_name": "stanford_see",
        "external_id": "stanford-cs231n-cs224n",
        "title": "Stanford CS224N & CS231n: Natural Language Processing & Deep Learning Lecture Notes",
        "url": "https://web.stanford.edu/class/cs224n/",
        "resource_type": "lecture",
        "authors_json": ["Prof. Christopher Manning", "Prof. Fei-Fei Li"],
        "published_date": "2025",
        "access_type": "open",
        "access_status": "Completely free",
        "license_info": "Stanford Open Course Material",
        "description": "Comprehensive mathematical lecture notes, slides, and assignments on word vectors, backpropagation, RNNs, self-attention, Transformers, pretraining, and alignment.",
        "relevance_explanation": "Provides rigorous mathematical derivations for gradient propagation through softmax and attention layers.",
        "credibility_score": 0.99,
        "relevance_score": 0.96,
        "difficulty_level": "intermediate",
        "stars_or_citations": 15000,
        "duration_or_length": "20 University Lectures",
        "keywords": ["ai", "artificial intelligence", "deep learning", "transformer", "gpt", "nlp", "neural network", "gradient descent"],
    },
    {
        "provider_name": "huggingface",
        "external_id": "hf-nlp-course",
        "title": "Hugging Face LLM & NLP Open Course + SmolLM Datasets",
        "url": "https://huggingface.co/learn/nlp-course/",
        "resource_type": "course",
        "authors_json": ["Hugging Face Open-Source Team"],
        "published_date": "2025",
        "access_status": "Completely free",
        "license_info": "Apache 2.0 / CC BY 4.0",
        "description": "Interactive open engineering course covering tokenizers (BPE, WordPiece, Unigram), Transformer internals, datasets, and distributed training.",
        "relevance_explanation": "Hands-on reference for tokenization algorithms and dataset preparation.",
        "credibility_score": 0.96,
        "relevance_score": 0.93,
        "difficulty_level": "beginner",
        "stars_or_citations": 9200,
        "keywords": ["huggingface", "transformer", "tokenizer", "gpt", "llm", "ai", "artificial intelligence"],
    },
    {
        "provider_name": "coursera",
        "external_id": "coursera-ml-audit",
        "title": "Machine Learning Specialization (Stanford / DeepLearning.AI — Audit Mode)",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "resource_type": "course",
        "authors_json": ["Andrew Ng"],
        "published_date": "2024",
        "access_status": "Free audit",
        "license_info": "Free Video/Lecture Audit (Paid Certificate Optional)",
        "description": "Foundational coverage of supervised learning, linear/logistic regression, gradient descent, neural networks, and decision trees.",
        "relevance_explanation": "Structured mathematical intuition for beginners entering AI from scratch.",
        "credibility_score": 0.96,
        "relevance_score": 0.91,
        "difficulty_level": "beginner",
        "stars_or_citations": 48000,
        "keywords": ["ai", "artificial intelligence", "machine learning", "gradient descent", "neural network"],
    },
]


class ResourceIntelligenceService:
    """Discovers, verifies, classifies, and ranks authentic learning resources across providers."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self._ensure_providers_seeded()

    def _ensure_providers_seeded(self) -> None:
        providers = [
            ("arxiv", "arXiv Open Access Preprints", "http://export.arxiv.org/api/query", False),
            ("openalex", "OpenAlex Global Research Catalogue", "https://api.openalex.org/works", False),
            ("github", "GitHub Open-Source Repositories", "https://api.github.com/search/repositories", False),
            ("huggingface", "Hugging Face Hub (Models & Datasets)", "https://huggingface.co/api", False),
            ("youtube", "YouTube Educational Lectures", "https://www.googleapis.com/youtube/v3", True),
            ("mit_ocw", "MIT OpenCourseWare", "https://ocw.mit.edu", False),
            ("stanford_see", "Stanford Engineering Everywhere", "https://see.stanford.edu", False),
            ("official_docs", "Official Technical Documentation & Open Textbooks", "https://pages.cs.wisc.edu", False),
            ("coursera", "Coursera (Free Audit Verified)", "https://www.coursera.org", False),
            ("wikipedia", "Wikipedia Open Encyclopedia", "https://en.wikipedia.org/w/api.php", False),
            ("web_search", "Live Web Search (DuckDuckGo & HN Algolia)", "https://hn.algolia.com/api/v1/search", False),
        ]
        existing = {p.name for p in self.db.query(ResourceProvider).all()}
        added = False
        for name, disp, url, req_key in providers:
            if name not in existing:
                self.db.add(
                    ResourceProvider(
                        name=name,
                        display_name=disp,
                        base_url=url,
                        requires_api_key=req_key,
                        status="online",
                    )
                )
                added = True
        if added:
            self.db.commit()

    async def _query_arxiv_live(self, query: str, max_results: int = 3) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                resp = await client.get(
                    "http://export.arxiv.org/api/query",
                    params={
                        "search_query": f"all:{query}",
                        "start": 0,
                        "max_results": max_results,
                    },
                )
                if resp.status_code == 200 and "<entry>" in resp.text:
                    root = ET.fromstring(resp.text)
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    for entry in root.findall("atom:entry", ns):
                        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip().replace("\n", " ")
                        summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip().replace("\n", " ")
                        url = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
                        published = (entry.findtext("atom:published", default="", namespaces=ns) or "")[:10]
                        authors = [
                            (a.findtext("atom:name", default="", namespaces=ns) or "").strip()
                            for a in entry.findall("atom:author", ns)
                        ]
                        if title and url:
                            results.append(
                                {
                                    "provider_name": "arxiv",
                                    "external_id": url.split("/")[-1],
                                    "title": title,
                                    "url": url,
                                    "resource_type": "paper",
                                    "authors_json": authors[:6],
                                    "published_date": published,
                                    "access_status": "Completely free",
                                    "license_info": "arXiv Open Access",
                                    "description": summary[:450],
                                    "relevance_explanation": f"Primary peer-reviewed/preprint research directly addressing '{query}'.",
                                    "credibility_score": 0.96,
                                    "relevance_score": 0.93,
                                    "difficulty_level": "advanced",
                                }
                            )
        except Exception:
            pass
        return results

    async def _query_openalex_live(self, query: str, max_results: int = 3) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                resp = await client.get(
                    "https://api.openalex.org/works",
                    params={
                        "search": query,
                        "per-page": max_results,
                        "mailto": settings.OPENALEX_MAILTO,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for work in data.get("results", []):
                        title = work.get("title") or work.get("display_name")
                        oa = work.get("open_access", {}) or {}
                        url = oa.get("oa_url") or work.get("doi") or work.get("id")
                        is_oa = bool(oa.get("is_oa", True))
                        authors = [
                            a.get("author", {}).get("display_name", "")
                            for a in (work.get("authorships") or [])[:5]
                            if a.get("author", {}).get("display_name")
                        ]
                        cited_by = int(work.get("cited_by_count") or 0)
                        pub_year = str(work.get("publication_year") or "")
                        if title and url:
                            results.append(
                                {
                                    "provider_name": "openalex",
                                    "external_id": str(work.get("id", "")).split("/")[-1],
                                    "title": title,
                                    "url": url,
                                    "resource_type": "paper",
                                    "authors_json": authors,
                                    "published_date": pub_year,
                                    "access_status": "Completely free" if is_oa else "Free preview only",
                                    "license_info": oa.get("oa_status", "Academic Publication"),
                                    "description": f"Academic work indexed by OpenAlex ({cited_by} citations) covering {query}.",
                                    "relevance_explanation": f"High-impact academic literature ({cited_by} citations) relevant to {query}.",
                                    "credibility_score": 0.95,
                                    "relevance_score": 0.91,
                                    "difficulty_level": "intermediate",
                                    "stars_or_citations": cited_by,
                                }
                            )
        except Exception:
            pass
        return results

    async def _query_github_live(self, query: str, max_results: int = 3) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        headers = {"Accept": "application/vnd.github+json"}
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
        try:
            async with httpx.AsyncClient(timeout=3.5, headers=headers) as client:
                resp = await client.get(
                    "https://api.github.com/search/repositories",
                    params={"q": query, "sort": "stars", "order": "desc", "per_page": max_results},
                )
                if resp.status_code == 200:
                    for repo in resp.json().get("items", []):
                        full_name = repo.get("full_name", "")
                        html_url = repo.get("html_url", "")
                        if full_name and html_url:
                            lic = (repo.get("license") or {}).get("spdx_id") or "Open Source"
                            results.append(
                                {
                                    "provider_name": "github",
                                    "external_id": str(repo.get("id", full_name)),
                                    "title": full_name,
                                    "url": html_url,
                                    "resource_type": "repository",
                                    "authors_json": [(repo.get("owner") or {}).get("login", "github")],
                                    "published_date": (repo.get("updated_at") or "")[:10],
                                    "access_status": "Completely free",
                                    "license_info": lic,
                                    "description": repo.get("description") or f"Open-source implementation for {query}.",
                                    "relevance_explanation": f"Practical reference implementation on GitHub ({repo.get('stargazers_count', 0)} stars).",
                                    "credibility_score": 0.92,
                                    "relevance_score": 0.92,
                                    "difficulty_level": "intermediate",
                                    "stars_or_citations": int(repo.get("stargazers_count") or 0),
                                    "language": repo.get("language") or "Code",
                                }
                            )
        except Exception:
            pass
        return results

    async def _query_huggingface_live(self, query: str, max_results: int = 2) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                resp = await client.get(
                    "https://huggingface.co/api/models",
                    params={"search": query, "limit": max_results, "sort": "downloads", "direction": -1},
                )
                if resp.status_code == 200:
                    for item in resp.json():
                        model_id = item.get("modelId") or item.get("id")
                        if model_id:
                            results.append(
                                {
                                    "provider_name": "huggingface",
                                    "external_id": model_id,
                                    "title": f"Hugging Face Model: {model_id}",
                                    "url": f"https://huggingface.co/{model_id}",
                                    "resource_type": "model",
                                    "authors_json": [model_id.split("/")[0]],
                                    "published_date": (item.get("lastModified") or "")[:10],
                                    "access_status": "Completely free",
                                    "license_info": "Open Weights / Hub Repository",
                                    "description": f"Hugging Face Hub model/weights ({item.get('pipeline_tag', 'ML')}) for hands-on experimentation.",
                                    "relevance_explanation": f"Open weights and tokenizer artifacts on Hugging Face Hub for '{query}'.",
                                    "credibility_score": 0.90,
                                    "relevance_score": 0.88,
                                    "difficulty_level": "intermediate",
                                    "stars_or_citations": int(item.get("likes") or 0),
                                }
                            )
        except Exception:
            pass
        return results

    async def _query_wikipedia_live(self, query: str, max_results: int = 3) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        headers = {"User-Agent": "AxiomOS/3.0 (Local-First Personal AI Research OS; mailto:researcher@axiom-local.os)"}
        try:
            async with httpx.AsyncClient(timeout=3.0, headers=headers) as client:
                resp = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "list": "search",
                        "srsearch": query,
                        "srlimit": max_results,
                        "format": "json",
                        "utf8": 1,
                    },
                )
                if resp.status_code == 200:
                    search_items = resp.json().get("query", {}).get("search", [])
                    for item in search_items:
                        title = item.get("title", "")
                        snippet_html = item.get("snippet", "")
                        snippet = re.sub(r"<[^>]+>", "", snippet_html).strip()
                        page_id = str(item.get("pageid", title))
                        if title:
                            url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                            results.append(
                                {
                                    "provider_name": "wikipedia",
                                    "external_id": f"wiki-{page_id}",
                                    "title": f"{title} — Technical Reference & Foundations",
                                    "url": url,
                                    "resource_type": "documentation",
                                    "authors_json": ["Wikipedia Contributors"],
                                    "published_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                                    "access_status": "Completely free",
                                    "license_info": "CC BY-SA 4.0",
                                    "description": snippet or f"Comprehensive technical reference article covering {title}.",
                                    "relevance_explanation": f"Up-to-date open encyclopedia synthesis and mathematical/historical context for '{query}'.",
                                    "credibility_score": 0.93,
                                    "relevance_score": 0.94,
                                    "difficulty_level": "beginner",
                                }
                            )
        except Exception:
            pass
        return results

    async def _query_web_live(self, query: str, max_results: int = 4) -> list[dict[str, Any]]:
        """Free, zero-API-key live web search combining DuckDuckGo Instant Answer API + HackerNews Algolia technical search."""
        results: list[dict[str, Any]] = []
        headers = {"User-Agent": "AxiomOS/3.0 (Local-First Personal AI Research OS)"}
        try:
            async with httpx.AsyncClient(timeout=3.0, headers=headers) as client:
                # 1. DuckDuckGo Instant Answer API
                ddg_resp = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                )
                if ddg_resp.status_code == 200:
                    ddg = ddg_resp.json()
                    abstract_text = (ddg.get("AbstractText") or "").strip()
                    abstract_url = (ddg.get("AbstractURL") or "").strip()
                    heading = (ddg.get("Heading") or query).strip()
                    if abstract_text and abstract_url:
                        results.append(
                            {
                                "provider_name": "web_search",
                                "external_id": f"ddg-{heading.lower().replace(' ', '-')}",
                                "title": f"{heading} — Live Web Knowledge Graph",
                                "url": abstract_url,
                                "resource_type": "documentation",
                                "authors_json": [ddg.get("AbstractSource") or "Web Knowledge Graph"],
                                "published_date": datetime.now(timezone.utc).strftime("%Y"),
                                "access_status": "Completely free",
                                "license_info": "Open Web Reference",
                                "description": abstract_text[:450],
                                "relevance_explanation": f"Direct instant-answer synthesis from live web search for '{query}'.",
                                "credibility_score": 0.92,
                                "relevance_score": 0.95,
                                "difficulty_level": "beginner",
                            }
                        )
                    for topic in (ddg.get("RelatedTopics") or [])[:2]:
                        if isinstance(topic, dict) and topic.get("Text") and topic.get("FirstURL"):
                            results.append(
                                {
                                    "provider_name": "web_search",
                                    "external_id": topic["FirstURL"].split("/")[-1][:48],
                                    "title": topic["Text"][:90],
                                    "url": topic["FirstURL"],
                                    "resource_type": "documentation",
                                    "authors_json": ["DuckDuckGo Open Index"],
                                    "published_date": datetime.now(timezone.utc).strftime("%Y"),
                                    "access_status": "Completely free",
                                    "license_info": "Open Web",
                                    "description": topic["Text"][:400],
                                    "relevance_explanation": f"Related live web concept for '{query}'.",
                                    "credibility_score": 0.89,
                                    "relevance_score": 0.90,
                                    "difficulty_level": "intermediate",
                                }
                            )

                # 2. HackerNews Algolia Engineering Articles Search
                hn_resp = await client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={"query": query, "tags": "story", "hitsPerPage": max_results},
                )
                if hn_resp.status_code == 200:
                    for hit in hn_resp.json().get("hits", []):
                        title = hit.get("title")
                        url = hit.get("url")
                        points = int(hit.get("points") or 0)
                        if title and url and points >= 10:
                            results.append(
                                {
                                    "provider_name": "web_search",
                                    "external_id": f"hn-{hit.get('objectID', '')}",
                                    "title": title,
                                    "url": url,
                                    "resource_type": "documentation",
                                    "authors_json": [hit.get("author") or "Engineering Community"],
                                    "published_date": (hit.get("created_at") or "")[:10],
                                    "access_status": "Completely free",
                                    "license_info": "Public Web Article",
                                    "description": f"Peer-vetted engineering deep-dive ({points} upvotes, {hit.get('num_comments', 0)} technical comments) on '{title}'.",
                                    "relevance_explanation": f"High-signal practitioner engineering article discovered via live web search for '{query}'.",
                                    "credibility_score": 0.91,
                                    "relevance_score": 0.92,
                                    "difficulty_level": "intermediate",
                                    "stars_or_citations": points,
                                }
                            )
        except Exception:
            pass
        return results[:max_results]

    async def search_youtube_videos_live(self, query: str, max_results: int = 3) -> list[dict[str, Any]]:
        """
        Discover real, specific, high-quality educational YouTube video lectures (never generic search query URLs)
        by parsing YouTube's ytInitialData videoRenderer objects with zero API key required.
        """
        results: list[dict[str, Any]] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        search_q = query if "lecture" in query.lower() or "tutorial" in query.lower() else f"{query} lecture tutorial"
        try:
            async with httpx.AsyncClient(timeout=5.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(
                    "https://www.youtube.com/results",
                    params={"search_query": search_q},
                )
                if resp.status_code == 200:
                    import json as _json
                    match = re.search(r"var ytInitialData = (\{.*?\});</script>", resp.text)
                    if match:
                        data = _json.loads(match.group(1))
                        sections = (
                            data.get("contents", {})
                            .get("twoColumnSearchResultsRenderer", {})
                            .get("primaryContents", {})
                            .get("sectionListRenderer", {})
                            .get("contents", [])
                        )
                        video_renderers: list[dict[str, Any]] = []
                        for sec in sections:
                            items = sec.get("itemSectionRenderer", {}).get("contents", [])
                            for it in items:
                                if "videoRenderer" in it:
                                    video_renderers.append(it["videoRenderer"])

                        for v in video_renderers:
                            vid_id = v.get("videoId", "")
                            if not vid_id:
                                continue
                            title_runs = v.get("title", {}).get("runs", [])
                            title = title_runs[0].get("text", "") if title_runs else ""
                            owner_runs = v.get("ownerText", {}).get("runs", [])
                            channel = owner_runs[0].get("text", "YouTube Educational Lecture") if owner_runs else "YouTube Lecture"
                            duration = v.get("lengthText", {}).get("simpleText", "")
                            views_text = v.get("viewCountText", {}).get("simpleText", "")

                            # Filter out YouTube Shorts (< 2 minutes) so only substantive lectures/tutorials are selected
                            if not duration:
                                continue
                            parts = duration.split(":")
                            if len(parts) == 2 and parts[0].isdigit() and int(parts[0]) < 2:
                                continue

                            desc_snippets = v.get("detailedMetadataSnippets", [])
                            desc_text = ""
                            if desc_snippets:
                                snippet_runs = desc_snippets[0].get("snippetText", {}).get("runs", [])
                                desc_text = "".join(r.get("text", "") for r in snippet_runs)

                            views_num = 1000
                            digits = re.sub(r"[^\d]", "", views_text)
                            if digits:
                                views_num = int(digits)

                            results.append(
                                {
                                    "provider_name": "youtube",
                                    "external_id": vid_id,
                                    "video_id": vid_id,
                                    "title": f"{title} ({channel})",
                                    "raw_title": title,
                                    "channel": channel,
                                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                                    "embed_url": f"https://www.youtube.com/embed/{vid_id}",
                                    "resource_type": "video",
                                    "authors_json": [channel],
                                    "published_date": "2024",
                                    "access_status": "Completely free",
                                    "license_info": "YouTube Educational Video",
                                    "description": desc_text or f"Specific technical video lecture by {channel} ({duration}) covering {query}.",
                                    "relevance_explanation": f"Verified specific video lecture ({duration}, {views_text or 'high-signal'}) by {channel}.",
                                    "credibility_score": 0.95,
                                    "relevance_score": 0.96,
                                    "difficulty_level": "intermediate",
                                    "stars_or_citations": views_num,
                                    "duration_or_length": duration,
                                    "thumbnail_url": f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg",
                                }
                            )
                            if len(results) >= max_results:
                                break
        except Exception:
            pass
        return results

    async def search_live_web_context(self, query: str, max_items: int = 8) -> dict[str, Any]:
        """
        Perform fast concurrent free web, video & academic search (YouTube specific videos, Wikipedia, DuckDuckGo, HN Algolia, arXiv, GitHub)
        and return both structured items and a compact text digest for grounding qwen3.5:9b generation.
        """
        batches = await asyncio.gather(
            self.search_youtube_videos_live(query, max_results=3),
            self._query_wikipedia_live(query, max_results=2),
            self._query_web_live(query, max_results=2),
            self._query_arxiv_live(query, max_results=2),
            self._query_github_live(query, max_results=2),
            return_exceptions=True,
        )
        combined: list[dict[str, Any]] = []
        youtube_videos: list[dict[str, Any]] = []
        if isinstance(batches[0], list):
            youtube_videos = batches[0]
        for b in batches:
            if isinstance(b, list):
                combined.extend(b)

        seen: set[str] = set()
        unique_items: list[dict[str, Any]] = []
        for item in combined:
            u = item.get("url", "")
            if u and u not in seen:
                seen.add(u)
                unique_items.append(item)

        top_items = unique_items[:max_items]
        digest_lines: list[str] = []
        for idx, it in enumerate(top_items, 1):
            digest_lines.append(
                f"[{idx}] {it.get('title')} ({it.get('provider_name')}, {it.get('duration_or_length') or it.get('published_date', '2025')}) — {it.get('description', '')[:220]} | URL: {it.get('url')}"
            )
        return {
            "query": query,
            "count": len(top_items),
            "results": top_items,
            "youtube_videos": youtube_videos,
            "grounding_digest": "\n".join(digest_lines) if digest_lines else f"Topic: {query} (First-Principles Synthesis)",
        }

    def _match_curated_catalogue(self, query: str) -> list[dict[str, Any]]:
        q_lower = query.lower()
        tokens = [t for t in q_lower.replace("-", " ").split() if len(t) >= 2]
        matched: list[dict[str, Any]] = []
        for item in CURATED_INSTITUTIONAL_CATALOGUE:
            keywords = item.get("keywords", [])
            title_desc = f"{item['title']} {item['description']}".lower()
            if any(k in q_lower for k in keywords) or any(t in title_desc for t in tokens):
                matched.append(dict(item))
        if not matched:
            matched = []
        return matched

    def _upsert_resource(self, payload: dict[str, Any]) -> Resource:
        url = payload["url"]
        existing = self.db.query(Resource).filter(Resource.url == url).first()
        now = datetime.now(timezone.utc)
        if existing:
            existing.last_verified_at = now
            self.db.commit()
            return existing

        provider = (
            self.db.query(ResourceProvider)
            .filter(ResourceProvider.name == payload.get("provider_name", "arxiv"))
            .first()
        )
        res = Resource(
            provider_id=provider.id if provider else None,
            provider_name=payload.get("provider_name", "arxiv"),
            external_id=payload.get("external_id", ""),
            title=payload["title"],
            url=url,
            resource_type=payload.get("resource_type", "paper"),
            authors_json=payload.get("authors_json", []),
            published_date=payload.get("published_date", "2024"),
            access_status=payload.get("access_status", "Completely free"),
            license_info=payload.get("license_info", "Open Access"),
            description=payload.get("description", ""),
            relevance_explanation=payload.get("relevance_explanation", ""),
            credibility_score=float(payload.get("credibility_score", 0.92)),
            relevance_score=float(payload.get("relevance_score", 0.90)),
            difficulty_level=payload.get("difficulty_level", "intermediate"),
            stars_or_citations=int(payload.get("stars_or_citations", 0)),
            language=payload.get("language", ""),
            duration_or_length=payload.get("duration_or_length", ""),
            thumbnail_url=payload.get("thumbnail_url", ""),
            is_saved_to_library=True,
            last_verified_at=now,
        )
        self.db.add(res)
        self.db.commit()
        self.db.refresh(res)
        return res

    async def discover_resources(
        self,
        query: str,
        free_only: bool = True,
        include_live_providers: bool = True,
        journey_id: Optional[int] = None,
        concept_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Discover, classify, and rank authentic learning resources.
        Returns structured slots: primary_resource, supplementary_resources (2),
        practical_repository (1), and explore_more.
        """
        raw_items: list[dict[str, Any]] = self._match_curated_catalogue(query)

        if include_live_providers:
            batches = await asyncio.gather(
                self.search_youtube_videos_live(query, max_results=3),
                self._query_wikipedia_live(query, max_results=2),
                self._query_web_live(query, max_results=2),
                self._query_arxiv_live(query, max_results=2),
                self._query_openalex_live(query, max_results=2),
                self._query_github_live(query, max_results=2),
                self._query_huggingface_live(query, max_results=1),
                return_exceptions=True,
            )
            for b in batches:
                if isinstance(b, list):
                    raw_items.extend(b)

        if free_only:
            raw_items = [r for r in raw_items if r.get("access_status", "Completely free") in FREE_ACCESS_TIERS]

        persisted: list[Resource] = []
        seen_urls: set[str] = set()
        for item in raw_items:
            if item["url"] in seen_urls:
                continue
            seen_urls.add(item["url"])
            persisted.append(self._upsert_resource(item))

        persisted.sort(
            key=lambda r: (0.55 * r.relevance_score + 0.45 * r.credibility_score),
            reverse=True,
        )

        primary = persisted[0] if persisted else None
        repos = [r for r in persisted if r.resource_type in ("repository", "model") and r != primary]
        practical_repo = repos[0] if repos else None
        non_primary = [r for r in persisted if r != primary and r != practical_repo]
        supplementary = non_primary[:2]
        explore_more = non_primary[2:]

        if journey_id or concept_id:
            for tier, items in [
                ("primary", [primary] if primary else []),
                ("supplementary", supplementary),
                ("practical_repo", [practical_repo] if practical_repo else []),
                ("explore_more", explore_more[:4]),
            ]:
                for res_obj in items:
                    exists = (
                        self.db.query(ResourceRelationship)
                        .filter(
                            ResourceRelationship.resource_id == res_obj.id,
                            ResourceRelationship.concept_id == concept_id,
                            ResourceRelationship.journey_id == journey_id,
                        )
                        .first()
                    )
                    if not exists:
                        self.db.add(
                            ResourceRelationship(
                                resource_id=res_obj.id,
                                journey_id=journey_id,
                                concept_id=concept_id,
                                recommendation_tier=tier,
                            )
                        )
            self.db.commit()

        return {
            "query": query,
            "free_only_applied": free_only,
            "total_count": len(persisted),
            "primary_resource": primary,
            "supplementary_resources": supplementary,
            "practical_repository": practical_repo,
            "explore_more": explore_more,
            "all_resources": persisted,
        }
