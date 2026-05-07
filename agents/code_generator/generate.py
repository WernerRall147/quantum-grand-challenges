"""Q# Code Generator Agent.

Pipeline:
1. Take a quantum problem description + recommended algorithm (from orchestrator)
2. Look up the closest reference implementation from problems/
3. Ask GPT-5.4-mini to generate a Q# operation tailored to the problem
4. Validate by compiling via the qsharp Python package
5. Run qsharp.estimate() for resource requirements

This produces the "🔧 Q# code" output advertised in README.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

OPENAI_ENDPOINT = os.environ.get("QGC_OPENAI_ENDPOINT", "https://qgc-openai.openai.azure.com/")
CHAT_DEPLOYMENT = os.environ.get("QGC_CHAT_DEPLOYMENT", "gpt-54-mini")
ROUTER_ENDPOINT = os.environ.get("QGC_ROUTER_ENDPOINT", "https://admin-mo1q7owo-eastus2.cognitiveservices.azure.com/")
ROUTER_DEPLOYMENT = os.environ.get("QGC_ROUTER_DEPLOYMENT", "model-router")
USE_ROUTER = os.environ.get("QGC_USE_ROUTER", "0") == "1"

# Map orchestrator-recommended algorithms to reference implementations
REFERENCE_IMPLEMENTATIONS = {
    "QPE": "problems/01_hubbard/qsharp/src/Main.qs",
    "Shor": "problems/09_factorization/qsharp/src/Main.qs",
    "Trotter": "problems/19_quantum_chromodynamics/qsharp/src/Main.qs",
    "Quantum Walk": "problems/18_photovoltaics/qsharp/src/Main.qs",
    "QEC": "problems/16_error_correction/qsharp/src/Main.qs",
}

SYSTEM_PROMPT = """You are a Q# code generator for the modern Azure Quantum Development Kit (QDK 1.27+).

Generate a single self-contained Q# operation that implements the requested algorithm for the user's problem.

CRITICAL RULES:
- Use modern Q# syntax (qsharp.json project format, NOT the legacy .NET namespace style)
- Start with `import Std.Arrays.*; import Std.Canon.*; import Std.Convert.*; import Std.Diagnostics.*; import Std.Math.*;`
- Do NOT emit `namespace ... { ... }` blocks — modern QDK is flat
- Define an `operation Main() : Result[]` or similar as the entry point
- Keep the implementation compilable (valid types, use `mutable` for variables reassigned in loops, `set` for reassignment)
- Target a modest qubit count (4-12 qubits) so resource estimation runs quickly
- Include brief /// doc comments explaining each operation

