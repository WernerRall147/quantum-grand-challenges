"""The assessment contract, in one place.

The output format was described in three places that could drift apart: prose in
SYSTEM_PROMPT, REQUIRED_KEYS in the narrative scorer, and the model's own habits.
That is how F6 came to be demanded by the output format while the prompt still
enumerated five filters. This module is the machine-readable copy: the agent path
enforces it as a structured output, and the scorer derives its key list from it.

Strict JSON-schema mode requires every property to appear in `required` and
`additionalProperties` to be false, so optional-looking fields are mandatory and
come back empty rather than absent.
"""

from __future__ import annotations

VERDICTS = ["QUANTUM_ADVANTAGE", "HPC_PREFERRED", "AI_ML_PREFERRED", "INCONCLUSIVE"]
PLATFORMS = ["QUANTUM", "AI_ML", "HPC", "HYBRID"]
ADVANTAGE_CLASSES = ["exponential", "superpolynomial", "quadratic", "none"]
DIVINCENZO_VALUES = ["met", "partial", "not_yet"]

FILTER_KEYS = [
    "F1_proven_speedup",
    "F2_io_survives",
    "F3_qec_survives",
    "F4_naturally_quantum",
    "F5_crossover_feasible",
    "F6_state_preparation",
]

DIVINCENZO_KEYS = [
    "scalable_qubits",
    "initialization",
    "coherence",
    "universal_gates",
    "measurement",
]


def _obj(properties: dict) -> dict:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _strings() -> dict:
    return {"type": "array", "items": {"type": "string"}}


ASSESSMENT_SCHEMA = _obj({
    "verdict": {"type": "string", "enum": VERDICTS},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "advantage_class": {"type": "string", "enum": ADVANTAGE_CLASSES},
    "recommended_algorithm": {"type": "string"},
    "recommended_platform": {"type": "string", "enum": PLATFORMS},
    "platform_reason": {"type": "string"},
    "workspace_guidance": _obj({
        "platform": {"type": "string"},
        "setup_steps": _strings(),
        "recommended_resources": {"type": "string"},
    }),
    "troyer_filters": _obj({k: {"type": "boolean"} for k in FILTER_KEYS}),
    "divincenzo_assessment": _obj({
        **{k: {"type": "string", "enum": DIVINCENZO_VALUES} for k in DIVINCENZO_KEYS},
        "summary": {"type": "string"},
    }),
    "red_flags": _strings(),
    "hpc_alternative": {"type": "string"},
    "ai_alternative": {"type": "string"},
    "explanation": {"type": "string"},
    "similar_problems": _strings(),
    "references": _strings(),
    "error_correction_codes": _strings(),
})

REQUIRED_KEYS = list(ASSESSMENT_SCHEMA["properties"])

RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "quantum_advantage_assessment",
    "schema": ASSESSMENT_SCHEMA,
    "strict": True,
}
