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

    def compile_and_estimate(self, code: str) -> Dict[str, Any]:
        """Compile generated Q# via qsharp package and run resource estimation."""
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
            try:
                est = qsharp.estimate("Main()")
                # qsharp returns an EstimatorResult with .data or dict-like output
                if hasattr(est, "data"):
                    data = est.data()
                else:
                    data = est
                phys = data.get("physicalCounts", {}) if isinstance(data, dict) else {}
                result["physical_qubits"] = phys.get("physicalQubits")
                result["runtime_ns"] = phys.get("runtime")
                result["logical_depth"] = phys.get("breakdown", {}).get("logicalDepth")
            except Exception as e:  # noqa: BLE001
                result["estimate_error"] = str(e)[:500]

            return result

    def generate_with_estimate(self, problem: str, algorithm: str = "QPE") -> Dict[str, Any]:
        """Full pipeline: generate + compile + estimate."""
        code = self.generate(problem, algorithm)
        est = self.compile_and_estimate(code)
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
