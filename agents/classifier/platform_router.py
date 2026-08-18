"""Deterministic platform routing for the Quantum Advantage Evaluator.

Routes problems to QUANTUM, HPC, or AI_ML based on:
1. KB algorithm match scores + Troyer filter evaluation (from stored data)
2. Problem domain keyword detection for HPC and AI/ML
3. Decision matrix with clear thresholds

This runs BEFORE the LLM and provides structured evidence that constrains
the LLM's output, preventing hallucinated classifications.
"""

from typing import Dict, Any, List, Optional

# Speedup classes that indicate genuine quantum advantage
STRONG_QUANTUM_SPEEDUPS = {"exponential", "superpolynomial"}
WEAK_QUANTUM_SPEEDUPS = {"quadratic", "quadratic_at_most", "polynomial"}
NO_QUANTUM_ADVANTAGE = {"none_proven", "dequantized", "varies"}

# AI/ML domain indicators  if these dominate, recommend AI_ML
AI_ML_KEYWORDS = [
    "classify", "classifier", "classification", "image recognition", "object detection",
    "natural language", "nlp", "text generation", "chatbot", "sentiment",
    "recommendation", "predict", "prediction", "forecast", "regression",
    "neural network", "deep learning", "machine learning", "training",
    "computer vision", "image segmentation", "generative", "diffusion model",
    "transformer", "llm", "language model", "fine-tune", "reinforcement learning",
    "anomaly detection", "clustering", "dimensionality reduction",
    "speech recognition", "translation", "summarization",
]

# HPC domain indicators  if these dominate, recommend HPC
HPC_KEYWORDS = [
    "fluid dynamics", "cfd", "navier-stokes", "turbulence simulation",
    "turbulent flow", "turbulence", "mach number", "reynolds number",
    "finite element", "fea", "structural analysis", "stress analysis",
    "molecular dynamics", "classical md", "force field",
    "weather prediction", "climate simulation", "ocean modeling",
    "seismic", "reservoir simulation", "oil and gas",
    "crash simulation", "aerodynamics", "wind tunnel", "aircraft",
    "rendering", "ray tracing", "monte carlo radiation",
    "genome assembly", "sequence alignment", "blast",
    "n-body classical", "gravitational simulation",
    "large linear system", "sparse matrix", "eigenvalue decomposition",
    "signal processing", "fft", "convolution",
    "combustion", "plasma physics classical", "thermal simulation",
    # Classical optimisation. Quantum offers at best a quadratic speedup here,
    # which does not survive QEC overhead, so these belong on classical compute.
    "portfolio", "mean-variance", "linear programming", "mixed-integer",
    "vehicle routing", "supply chain", "scheduling problem",
]

# Quantum domain indicators  problems naturally suited to quantum
QUANTUM_KEYWORDS = [
    "quantum simulation", "hamiltonian", "ground state energy",
    "quantum chemistry", "molecular orbital", "electronic structure",
    "factoring", "rsa", "discrete logarithm", "elliptic curve crypto",
    "quantum phase estimation", "eigenvalue",
    "many-body", "strongly correlated", "hubbard model",
    "lattice gauge", "qcd", "quark", "gluon", "sign problem",
    "quantum walk", "exciton transport", "photosynthesis",
    "topological invariant", "jones polynomial", "knot",
    "boson sampling", "quantum supremacy",
    "quantum error correction", "surface code", "logical qubit",
    "nuclear structure", "nuclear force",
]

# Electronic-structure classification from Moerchen, Low, Weymuth, Liu, Troyer
# and Reiher, arXiv:2409.08910. Class-2 structures admit no reasonably sized set
# of important determinants, which is precisely what defeats coupled cluster and
# makes them the target for quantum computation. FeMoco is the paper's
# prototypical example. Class-1 structures are dominated by a few determinants
# and are usually already tractable classically.
CLASS_2_MARKERS = [
    "femoco", "nitrogenase", "iron-sulfur", "iron sulfur", "fe-s cluster",
    "multi-reference", "multireference", "multi-configurational",
    "multiconfigurational", "open-shell", "open shell", "diradical",
    "biradical", "strongly correlated", "transition metal cluster",
    "polynuclear", "spin crossover", "bond dissociation", "transition state",
    "active site", "catalytic centre", "catalytic center",
]
CLASS_1_MARKERS = [
    "closed-shell", "closed shell", "single-reference", "single reference",
    "weakly correlated", "equilibrium geometry", "well-separated",
    "mean-field", "hartree-fock is sufficient", "dft is sufficient",
]