OUTPUT: Return ONLY the Q# source code. No markdown fences, no explanations. Just compilable Q# starting with the `import` statements.
"""


class QSharpCodeGenerator:
    def __init__(self):
        self.credential = DefaultAzureCredential()

    def _client(self) -> AzureOpenAI:
        token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        endpoint = ROUTER_ENDPOINT if USE_ROUTER else OPENAI_ENDPOINT
        return AzureOpenAI(
            azure_ad_token=token.token,
            azure_endpoint=endpoint,
            api_version="2024-10-21",
        )

    def _deployment(self) -> str:
        return ROUTER_DEPLOYMENT if USE_ROUTER else CHAT_DEPLOYMENT

    def _load_reference(self, algorithm: str) -> str:
        """Return a short reference snippet for the algorithm, or empty string."""
        rel = REFERENCE_IMPLEMENTATIONS.get(algorithm)
        if not rel:
            return ""
        path = ROOT / rel
        if not path.exists():
            return ""
        text = path.read_text(encoding="utf-8", errors="replace")
        # Keep it short to avoid blowing the prompt budget
        return text[:3500]

    @staticmethod
    def _strip_fences(code: str) -> str:
        """Remove markdown code fences if the model adds them despite instructions."""
        m = re.search(r"```(?:qsharp|q#)?\s*(.+?)```", code, flags=re.DOTALL)
        if m:
            return m.group(1).strip()
        return code.strip()

    def generate(self, problem: str, algorithm: str = "QPE") -> str:
        """Generate Q# source code for the given problem + algorithm."""
        reference = self._load_reference(algorithm)
        user_msg = f"""PROBLEM: {problem}

RECOMMENDED ALGORITHM: {algorithm}

REFERENCE IMPLEMENTATION (for style only — adapt to the problem):
{reference if reference else '(no reference available — generate from scratch)'}

Generate a compilable Q# `Main` operation implementing {algorithm} for this problem."""

        client = self._client()
        resp = client.chat.completions.create(
            model=self._deployment(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_completion_tokens=1500,
        )
        code = resp.choices[0].message.content or ""
        return self._strip_fences(code)

    # Pareto sweep: 6 qubit profiles × applicable QEC schemes (10 total runs).
    PARETO_PROFILES: tuple = (
        {"name": "qubit_gate_ns_e3", "label": "Superconducting (ns, 1e-3)", "qec": ("surface_code",), "family": "gate_based"},
        {"name": "qubit_gate_ns_e4", "label": "Superconducting (ns, 1e-4)", "qec": ("surface_code",), "family": "gate_based"},
        {"name": "qubit_gate_us_e3", "label": "Trapped Ion (μs, 1e-3)", "qec": ("surface_code",), "family": "gate_based"},
        {"name": "qubit_gate_us_e4", "label": "Trapped Ion (μs, 1e-4)", "qec": ("surface_code",), "family": "gate_based"},
        {"name": "qubit_maj_ns_e4", "label": "Majorana (ns, 1e-4)", "qec": ("surface_code", "floquet_code"), "family": "majorana"},
        {"name": "qubit_maj_ns_e6", "label": "Majorana (ns, 1e-6)", "qec": ("surface_code", "floquet_code"), "family": "majorana"},
    )

    @staticmethod
    def _extract_estimate(data: Any) -> Dict[str, Any]:
        """Pull the headline metrics from a qsharp.estimate() result."""
        if not isinstance(data, dict):
            return {}
        phys = data.get("physicalCounts", {})
        logical = data.get("logicalCounts", {})
        breakdown = phys.get("breakdown", {})
        runtime_ns = phys.get("runtime")
        physical_qubits = phys.get("physicalQubits")
        physical_t_factory_qubits = breakdown.get("physicalQubitsForTfactories")
        t_factory_fraction = None
        if physical_qubits and physical_t_factory_qubits:
            try:
                t_factory_fraction = round(physical_t_factory_qubits / physical_qubits, 3)
            except (ZeroDivisionError, TypeError):
                t_factory_fraction = None
        return {
            "physical_qubits": physical_qubits,
            "runtime_ns": runtime_ns,
            "logical_qubits": breakdown.get("algorithmicLogicalQubits"),
            "logical_depth": logical.get("logicalDepth"),
            "t_count": logical.get("tCount"),
            "rotation_count": logical.get("rotationCount"),
            "t_factory_fraction": t_factory_fraction,
            "code_distance": (
                breakdown.get("logicalPatch", {}).get("codeDistance")
                if isinstance(breakdown.get("logicalPatch"), dict)
                else None
            ),
        }

    def compile_and_estimate(self, code: str, multi_profile: bool = False) -> Dict[str, Any]:
        """Compile generated Q# via qsharp package and run resource estimation.

        When ``multi_profile`` is True, also sweeps 6 qubit profiles × QEC schemes
        and returns ``pareto_table`` for comparison rendering.
        """
        try:
            import qsharp  # type: ignore
        except ImportError:
            return {"compiled": False, "error": "qsharp package not installed"}

        with tempfile.TemporaryDirectory() as td:
            proj = Path(td)
            (proj / "qsharp.json").write_text(json.dumps({"author": "qgc", "license": "AGPL-3.0"}))
            src_dir = proj / "src"
            src_dir.mkdir()
            (src_dir / "Main.qs").write_text(code, encoding="utf-8")

            try:
                qsharp.init(project_root=str(proj))
            except Exception as e:  # noqa: BLE001 — surface compile failures to the UI
                return {"compiled": False, "error": f"compile failed: {str(e)[:500]}"}

            result: Dict[str, Any] = {"compiled": True}

            # Default-profile estimate (kept at top level for backwards compat).
            try:
                est = qsharp.estimate("Main()")
                data = est.data() if hasattr(est, "data") else est
                summary = self._extract_estimate(data)
                result.update({
                    "physical_qubits": summary.get("physical_qubits"),
                    "runtime_ns": summary.get("runtime_ns"),
                    "logical_depth": summary.get("logical_depth"),
                })
            except Exception as e:  # noqa: BLE001
                result["estimate_error"] = str(e)[:500]

            if multi_profile:
                pareto: list = []
                for profile in self.PARETO_PROFILES:
                    for qec in profile["qec"]:
                        config_key = f"{profile['name']}+{qec}"
                        try:
                            est = qsharp.estimate(
                                "Main()",
                                params={
                                    "qubitParams": {"name": profile["name"]},
                                    "qecScheme": {"name": qec},
                                },
                            )
                            data = est.data() if hasattr(est, "data") else est
                            summary = self._extract_estimate(data)
                            summary.update({
                                "config": config_key,
                                "qubit_tech": profile["name"],
                                "qubit_label": profile["label"],
                                "qec_scheme": qec,
                                "family": profile["family"],
                            })
                            pareto.append(summary)
                        except Exception as e:  # noqa: BLE001 — skip incompatible combos
                            pareto.append({
                                "config": config_key,
                                "qubit_tech": profile["name"],
                                "qubit_label": profile["label"],
                                "qec_scheme": qec,
                                "family": profile["family"],
                                "error": str(e)[:200],
                            })
                result["pareto_table"] = pareto

            return result

    def generate_with_estimate(
        self,
        problem: str,
        algorithm: str = "QPE",
        multi_profile: bool = False,
    ) -> Dict[str, Any]:
        """Full pipeline: generate + compile + estimate (optionally multi-profile)."""
        code = self.generate(problem, algorithm)
        est = self.compile_and_estimate(code, multi_profile=multi_profile)
        return {"qsharp_code": code, "estimation": est, "algorithm": algorithm}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: generate.py <problem description> [algorithm]")
        sys.exit(1)
    problem = sys.argv[1]
    algorithm = sys.argv[2] if len(sys.argv) > 2 else "QPE"

    gen = QSharpCodeGenerator()
    out = gen.generate_with_estimate(problem, algorithm)
    print("=== Q# Code ===")
    print(out["qsharp_code"])
    print("\n=== Estimation ===")
    print(json.dumps(out["estimation"], indent=2))


if __name__ == "__main__":
    main()
