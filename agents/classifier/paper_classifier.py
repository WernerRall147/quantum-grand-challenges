"""Classify a paper's claimed speedup from its title and abstract.

The Troyer filters read speedup_class, io_bottleneck and naturally_quantum. Papers carry
none of those, which is why 2,239 indexed abstracts could not become better verdicts.
This closes part of that gap, deliberately conservatively.

Three design choices, each forced by something measured:

INDETERMINATE is the default, not a fallback. The labelled set drawn from the Quantum
Algorithm Zoo is 239 STRONG against 119 WEAK, so a classifier that always answers STRONG
scores 67% accuracy while being wrong about every paper that matters. Accuracy is the
wrong target; the over-claim rate - WEAK papers called STRONG - is the one that decides
whether this may ever touch a verdict.

Conflicting evidence abstains rather than picking a side. A paper that says both
"exponential speedup" and "quadratic" is usually contrasting a regime, and guessing which
one the authors meant is how an over-claim gets made.

Nothing here sets a verdict. route_platform() owns that and does not call this.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

STRONG = "STRONG"
WEAK = "WEAK"
INDETERMINATE = "INDETERMINATE"

# Phrases that assert a speedup surviving error correction.
STRONG_PHRASES = [
    "exponential speedup", "exponentially faster", "superpolynomial speedup",
    "super-polynomial speedup", "exponential advantage", "exponential improvement",
    "exponential separation", "exponentially better", "exponential quantum advantage",
]

# Phrases that mark a speedup as quadratic or smaller, or as refuted. Troyer's F3 is the
# reason these matter: a quadratic win does not survive error-correction overhead.
WEAK_PHRASES = [
    "quadratic speedup", "quadratic advantage", "quadratic improvement",
    "square-root speedup", "square root speedup", "grover speedup",
    "polynomial speedup", "constant-factor", "constant factor speedup",
    "no quantum speedup", "no quantum advantage", "dequantiz",
    "classically simulable", "classical algorithm matches", "quantum-inspired classical",
]


@dataclass
class PaperClassification:
    speedup_class: str
    evidence: list[str] = field(default_factory=list)
    conflict: bool = False

    @property
    def is_decided(self) -> bool:
        return self.speedup_class in (STRONG, WEAK)


def _hits(text: str, phrases: list[str]) -> list[str]:
    return [p for p in phrases if p in text]


def classify_paper(title: str, abstract: str = "") -> PaperClassification:
    """Return the speedup class the paper claims, or INDETERMINATE.

    Abstains on silence and on conflict. Both are common and both are correct answers.
    """
    text = re.sub(r"\s+", " ", f"{title} {abstract}").lower()

    strong = _hits(text, STRONG_PHRASES)
    weak = _hits(text, WEAK_PHRASES)

    if strong and weak:
        return PaperClassification(INDETERMINATE, sorted(strong + weak), conflict=True)
    if strong:
        return PaperClassification(STRONG, sorted(strong))
    if weak:
        return PaperClassification(WEAK, sorted(weak))
    return PaperClassification(INDETERMINATE, [])
