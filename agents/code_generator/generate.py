"""Q# Code Generator Agent.

Pipeline:
1. Take a quantum problem description + recommended algorithm (from orchestrator)
2. Look up the closest reference implementation from problems/
3. Ask GPT-5.4-mini to generate a Q# operation tailored to the problem
4. Validate by compiling via the qsharp Python package
5. Run QRE v3 resource estimation for resource requirements

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
sys.path.insert(0, str(ROOT / "tooling"))

from estimator_config import (  # noqa: E402  must follow sys.path setup
    DEFAULT_QEC_SCHEME,
    DEFAULT_QUBIT_MODEL,
    QUBIT_MODELS,
    estimate_summary,
    iter_model_configs,
)

OPENAI_ENDPOINT = os.environ.get("QGC_OPENAI_ENDPOINT", "https://qgc-openai.openai.azure.com/")
CHAT_DEPLOYMENT = os.environ.get("QGC_CHAT_DEPLOYMENT", "gpt-54-mini")
ROUTER_ENDPOINT = os.environ.get("QGC_ROUTER_ENDPOINT", "https://admin-mo1q7owo-eastus2.cognitiveservices.azure.com/")
ROUTER_DEPLOYMENT = os.environ.get("QGC_ROUTER_DEPLOYMENT", "model-router")
# The router picks a different model per request, and gpt-5.6-sol spends the entire
# budget reasoning and returns no content: measured empty on 2 of 4 production calls
# 2026-08-31. Raising the budget to 12000 only moved the failure to a gateway timeout,
# so generation is pinned to one deployment. The verdict path still uses the router;
# set QGC_CODEGEN_USE_ROUTER=1 to opt generation back in.
USE_ROUTER = os.environ.get("QGC_CODEGEN_USE_ROUTER", "0") == "1"

# CHAT_DEPLOYMENT is the verdict path's model. Pointing generation at it produced Q# that
# never compiled: the deployment named gpt-54-mini serves gpt-4.1-mini from April 2025,
# which writes `import Std.Math::*` and imports without semicolons however plainly the
# system prompt states otherwise. Three retries, three parse errors, no estimate.
# gpt-53-codex is not the answer either - codex serves the Responses API and returns
# 400 to chat.completions. qgc-codegen is gpt-5.4-mini, measured compiling.
CODEGEN_DEPLOYMENT = os.environ.get("QGC_CODEGEN_DEPLOYMENT", "qgc-codegen")

# Must cover the model's reasoning tokens as well as the Q# it emits. evaluate.py hit
# this first: the router picks reasoning models, 1000 was consumed by thinking alone, and
# the answer came back empty. This path kept 1500 and failed the same way, silently.
MAX_COMPLETION_TOKENS = int(os.environ.get("QGC_CODEGEN_MAX_TOKENS", "4000"))

# Generation is not reliable enough to trust once. Three consecutive runs of the same
# prompt gave an adjoint violation, a clean compile, and legacy for-loop parentheses.
MAX_GENERATION_ATTEMPTS = int(os.environ.get("QGC_CODEGEN_ATTEMPTS", "3"))

# Map orchestrator-recommended algorithms to reference implementations
REFERENCE_IMPLEMENTATIONS = {
    "QPE": "problems/01_hubbard/qsharp/src/Main.qs",
    "Shor": "problems/09_factorization/qsharp/src/Main.qs",
    "Trotter": "problems/19_quantum_chromodynamics/qsharp/src/Main.qs",
    "Quantum Walk": "problems/18_photovoltaics/qsharp/src/Main.qs",
    "QEC": "problems/16_error_correction/qsharp/src/Main.qs",
    # Vendored from microsoft/qdk v1.31.0 by tooling/vendor_qdk_samples.py, which keeps
    # only samples that compile against the pinned compiler and define Main.
    "VQE": "libs/qdk_samples/SimpleVQE.qs",
    "Grover": "libs/qdk_samples/Grover.qs",
    "Bernstein-Vazirani": "libs/qdk_samples/BernsteinVazirani.qs",
    "Deutsch-Jozsa": "libs/qdk_samples/DeutschJozsa.qs",
    "Hidden Shift": "libs/qdk_samples/HiddenShift.qs",
    "Phase Estimation": "libs/qdk_samples/PhaseEstimation.qs",
    "Teleportation": "libs/qdk_samples/Teleportation.qs",
    "QRNG": "libs/qdk_samples/QRNG.qs",
    "Repetition Code": "libs/qdk_samples/ThreeQubitRepetitionCode.qs",
    "Superdense Coding": "libs/qdk_samples/SuperdenseCoding.qs",
}

# QAOA, HHL and anything else unmapped used to get no example at all - the model was left
# to recall modern Q# syntax unaided for exactly those requests.
DEFAULT_REFERENCE = "problems/01_hubbard/qsharp/src/Main.qs"

SYSTEM_PROMPT = """You are a Q# code generator for the modern Azure Quantum Development Kit (QDK 1.27+).

