"""Axiom OS — Universal Domain Intelligence & Competency Engine (V6.1)

Provides domain-specific taxonomy, prerequisite validation, and dynamic phase structures
for ANY subject: Computer Science, Mathematics, Natural Sciences, Computational Neuroscience,
Music (Piano/Guitar), Languages (French/Spanish), History, Literature/Creative Writing, Business, etc.
"""
from __future__ import annotations

import math
from typing import Any, Optional


class DomainType:
    COMPUTATIONAL_NEUROSCIENCE = "computational_neuroscience"
    SOFTWARE_SYSTEMS = "software_systems"
    MATHEMATICS = "mathematics"
    NATURAL_SCIENCES = "natural_sciences"
    MUSIC_ARTS = "music_arts"
    LANGUAGES = "languages"
    HISTORY_HUMANITIES = "history_humanities"
    WRITING_LITERATURE = "writing_literature"
    BUSINESS_ECONOMICS = "business_economics"


class DomainProfile:
    """Represents the cognitive, pedagogical, and practical profile of a learning domain."""

    def __init__(
        self,
        domain_key: str,
        display_name: str,
        foundational_prerequisites: list[str],
        core_knowledge_areas: list[str],
        practice_activity_types: list[str],
        default_builder_activity: str,
        assessment_methods: list[str],
        sample_phase_templates: list[str],
    ) -> None:
        self.domain_key = domain_key
        self.display_name = display_name
        self.foundational_prerequisites = foundational_prerequisites
        self.core_knowledge_areas = core_knowledge_areas
        self.practice_activity_types = practice_activity_types
        self.builder_activity_types = practice_activity_types
        self.default_builder_activity = default_builder_activity
        self.assessment_methods = assessment_methods
        self.sample_phase_templates = sample_phase_templates

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.domain_key == other
        if isinstance(other, DomainProfile):
            return self.domain_key == other.domain_key
        return False

    def __hash__(self) -> int:
        return hash(self.domain_key)

    def __str__(self) -> str:
        return self.domain_key

    def __repr__(self) -> str:
        return f"DomainProfile('{self.domain_key}')"