# Algorithms whose advantage depends on starting from a guiding state with
# useful overlap. Factoring, search and sampling do not.
GUIDING_STATE_MARKERS = [
    "phase estimation", "ground state", "ground-state", "eigenvalue",
    "chemistry", "electronic structure", "hamiltonian simulation",
    "vqe", "variational quantum eigensolver", "qpe",
]


def _any_marker(text: str, markers: List[str]) -> bool:
    lowered = text.lower()
    return any(m in lowered for m in markers)


def classify_electronic_structure(problem_description: str) -> str:
    """Label the problem class-1, class-2 or unknown per arXiv:2409.08910."""
    if _any_marker(problem_description, CLASS_2_MARKERS):
        return "class_2"
    if _any_marker(problem_description, CLASS_1_MARKERS):
        return "class_1"
    return "unknown"


def _keyword_score(text: str, keywords: List[str]) -> float:
    """Count fraction of keyword list that appears in text."""
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw in text_lower)
    return hits / len(keywords) if keywords else 0.0


def compute_troyer_filters(algorithm: Dict[str, Any], problem_description: str = "") -> Dict[str, bool]:
    """Compute Troyer's utility-scale filters from stored algorithm data.

    This is deterministic  derived directly from the algorithm's properties,
    not generated by the LLM.

    F1-F5 follow Hoefler, Haener and Troyer, CACM 2023. F6 adds the guiding-state
    requirement from Moerchen et al., arXiv:2409.08910.
    """
    speedup = algorithm.get("speedup_class", "unknown")
    io_bottleneck = algorithm.get("io_bottleneck", True)
    naturally_quantum = algorithm.get("naturally_quantum", False)
    troyer_verdict = algorithm.get("troyer_verdict", "INCONCLUSIVE")

    return {
        "F1_proven_speedup": speedup in STRONG_QUANTUM_SPEEDUPS,
        "F2_io_survives": not io_bottleneck,
        "F3_qec_survives": speedup not in WEAK_QUANTUM_SPEEDUPS,
        "F4_naturally_quantum": naturally_quantum,
        "F5_crossover_feasible": troyer_verdict == "QUANTUM_ADVANTAGE",
        "F6_state_preparation": compute_state_preparation_filter(algorithm, problem_description),
    }


def compute_state_preparation_filter(algorithm: Dict[str, Any], problem_description: str = "") -> bool:
    """F6: is a guiding state with useful overlap both needed and obtainable?

    Per arXiv:2409.08910, mean-field overlap decays with system size, so an
    eigenvalue algorithm is only worth running where the structure is genuinely
    multi-configurational. A single-reference problem fails this filter because
    coupled cluster already answers it, not because the quantum circuit is
    unbuildable.

    Algorithms that need no guiding state pass: the filter does not apply.

    Applicability is decided from the problem as well as the matched algorithm.
    Deciding it from the algorithm name alone meant a poor retrieval switched the
    filter off entirely: a single-reference water dimer matched "Coupled Classical
    Oscillators Simulation", no marker hit, and F6 passed by default on exactly
    the kind of problem it exists to reject.
    """
    structure = classify_electronic_structure(problem_description)
    identity = f"{algorithm.get('name', '')} {algorithm.get('category', '')}"
    if not _any_marker(identity, GUIDING_STATE_MARKERS) and structure == "unknown":
        return True
    return structure != "class_1"