Generate a single self-contained Q# operation that implements the requested algorithm for the user's problem.

CRITICAL RULES:
- Use modern Q# syntax (qsharp.json project format, NOT the legacy .NET namespace style)
- Start with `import Std.Arrays.*; import Std.Canon.*; import Std.Convert.*; import Std.Diagnostics.*; import Std.Math.*;`
- Do NOT emit `namespace ... { ... }` blocks  modern QDK is flat
- Loops and conditionals take NO parentheses around the header. Write
  `for i in 0..Length(xs) - 1 {` and `if x > 0 {`, never `for (i in ...)` or `if (x > 0)`.
  The parenthesised form is legacy Q# and is a parse error in modern QDK.
- Build arrays with `[value, size = n]`, or `Repeated(value, n)` from Std.Arrays. Write
  `mutable rs = [Zero, size = n];`, never `mutable rs = new Result[n];`. `new T[n]` and
  `ConstantArray` were removed from the language: `new` is a parse error and
  `ConstantArray` does not resolve. Grow an array with `set xs += [x];`.
- The entry point MUST be `operation Main() : Result[]` - exactly that name, and no
  parameters. Resource estimation invokes `Main()` by name; any other name or any
  parameter list makes the program unestimatable.
- Put every other operation behind `Main`, called from it
- Keep the implementation compilable (valid types, use `mutable` for variables reassigned in loops, `set` for reassignment)
- An operation that is `is Adj`, `is Adj + Ctl`, or ever used via `Adjoint`/`Controlled`
  must contain NO `set` assignment, `while`, `repeat`, or `return`. Q# generates the
  adjoint by inverting the body and cannot invert those. Compute such values in a
  `function`, or before the adjointable operation, and pass them in as parameters.
- Target a modest qubit count (4-12 qubits) so resource estimation runs quickly
- Include brief /// doc comments explaining each operation