class DomainIntelligenceService:
    """Infers subject domain, constructs competency maps, and designs dynamic subject-specific phases."""

    DOMAINS: dict[str, DomainProfile] = {
        "computational_neuroscience": DomainProfile(
            domain_key="computational_neuroscience",
            display_name="Computational Neuroscience & Neural Engineering",
            foundational_prerequisites=[
                "Cellular biology & neuron anatomy basics",
                "Basic electricity (charge, current, voltage, resistance, capacitance)",
                "Elementary functions & rates of change",
            ],
            core_knowledge_areas=[
                "Neuron anatomy & cell biology",
                "Resting membrane potential & ion channels",
                "Action potential dynamics & Hodgkin-Huxley formulation",
                "Synaptic transmission & chemical signalling",
                "Neural coding & rate/temporal codes",
                "Network dynamics & collective population behaviour",
                "Synaptic plasticity & learning mechanisms",
                "Sensory & motor system models",
                "Neural signal analysis & brain-computer interfaces",
            ],
            practice_activity_types=[
                "diagram_labeling",
                "signal_flow_trace",
                "numerical_simulation",
                "spike_train_analysis",
                "biophysical_parameter_tuning",
            ],
            default_builder_activity="interactive_exercise",
            assessment_methods=[
                "First-principles causal explanation",
                "Biological-to-computational mapping check",
                "Invariant parameter sensitivity analysis",
            ],
            sample_phase_templates=[
                "Biological & Biophysical Foundations",
                "Membrane Dynamics & Action Potentials",
                "Mathematical Neuron Models & Simulations",
                "Synaptic Transmission & Plasticity Rules",
                "Neural Coding & Spike Train Analysis",
                "Population Dynamics & Network Oscillations",
                "Brain Systems & Sensory Computation",
                "Independent Modeling Capstone & Research Synthesis",
            ],
        ),
        "software_systems": DomainProfile(
            domain_key="software_systems",
            display_name="Computer Science & Systems Engineering",
            foundational_prerequisites=[
                "Variables, data types, and memory representation",
                "Control flow (branching, loops, functions)",
                "Basic complexity notation (time and space)",
            ],
            core_knowledge_areas=[
                "State machines & execution invariants",
                "Low-level memory management & address spaces",
                "Algorithmic complexity & data structures",
                "Concurrency, synchronization & race conditions",
                "I/O subsystems, file systems & serialization",
                "Network protocols & distributed failure modes",
                "Performance profiling & cache optimization",
                "Fault tolerance, testing harnesses & production hardening",
            ],
            practice_activity_types=[
                "code_lab",
                "test_driven_implementation",
                "controlled_failure_challenge",
                "profiling_and_optimization",
            ],
            default_builder_activity="code_lab",
            assessment_methods=[
                "Automated assertion test execution",
                "Invariant proof and state validation",
                "Controlled failure / Break-It debugging",
            ],
            sample_phase_templates=[
                "Foundational State Primitives & Invariants",
                "Core Algorithms & Low-Level Mechanics",
                "Systems Architecture & Pipeline Construction",
                "Concurrency, Scheduling & Resource Management",
                "Controlled Failure, Resilience & Boundary Testing",
                "Production-Grade Systems Capstone",
            ],
        ),
        "mathematics": DomainProfile(
            domain_key="mathematics",
            display_name="Pure & Applied Mathematics",
            foundational_prerequisites=[
                "Arithmetic operations & real number properties",
                "Algebraic identities & polynomial manipulation",
                "Function concepts (domain, codomain, composition)",
            ],
            core_knowledge_areas=[
                "Axiomatic foundations & formal logic",
                "Linear algebra (vectors, spaces, transformations, eigensystems)",
                "Calculus (limits, continuity, derivatives, integrals)",
                "Differential equations & dynamical systems",
                "Probability theory & stochastic processes",
                "Optimization & variational methods",
                "Mathematical modeling of natural phenomena",
            ],
            practice_activity_types=[
                "problem_solving",
                "derivation_steps",
                "counterexample_discovery",
                "computational_verification",
            ],
            default_builder_activity="problem_solving",
            assessment_methods=[
                "Formal step-by-step derivation check",
                "Counterexample refutation",
                "Numerical property verification",
            ],
            sample_phase_templates=[
                "Axiomatic Primitives & Notation",
                "Linear Transformations & Invariants",
                "Continuous Dynamics & Calculus Foundations",
                "Differential Systems & State Spaces",
                "Stochastic Modeling & Probability Measures",
                "Advanced Mathematical Synthesis & Theorems",
            ],
        ),
        "natural_sciences": DomainProfile(
            domain_key="natural_sciences",
            display_name="Natural Sciences (Physics, Chemistry, Biology)",
            foundational_prerequisites=[
                "Units of measurement & scientific notation",
                "Atomic structure & conservation laws",
                "Empirical observation & hypothesis formulation",
            ],
            core_knowledge_areas=[
                "Conservation principles (mass, energy, charge, momentum)",
                "Thermodynamics, kinetics & equilibrium",
                "Molecular structure, chemical bonding & orbitals",
                "Reaction mechanisms & pathway dynamics",
                "Cellular machinery, genetics & evolution",
                "Experimental design, controls & error analysis",
            ],
            practice_activity_types=[
                "experiment_design",
                "molecular_modeling",
                "reaction_balancing",
                "data_interpretation",
            ],
            default_builder_activity="design_experiment",
            assessment_methods=[
                "Hypothesis vs actual outcome analysis",
                "Thermodynamic feasibility justification",
                "Error propagation & boundary audit",
            ],
            sample_phase_templates=[
                "Empirical Foundations & Conservation Laws",
                "Atomic & Molecular Structural Foundations",
                "Equilibrium, Kinetics & Dynamic Systems",
                "Complex Reaction Pathways & Catalysis",
                "Scientific Experimentation & Data Synthesis",
            ],
        ),
        "music_arts": DomainProfile(
            domain_key="music_arts",
            display_name="Music Theory, Performance & Composition",
            foundational_prerequisites=[
                "Acoustic properties of sound (pitch, frequency, timbre)",
                "Keyboard or instrument physical layout & posture",
                "Basic pulse, rhythm, and tempo",
            ],
            core_knowledge_areas=[
                "Instrument geography & ergonomics",
                "Rhythm, meter, and notation literacy",
                "Pitch, intervals, and scalar construction",
                "Triads, seventh chords, and voicing",
                "Diatonic harmony & voice leading",
                "Cadences, chord progressions, and modulation",
                "Musical forms & textural analysis",
                "Improvisation, ear training & composition",
            ],
            practice_activity_types=[
                "instrument_drill",
                "interval_recognition",
                "chord_construction",
                "score_analysis",
                "composition_prompt",
            ],
            default_builder_activity="interactive_exercise",
            assessment_methods=[
                "Ear training recognition check",
                "Harmonic progression voice-leading audit",
                "Hands-on performance / composition critique",
            ],
            sample_phase_templates=[
                "Sound Physics, Instrument Geography & Posture",
                "Rhythm, Meter & Fundamental Literacy",
                "Intervals, Scales & Melodic Contours",
                "Harmony, Triads & Functional Progressions",
                "Voice Leading, Texture & Formal Architecture",
                "Creative Composition & Performance Synthesis",
            ],
        ),
        "languages": DomainProfile(
            domain_key="languages",
            display_name="Language Acquisition & Linguistics",
            foundational_prerequisites=[
                "Phonetic awareness & sound production mechanics",
                "Grammatical concepts in native language (parts of speech)",
                "Cultural context of communication",
            ],
            core_knowledge_areas=[
                "Phonetics, vowel sounds & pronunciation rules",
                "High-frequency essential vocabulary & greetings",
                "Sentence structure & fundamental grammar (tenses, agreement)",
                "Everyday survival dialogues & social interaction",
                "Listening comprehension & contextual decoding",
                "Reading authentic texts & idiomatic expressions",
                "Complex communication, subjunctive & nuanced discourse",
                "Cultural fluency & spontaneous conversational mastery",
            ],
            practice_activity_types=[
                "pronunciation_drill",
                "dialogue_practice",
                "contextual_translation",
                "listening_comprehension",
                "composition_scenario",
            ],
            default_builder_activity="dialogue_practice",
            assessment_methods=[
                "Pronunciation accuracy & communicative success",
                "Grammatical agreement & structural accuracy",
                "Interactive scenario roleplay defense",
            ],
            sample_phase_templates=[
                "Phonetics, Pronunciation & Basic Greetings",
                "Essential Vocabulary & Present Tense Structures",
                "Daily Life Conversations & Listening Comprehension",
                "Past & Future Tenses in Narrative Context",
                "Nuanced Expression, Subjunctive & Complex Dialogue",
                "Full Conversational & Cultural Fluency",
            ],
        ),
        "history_humanities": DomainProfile(
            domain_key="history_humanities",
            display_name="History, Philosophy & Humanities",
            foundational_prerequisites=[
                "Chronological understanding & temporal markers",
                "Primary vs. secondary evidence distinction",
                "Critical questioning of authorial intent & bias",
            ],
            core_knowledge_areas=[
                "Historical evidence & archival methodology",
                "Chronological frameworks & socio-economic context",
                "Ideological, cultural & geopolitical driving forces",
                "Primary source close reading & perspective critique",
                "Historiographical debates & competing schools of thought",
                "Causal networks (contingency vs structural determination)",
                "Independent thesis formulation & archival synthesis",
            ],
            practice_activity_types=[
                "source_analysis",
                "historiographical_debate",
                "causal_map_construction",
                "evidence_synthesis_essay",
            ],
            default_builder_activity="source_analysis",
            assessment_methods=[
                "Primary source evaluation & bias audit",
                "Argumentative thesis defense against counter-evidence",
                "Historiographical perspective comparison",
            ],
            sample_phase_templates=[
                "Historical Method, Evidence & Epistemology",
                "Origins, Geography & Cultural Primitives",
                "Institutional, Economic & Political Structures",
                "Turning Points, Crises & Transformative Shifts",
                "Historiographical Debates & Competing Evidence",
                "Archival Synthesis & Independent Monograph Defense",
            ],
        ),
        "writing_literature": DomainProfile(
            domain_key="writing_literature",
            display_name="Creative Writing, Literature & Rhetoric",
            foundational_prerequisites=[
                "Sentence-level clarity and syntax awareness",
                "Habit of keen sensory observation",
                "Appreciation of narrative structure",
            ],
            core_knowledge_areas=[
                "Sensory observation, detail & setting generation",
                "Character desire, motivation & internal conflict",
                "Scene structure, pacing & dramatic tension",
                "Point of view, voice & stylistic tone",
                "Dialogue, subtext & unspoken communication",
                "Plot architecture (inciting incident, climax, resolution)",
                "Thematic coherence, symbolism & metaphor",
                "The art of aggressive revision and structural editing",
            ],
            practice_activity_types=[
                "scene_drafting",
                "character_monologue",
                "sensory_sketching",
                "structural_editing_drill",
            ],
            default_builder_activity="interactive_exercise",
            assessment_methods=[
                "Rubric-based character motivation & subtext audit",
                "Scene dramatic tension evaluation",
                "Stylistic voice consistency review",
            ],
            sample_phase_templates=[
                "Observation, Sensory Detail & Image Craft",
                "Character Motivation, Desire & Wound",
                "Scene Dynamics, Conflict & Micro-Tension",
                "Dialogue, Subtext & Unspoken Energy",
                "Plot Architecture, Pacing & Thematic Resonance",
                "Aggressive Revision & Polished Portfolio Piece",
            ],
        ),
        "business_economics": DomainProfile(
            domain_key="business_economics",
            display_name="Economics, Finance & Business Strategy",
            foundational_prerequisites=[
                "Concept of opportunity cost & scarcity",
                "Basic numerical literacy & percentages",
                "Incentive structures in human decision-making",
            ],
            core_knowledge_areas=[
                "Supply, demand, and price equilibrium",
                "Marginal thinking & elasticity of demand",
                "Market structures (perfect competition to monopoly)",
                "Financial statements & cash flow dynamics",
                "Valuation, discounting & capital allocation",
                "Competitive advantage, barriers to entry & moats",
                "Risk management, asymmetric payoff & game theory",
                "Strategic execution & decision-making under uncertainty",
            ],
            practice_activity_types=[
                "market_equilibrium_model",
                "financial_statement_analysis",
                "case_study_defense",
                "decision_tree_construction",
            ],
            default_builder_activity="problem_solving",
            assessment_methods=[
                "Unit economics & margin calculation check",
                "Competitive moat thesis defense",
                "Asymmetric risk scenario audit",
            ],
            sample_phase_templates=[
                "Scarcity, Incentives & Market Primitives",
                "Supply, Demand & Price Mechanics",
                "Firm Economics, Cost Curves & Structure",
                "Financial Statements & Capital Dynamics",
                "Strategic Moats & Game Theory in Markets",
                "Independent Strategic Case & Valuation Capstone",
            ],
        ),
    }

    @classmethod
    def infer_domain(cls, user_intent: str) -> DomainProfile:
        """Infer domain profile from user intent string using semantic keyword indicators."""
        text = user_intent.lower()

        # Check Computational Neuroscience first (specialized hybrid)
        if any(w in text for w in ["neuroscience", "neural signal", "brain computer", "bci", "eeg", "hodgkin", "neuron", "synapse", "cortex", "action potential"]):
            return cls.DOMAINS["computational_neuroscience"]

        # Music / Instruments
        if any(w in text for w in ["piano", "guitar", "music", "chord", "melody", "harmony", "tempo", "scale", "instrument", "flute", "violin"]):
            return cls.DOMAINS["music_arts"]

        # Languages
        if any(w in text for w in ["french", "spanish", "german", "japanese", "mandarin", "italian", "language", "grammar", "vocabulary", "pronunciation", "speak"]):
            return cls.DOMAINS["languages"]

        # History / Humanities / Philosophy
        if any(w in text for w in ["history", "ancient", "war", "civilization", "empire", "revolution", "medieval", "historiography", "philosophy", "ethics"]):
            return cls.DOMAINS["history_humanities"]

        # Writing / Literature
        if any(w in text for w in ["creative writing", "novel", "fiction", "screenplay", "storytelling", "poetry", "literature", "character development"]):
            return cls.DOMAINS["writing_literature"]

        # Mathematics
        if any(w in text for w in ["math", "calculus", "linear algebra", "geometry", "trigonometry", "algebra", "differential equation", "topology", "statistics"]):
            return cls.DOMAINS["mathematics"]

        # Natural Sciences (Chemistry, Physics, Biology)
        if any(w in text for w in ["chemistry", "organic chemistry", "physics", "quantum mechanics", "thermodynamics", "biology", "genetics", "molecule"]):
            return cls.DOMAINS["natural_sciences"]

        # Business / Economics / Finance
        if any(w in text for w in ["economics", "finance", "business", "stock market", "investing", "startup", "accounting", "venture capital"]):
            return cls.DOMAINS["business_economics"]

        # Default fallback to Software Systems
        return cls.DOMAINS["software_systems"]

    @classmethod
    def generate_dynamic_phases(
        cls,
        domain_profile: DomainProfile | str,
        total_days: int,
        experience_level: str = "beginner",
        user_intent: str = "",
    ) -> list[dict[str, Any]]:
        """
        Dynamically synthesize subject-specific phases tailored to duration, domain, and experience level.
        NEVER applies generic software engineering phase templates to non-engineering domains!
        """
        if isinstance(domain_profile, str):
            domain_profile = cls.DOMAINS.get(domain_profile) or cls.DOMAINS["software_systems"]

        templates = domain_profile.sample_phase_templates
        days = max(1, total_days)

        # Determine number of phases based on duration
        if days <= 7:
            num_phases = 1
        elif days <= 15:
            num_phases = 2
        elif days <= 30:
            num_phases = 4
        elif days <= 60:
            num_phases = 5
        elif days <= 90:
            num_phases = 6
        elif days <= 180:
            num_phases = 8
        else:
            num_phases = 12

        # Partition days across num_phases cleanly so phases[-1]["end_day"] == days
        bounds = []
        base = days // num_phases
        rem = days % num_phases
        cur = 1
        for i in range(num_phases):
            p_len = base + (1 if i < rem else 0)
            bounds.append((cur, cur + p_len - 1))
            cur += p_len

        phases: list[dict[str, Any]] = []

        # Select domain-specific template names
        if num_phases == 1:
            selected_names = [templates[0]]
        elif num_phases == 2:
            selected_names = [templates[0], templates[-1]]
        elif num_phases <= len(templates):
            # Sample evenly from templates
            indices = [int(i * (len(templates) - 1) / (num_phases - 1)) for i in range(num_phases)]
            selected_names = [templates[i] for i in indices]
        else:
            selected_names = []
            for i in range(num_phases):
                base_name = templates[i % len(templates)]
                cycle = (i // len(templates)) + 1
                if cycle > 1:
                    selected_names.append(f"{base_name} (Part {cycle})")
                else:
                    selected_names.append(base_name)

        for i, (s_day, e_day) in enumerate(bounds):
            raw_name = selected_names[i]

            # Adjust phase description for experience level
            if experience_level == "beginner" and i == 0:
                focus = f"Zero-assumed-knowledge foundations: essential primitives, physical intuition, and core terminology of {domain_profile.display_name}."
            elif experience_level == "advanced" and i == 0:
                focus = f"Accelerated synthesis of foundational invariants and transition directly to high-order dynamics."
            else:
                focus = f"Comprehensive development and hands-on practice in {raw_name}."

            phases.append({
                "phase_number": i + 1,
                "name": f"Phase {i + 1}: {raw_name}",
                "start_day": s_day,
                "end_day": e_day,
                "focus": focus,
                "domain_key": domain_profile.domain_key,
                "default_builder_activity": domain_profile.default_builder_activity,
            })

        return phases

    @classmethod
    def validate_prerequisite_graph_acyclic(
        cls,
        nodes: list[dict[str, Any]],
        edges: Optional[list[tuple[str, str]]] = None,
    ) -> tuple[bool, list[str]]:
        """
        Validates that prerequisite dependencies form a strict Directed Acyclic Graph (DAG)
        using Kahn's topological sort algorithm. Returns (is_acyclic: bool, topological_order: list[str]).
        """
        node_ids = [str(n["id"]) for n in nodes]
        in_degree: dict[str, int] = {nid: 0 for nid in node_ids}
        adjacency: dict[str, list[str]] = {nid: [] for nid in node_ids}

        if edges is None:
            edges = []
            for n in nodes:
                nid = str(n.get("id"))
                for prereq in n.get("prerequisites", []):
                    edges.append((str(prereq), nid))

        for u, v in edges:
            u_str, v_str = str(u), str(v)
            if u_str in adjacency and v_str in in_degree:
                adjacency[u_str].append(v_str)
                in_degree[v_str] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        topological_order: list[str] = []

        while queue:
            curr = queue.pop(0)
            topological_order.append(curr)
            for neighbor in adjacency.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        is_acyclic = len(topological_order) == len(nodes)
        return is_acyclic, topological_order