def route_platform(
    problem_description: str,
    kb_matches: List[Dict[str, Any]],
    search_score: float = 0.0,
) -> Dict[str, Any]:
    """Deterministic platform routing based on KB matches + keyword analysis.

    Returns a routing decision with structured evidence for the LLM.

    Decision matrix:
    1. If best KB match has QUANTUM_ADVANTAGE verdict AND strong speedup
       AND the problem text itself reads as quantum → QUANTUM
    2. If AI/ML keyword score > HPC keyword score AND > quantum keyword score → AI_ML
    3. If HPC keyword score > AI/ML keyword score AND > quantum keyword score → HPC
    4. If best KB match exists but has weak/no advantage → HPC (with quantum context)
    5. Default → let LLM decide (INCONCLUSIVE)

    Rule 1 is deliberately conservative. Retrieval returns a top match for every
    query, so the KB match alone cannot establish that a problem is quantum.
    """
    # Compute keyword domain scores
    ai_score = _keyword_score(problem_description, AI_ML_KEYWORDS)
    hpc_score = _keyword_score(problem_description, HPC_KEYWORDS)
    quantum_score = _keyword_score(problem_description, QUANTUM_KEYWORDS)

    # Compute KB-based quantum assessment
    best_match = kb_matches[0] if kb_matches else None
    troyer_filters = compute_troyer_filters(best_match, problem_description) if best_match else {}
    all_troyer_pass = all(troyer_filters.values()) if troyer_filters else False
    structure_class = classify_electronic_structure(problem_description)

    best_speedup = best_match.get("speedup_class", "unknown") if best_match else "unknown"
    best_verdict = best_match.get("troyer_verdict", "INCONCLUSIVE") if best_match else "INCONCLUSIVE"
    best_name = best_match.get("name", "Unknown") if best_match else "Unknown"

    # Search always returns its top-k, relevant or not, and the zoo is almost
    # entirely strong-speedup quantum algorithms. So "there is a top match" is
    # not evidence of anything. Require the problem itself to read as quantum
    # before a KB match is allowed to carry a QUANTUM_ADVANTAGE verdict.
    #
    # Without this gate a portfolio-optimisation question retrieved
    # "Probabilistic Sampling (Quantum Supremacy)" and was published as
    # QUANTUM_ADVANTAGE at 0.9 confidence.
    quantum_corroborated = (
        quantum_score > 0 and quantum_score >= ai_score and quantum_score >= hpc_score
    )

    # Build evidence
    evidence = {
        "keyword_scores": {"quantum": round(quantum_score, 4), "hpc": round(hpc_score, 4), "ai_ml": round(ai_score, 4)},
        "kb_match": {"name": best_name, "speedup": best_speedup, "verdict": best_verdict, "search_score": round(search_score, 4)} if best_match else None,
        "troyer_filters": troyer_filters,
        "all_troyer_pass": all_troyer_pass,
        "quantum_corroborated": quantum_corroborated,
        "electronic_structure_class": structure_class,
    }

    # === DECISION MATRIX ===

    # Rule 0: a single-reference structure is already answered by coupled cluster.
    # Per arXiv:2409.08910 the quantum case rests on there being no small set of
    # important determinants, so an explicitly class-1 problem does not get a
    # quantum verdict no matter how strong the retrieved match is.
    if structure_class == "class_1":
        return {
            "platform": "HPC",
            "verdict": "HPC_PREFERRED",
            "confidence": 0.75,
            "reason": (
                "The problem describes a single-reference, weakly correlated structure. "
                "Classical coupled cluster already resolves this class, so there is no "
                "quantum advantage to claim (F6, arXiv:2409.08910)."
            ),
            "evidence": evidence,
        }

    # Rule 1: Strong quantum advantage from KB, corroborated by the problem text.
    # Trust EITHER all computed Troyer filters OR the curated troyer_verdict.
    # Structural-advantage algorithms (e.g. Shor factoring) are QUANTUM_ADVANTAGE
    # despite F4_naturally_quantum being false, so the curated verdict is
    # authoritative for strong-speedup problems.
    if (
        quantum_corroborated
        and best_speedup in STRONG_QUANTUM_SPEEDUPS
        and (all_troyer_pass or best_verdict == "QUANTUM_ADVANTAGE")
    ):
        reason = (
            f"KB match '{best_name}' has {best_speedup} speedup and passes all Troyer filters"
            if all_troyer_pass
            else f"KB match '{best_name}' has {best_speedup} speedup and a curated QUANTUM_ADVANTAGE verdict"
        )
        return {
            "platform": "QUANTUM",
            "verdict": "QUANTUM_ADVANTAGE",
            "confidence": 0.9,
            "reason": reason,
            "evidence": evidence,
        }

    # Rule 2: AI/ML domain dominates (no strong quantum match)
    if ai_score > quantum_score and ai_score > hpc_score and ai_score > 0.02:
        return {
            "platform": "AI_ML",
            "verdict": "AI_ML_PREFERRED",
            "confidence": 0.8,
            "reason": "Problem domain keywords strongly match AI/ML patterns (classification, prediction, NLP, etc.)",
            "evidence": evidence,
        }

    # Rule 3: HPC domain dominates
    if hpc_score > quantum_score and hpc_score > ai_score and hpc_score > 0.02:
        return {
            "platform": "HPC",
            "verdict": "HPC_PREFERRED",
            "confidence": 0.8,
            "reason": "Problem domain keywords match classical compute patterns (simulation, numerical methods, classical optimisation)",
            "evidence": evidence,
        }

    # Rule 4: KB match exists but weak/dequantized advantage
    if best_match and best_speedup in NO_QUANTUM_ADVANTAGE:
        return {
            "platform": "HPC",
            "verdict": "HPC_PREFERRED",
            "confidence": 0.7,
            "reason": f"Best quantum algorithm '{best_name}' has {best_speedup} speedup  no proven quantum advantage",
            "evidence": evidence,
        }

    # Rule 5: KB match with weak advantage (quadratic)  Troyer filters fail
    if best_match and best_speedup in WEAK_QUANTUM_SPEEDUPS and not all_troyer_pass:
        failed = [k for k, v in troyer_filters.items() if not v]
        return {
            "platform": "HPC",
            "verdict": "HPC_PREFERRED",
            "confidence": 0.7,
            "reason": f"Best quantum algorithm '{best_name}' has only {best_speedup} speedup; Troyer filters fail: {', '.join(failed)}",
            "evidence": evidence,
        }

    # Rule 6: Quantum keywords dominate but no strong KB match
    if quantum_score > ai_score and quantum_score > hpc_score and quantum_score > 0.02:
        if best_match and best_speedup in STRONG_QUANTUM_SPEEDUPS:
            # Strong speedup but some Troyer filters fail
            failed = [k for k, v in troyer_filters.items() if not v]
            return {
                "platform": "QUANTUM",
                "verdict": "INCONCLUSIVE",
                "confidence": 0.6,
                "reason": f"KB match '{best_name}' has {best_speedup} speedup but Troyer filters partially fail: {', '.join(failed)}",
                "evidence": evidence,
            }
        return {
            "platform": "QUANTUM",
            "verdict": "INCONCLUSIVE",
            "confidence": 0.5,
            "reason": "Problem has quantum domain keywords but no strong KB algorithm match",
            "evidence": evidence,
        }

    # Default: no rule fired.
    if best_match and best_speedup in STRONG_QUANTUM_SPEEDUPS and not quantum_corroborated:
        # Say why we did not take the KB match, rather than implying there wasn't one.
        return {
            "platform": "INCONCLUSIVE",
            "verdict": "INCONCLUSIVE",
            "confidence": 0.4,
            "reason": (
                f"Nearest KB algorithm '{best_name}' has {best_speedup} speedup, but nothing in the "
                f"problem description indicates a quantum workload, so the match is treated as a "
                f"retrieval artefact rather than evidence"
            ),
            "evidence": evidence,
        }

    return {
        "platform": "INCONCLUSIVE",
        "verdict": "INCONCLUSIVE",
        "confidence": 0.4,
        "reason": "No clear platform signal from KB or domain analysis  LLM will assess",
        "evidence": evidence,
    }