OUTPUT: Return ONLY the Q# source code. No markdown fences, no explanations. Just compilable Q# starting with the `import` statements.
"""

# Operations the estimator can be pointed at: a name, then a parameter list we require to
# be empty. Estimation invokes the entry by expression, so an operation taking arguments
# cannot be one however well it is named.
_OPERATION = re.compile(r"^\s*operation\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*\)", re.M)


def entry_expression(code: str, module: str = "Main") -> str:
    """Return the call expression to estimate, preferring Main, qualified by module.

    Two things had to be measured to get this right. The prompt asks for an operation
    named Main and the estimator assumed it, until the model named it after the problem
    instead and every Pareto row read `Qdk.Qsc.Resolve.NotFound ... 'Main' not found`.
    Reading the name out of the source fixed that and produced the identical error, because
    the name alone is not enough: src/Main.qs defines a module, so the callable is
    Main.Main. Checked directly against generated source - `Main()` does not resolve,
    `Main.Main()` returns 67,105 physical qubits. The repo's own Q# tests already used the
    qualified form.
    """
    names = _OPERATION.findall(code)
    chosen = "Main" if (not names or "Main" in names) else names[0]
    return f"{module}.{chosen}()"


class QSharpCodeGenerator:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.last_model_used: str | None = None
    def _client(self) -> AzureOpenAI:
        token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        endpoint = ROUTER_ENDPOINT if USE_ROUTER else OPENAI_ENDPOINT
        return AzureOpenAI(
            azure_ad_token=token.token,
            azure_endpoint=endpoint,
            api_version="2024-10-21",
        )

    def _deployment(self) -> str:
        return ROUTER_DEPLOYMENT if USE_ROUTER else CODEGEN_DEPLOYMENT

    def _load_reference(self, algorithm: str) -> str:
        """Return a short reference snippet for the algorithm, falling back to a known-good one."""
        rel = REFERENCE_IMPLEMENTATIONS.get(algorithm, DEFAULT_REFERENCE)
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

REFERENCE IMPLEMENTATION (for style only  adapt to the problem):
{reference if reference else '(no reference available  generate from scratch)'}

Generate a compilable Q# `Main` operation implementing {algorithm} for this problem."""

        client = self._client()
        resp = client.chat.completions.create(
            model=self._deployment(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_completion_tokens=MAX_COMPLETION_TOKENS,
        )
        choice = resp.choices[0]
        self.last_model_used = getattr(resp, "model", None)
        code = choice.message.content or ""
        if not code.strip():
            # `or ""` used to hide this, and the API turns an empty string into a page
            # with no code block on it. Say what happened instead: the router picks
            # reasoning models whose thinking counts against the same budget, so an
            # exhausted budget returns a valid response carrying nothing.
            usage = getattr(resp, "usage", None)
            raise RuntimeError(
                f"model returned no content (finish_reason={choice.finish_reason}, "
                f"model={getattr(resp, 'model', '?')}, "
                f"max_completion_tokens={MAX_COMPLETION_TOKENS}, usage={usage})"
            )
        return self._strip_fences(code)

    # Pareto sweep matrix is sourced from tooling/estimator_config.QUBIT_MODELS
    # so the agent, the multimodel estimator, and the calibration tooling stay
    # aligned on which (qubit, QEC) combinations get evaluated.
    PARETO_MODELS = QUBIT_MODELS

    # Snake_case output schema kept stable for downstream UI / telemetry
    # consumers. estimator_config.extract_summary returns camelCase keys, so
    # this adapter renames them on the way out.
    _SUMMARY_KEY_MAP = {
        "physicalQubits": "physical_qubits",
        "runtime": "runtime_ns",
        "logicalQubits": "logical_qubits",
        "logicalDepth": "logical_depth",
        "tCount": "t_count",
        "rotationCount": "rotation_count",
        "tFactoryFraction": "t_factory_fraction",
        "codeDistance": "code_distance",
    }

    @classmethod
    def _extract_estimate(cls, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Rename a QRE v3 summary to the snake_case UI schema."""
        return {snake: summary.get(camel_k) for camel_k, snake in cls._SUMMARY_KEY_MAP.items()}

    def compile_and_estimate(self, code: str, multi_profile: bool = False) -> Dict[str, Any]:
        """Compile generated Q# via qdk and run QRE v3 resource estimation.

        When ``multi_profile`` is True, also sweeps the qubit profiles × QEC
        schemes and returns ``pareto_table`` for comparison rendering.
        """
        try:
            from qdk import qsharp  # type: ignore
        except ImportError:
            return {"compiled": False, "error": "qdk package not installed"}

        with tempfile.TemporaryDirectory() as td:
            proj = Path(td)
            (proj / "qsharp.json").write_text(json.dumps({"author": "qgc", "license": "AGPL-3.0"}))
            src_dir = proj / "src"
            src_dir.mkdir()
            (src_dir / "Main.qs").write_text(code, encoding="utf-8")

            # Derived before init so a compile failure still reports what would have run.
            entry = entry_expression(code)

            try:
                qsharp.init(project_root=str(proj))
            except Exception as e:  # noqa: BLE001  surface compile failures to the UI
                return {"compiled": False, "entry_expression": entry,
                        "error": f"compile failed: {str(e)[:500]}"}

            result: Dict[str, Any] = {"compiled": True}
            result["entry_expression"] = entry

            # Default-profile estimate (kept at top level for backwards compat).
            try:
                summary = self._extract_estimate(
                    estimate_summary(entry, DEFAULT_QUBIT_MODEL, DEFAULT_QEC_SCHEME)
                )
                result.update({
                    "physical_qubits": summary.get("physical_qubits"),
                    "runtime_ns": summary.get("runtime_ns"),
                    "logical_depth": summary.get("logical_depth"),
                })
            except Exception as e:  # noqa: BLE001
                result["estimate_error"] = str(e)[:500]

            if multi_profile:
                result["pareto_table"] = self._run_pareto_sweep(entry)

            return result

    def _run_pareto_sweep(self, entry: str = "Main.Main()") -> list:
        """Evaluate every (qubit, QEC) combination in QUBIT_MODELS.

        QRE v3 explores code distances and factories internally, so each
        combination is its own call and per-config errors stay diagnosable.
        """
        triples = list(iter_model_configs(self.PARETO_MODELS))

        def _annotate(summary: Dict[str, Any], model: Any, qec: str, key: str) -> Dict[str, Any]:
            summary = dict(summary)
            summary.update({
                "config": key,
                "qubit_tech": model.name,
                "qubit_label": model.label,
                "qec_scheme": qec,
                "family": model.family,
            })
            return summary

        pareto: list = []
        for model, qec, key in triples:
            try:
                summary = self._extract_estimate(estimate_summary(entry, model.name, qec))
                pareto.append(_annotate(summary, model, qec, key))
            except Exception as e:  # noqa: BLE001  skip incompatible combos
                pareto.append({
                    "config": key,
                    "qubit_tech": model.name,
                    "qubit_label": model.label,
                    "qec_scheme": qec,
                    "family": model.family,
                    "error": str(e)[:200],
                })
        return pareto

    def generate_with_estimate(
        self,
        problem: str,
        algorithm: str = "QPE",
        multi_profile: bool = False,
    ) -> Dict[str, Any]:
        """Generate, compile, and retry with the compiler's own message on failure.

        One shot at generation was never going to be enough. Three consecutive runs of the
        same prompt produced an adjoint violation, a clean compile, and legacy `for (i in
        ...)` parentheses - so whether the demo showed working code came down to luck. The
        compiler already says precisely what is wrong; handing that back is far more
        effective than another rule in the prompt, and the rules do not have to anticipate
        every mistake.

        Returns compiled=False after the last attempt rather than raising. Callers must not
        present code that did not compile, which is what the UI was doing.
        """
        attempts: list[dict] = []
        code = ""
        est: Dict[str, Any] = {}

        for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
            if attempt == 1:
                code = self.generate(problem, algorithm)
            else:
                code = self.repair(code, est.get("error", ""), problem, algorithm)

            est = self.compile_and_estimate(code, multi_profile=multi_profile)
            attempts.append({"attempt": attempt, "compiled": bool(est.get("compiled")),
                             "error": (est.get("error") or "")[:300]})
            if est.get("compiled"):
                break

        est["attempts"] = attempts
        est["attempt_count"] = len(attempts)
        # Which model wrote this. Three different models produced three different failures
        # on 2026-08-31 - empty output, uncompilable imports, and a 400 - and none of the
        # responses said which one had been used, so every diagnosis started from scratch.
        est["codegen_deployment"] = ROUTER_DEPLOYMENT if USE_ROUTER else CODEGEN_DEPLOYMENT
        est["codegen_model"] = getattr(self, "last_model_used", None)
        return {"qsharp_code": code, "estimation": est, "algorithm": algorithm}

    def repair(self, code: str, error: str, problem: str, algorithm: str) -> str:
        """Ask for a fix using the compiler's message, rather than guessing at the rule."""
        user_msg = f"""This Q# failed to compile. Fix it and return the corrected program.

COMPILER ERROR:
{error[:1500]}

PROGRAM:
{code}

Return ONLY the corrected Q#. Keep the same algorithm ({algorithm}) and the same problem
({problem[:200]}). The entry point must still be `operation Main() : Result[]` with no
parameters."""

        resp = self._client().chat.completions.create(
            model=self._deployment(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_completion_tokens=MAX_COMPLETION_TOKENS,
        )
        fixed = (resp.choices[0].message.content or "").strip()
        # A repair that returns nothing must not blank the code; keep the last attempt so
        # the reported error stays the real one.
        return self._strip_fences(fixed) if fixed else code



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
