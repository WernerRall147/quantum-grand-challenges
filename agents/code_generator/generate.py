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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, Optional

from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

from agents.code_generator.compiler_hints import hints_for
from agents.code_generator.stdlib_index import diagnose
from agents.observability.trace import span

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tooling"))

from estimator_config import (  # noqa: E402  must follow sys.path setup
    DEFAULT_QEC_SCHEME,
    DEFAULT_QUBIT_MODEL,
    QUBIT_MODELS,
    _logical_counts,
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
    # Written for the generator: complete programs in the shape it must return, each checked
    # against exact results by agents/tests/test_codegen_exemplars.py. The problem files
    # these replaced were cut mid-statement by the character budget, and the one used for
    # QPE opened with 3,500 characters of VQE code.
    "QPE": "agents/code_generator/exemplars/QPE.qs",
    "Shor": "agents/code_generator/exemplars/Shor.qs",
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
DEFAULT_REFERENCE_KEY = "QPE"
DEFAULT_REFERENCE = REFERENCE_IMPLEMENTATIONS[DEFAULT_REFERENCE_KEY]

# Characters of exemplar in the prompt. Every reference fits (the largest, SimpleVQE, is
# 6,995), because the vendored samples define Main first and helpers after it, so a cut
# shows the model calls to helpers it never sees. A longer file is cut between top-level
# declarations, never inside one.
REFERENCE_BUDGET = 7000

# The evaluator passes its recommended_algorithm, which is prose: "Preparing Eigenstates
# and Thermal States, followed by fault-tolerant Quantum Phase Estimation (QPE)". Looked up
# as a dictionary key it never matched, so all 29 production requests between 1 and 25
# September 2026 got the default exemplar, the Shor requests included. The family named
# first in the text wins, because the evaluator names the primary algorithm first and
# mentions alternatives after it ("QPE ...; use VQE only as a state-preparation heuristic").
_REFERENCE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Shor", ("shor", "period finding", "order finding", "integer factoriz", "factoring",
              "discrete log")),
    ("Grover", ("grover", "amplitude amplification", "unstructured search")),
    ("Quantum Walk", ("quantum walk",)),
    ("QPE", ("phase estimation", "qpe", "eigenstate", "ground state", "ground-state",
             "qubitization", "eigenvalue")),
    ("Trotter", ("trotter", "hamiltonian simulation", "time evolution", "real-time dynamics",
                 "lattice gauge", "product formula")),
    ("VQE", ("vqe", "variational")),
    ("Repetition Code", ("repetition code",)),
    ("QEC", ("error correction", "surface code", "qec", "syndrome")),
    ("Bernstein-Vazirani", ("bernstein",)),
    ("Deutsch-Jozsa", ("deutsch",)),
    ("Hidden Shift", ("hidden shift",)),
    ("Teleportation", ("teleport",)),
    ("Superdense Coding", ("superdense",)),
    ("QRNG", ("random number", "qrng")),
)


def resolve_reference(algorithm: str) -> str:
    """The REFERENCE_IMPLEMENTATIONS key for a free-text algorithm name."""
    if algorithm in REFERENCE_IMPLEMENTATIONS:
        return algorithm
    text = (algorithm or "").lower()
    best: tuple[int, int, str] | None = None
    for order, (key, words) in enumerate(_REFERENCE_KEYWORDS):
        positions = [text.find(w) for w in words if w in text]
        if positions and (best is None or (min(positions), order) < best[:2]):
            best = (min(positions), order, key)
    return best[2] if best else DEFAULT_REFERENCE_KEY


# Comments and strings are stripped before braces are counted, because Q# interpolated
# strings hold braces of their own: $"Found {n} factors".
_LINE_COMMENT = re.compile(r"//[^\n]*")
_STRING_LITERAL = re.compile(r'\$?"(?:[^"\\\n]|\\.)*"')


def complete_prefix(source: str, budget: int = REFERENCE_BUDGET) -> str:
    """The longest prefix within `budget` that ends between top-level declarations.

    The old cut was `text[:3500]`, which ended the Hubbard exemplar at `return hopp` and
    the Shor one at `// Initialize work register`: the model was shown unbalanced code as
    the style to follow. A declaration longer than the whole budget is returned whole
    rather than dropped.
    """
    if len(source) <= budget:
        return source
    depth, parens, offset, cut, has_declaration = 0, 0, 0, 0, False
    for line in source.splitlines(keepends=True):
        code = _STRING_LITERAL.sub('""', _LINE_COMMENT.sub("", line)).strip()
        inside = depth > 0 or "{" in code
        depth += code.count("{") - code.count("}")
        parens += code.count("(") - code.count(")")
        offset += len(line)
        # A boundary ends a declaration or statement: `}` or `;` with every bracket closed.
        # That excludes an `@EntryPoint()` line and the lines of a multi-line parameter list.
        if depth == 0 and parens == 0 and code.endswith(("}", ";")):
            if offset > budget and has_declaration:
                break
            cut = offset
            has_declaration = has_declaration or inside
            if offset > budget:
                break
    return source[:cut].rstrip() + "\n"

# Fewer qubits than this cannot run any of the algorithms the evaluator recommends. QRNG is
# the exception: one qubit in superposition is the whole algorithm.
MIN_QUBITS = {"QRNG": 1}
DEFAULT_MIN_QUBITS = 2

NO_QUANTUM_WORK = "The program compiled but uses"


def no_quantum_work(num_qubits: int, algorithm: str) -> str:
    """The feedback for a program that compiles and does no quantum work."""
    return (
        f"{NO_QUANTUM_WORK} {num_qubits} qubit(s), so it does no quantum work: it is a "
        f"classical placeholder, not {algorithm}. Rewrite Main so that it allocates qubits, "
        "applies the algorithm's quantum operations on the smallest instance that still shows "
        "the algorithm, and returns their measurement results."
    )

# The qsharp interpreter is a thread-bound object. Used from another thread it panics
# ("Interpreter is unsendable, but sent to another thread"), and replaced from another
# thread the old one is leaked, not freed. The API serves requests on a thread pool, so
# two generations at once crashed 6 of 6 times in a test, and even one at a time leaked an
# interpreter whenever consecutive requests landed on different threads. Every compile and
# estimate therefore runs on this one thread, which also serialises them.
_QSHARP_THREAD = ThreadPoolExecutor(max_workers=1, thread_name_prefix="qsharp")

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
- The program must do the algorithm's quantum work: allocate qubits and apply its gates.
  Never return a classical placeholder - trial division, a hard-coded answer, or a loop
  that only prints. When the real instance is far too large to simulate (RSA-2048, FeMoco,
  a 2D lattice), implement the same algorithm on the smallest meaningful instance, such as
  order finding for N = 15 or a two- to four-qubit model Hamiltonian, and say so in a doc
  comment.
- Types never convert implicitly. Write Double literals with a decimal point (`2.0 * PI()`,
  never `2 * PI()`) and convert with `IntAsDouble(n)`. BigInt literals end in `L`.
- `Exp(paulis, theta, qubits)` takes a Pauli[], a Double and a Qubit[] of the same length.
  `Controlled` takes the controls, then ONE tuple holding the original arguments:
  `Controlled Exp([c], (paulis, theta, qubits))`, `Controlled R1([c], (theta, q))`.
- Use the library for standard subroutines instead of writing them by hand: `ApplyQPE(oracle,
  target, phase)`, whose oracle has type `(Int, Qubit[]) => Unit is Adj + Ctl` and receives
  the power to apply; `ApplyQFT` and `Adjoint ApplyQFT`; `MResetEachZ` to measure and reset.
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
        self.last_reference: str | None = None

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
        """The exemplar for the algorithm's family, cut only between declarations."""
        key = resolve_reference(algorithm)
        self.last_reference = key
        path = ROOT / REFERENCE_IMPLEMENTATIONS[key]
        if not path.exists():
            return ""
        return complete_prefix(path.read_text(encoding="utf-8", errors="replace"))

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
        "numQubits": "num_qubits",
    }

    @classmethod
    def _extract_estimate(cls, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Rename a QRE v3 summary to the snake_case UI schema."""
        return {snake: summary.get(camel_k) for camel_k, snake in cls._SUMMARY_KEY_MAP.items()}

    def compile_and_estimate(self, code: str, multi_profile: bool = False) -> Dict[str, Any]:
        """Compile generated Q# via qdk and run QRE v3 resource estimation.

        When ``multi_profile`` is True, also sweeps the qubit profiles × QEC
        schemes and returns ``pareto_table`` for comparison rendering. Runs on the
        dedicated qsharp thread whichever thread calls it.
        """
        return _QSHARP_THREAD.submit(self._compile_and_estimate, code, multi_profile).result()

    def _compile_and_estimate(self, code: str, multi_profile: bool) -> Dict[str, Any]:
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
                # The display copy is short; the repair gets the whole message, because a
                # program with several errors lost all but the first at 500 characters.
                return {"compiled": False, "entry_expression": entry,
                        "error": f"compile failed: {str(e)[:500]}",
                        "error_detail": str(e)[:4000]}

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
                    "logical_qubits": summary.get("logical_qubits"),
                    "num_qubits": summary.get("num_qubits"),
                })
            except Exception as e:  # noqa: BLE001
                result["estimate_error"] = str(e)[:500]
            if result.get("num_qubits") is None:
                # The width must be known even when estimation fails, to tell a program
                # that does quantum work from one that does not.
                result["num_qubits"] = _logical_counts(entry).get("numQubits")

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

        Compiling is not enough either. In production two of three Shor requests returned a
        classical trial-division loop that allocated no qubits, and it was estimated at 17
        physical qubits and shown as the implementation. A program narrower than the
        algorithm needs is now treated like a compile failure: repaired with that message,
        and reported with quantum_work=False, and without an estimate, if it never changes.
        """
        attempts: list[dict] = []
        code = ""
        est: Dict[str, Any] = {}
        feedback = ""
        reference = resolve_reference(algorithm)
        min_qubits = MIN_QUBITS.get(reference, DEFAULT_MIN_QUBITS)

        for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
            with span(f"codegen.attempt {attempt}") as _attempt_span:
                if attempt == 1:
                    with span("codegen.generate") as _gen_span:
                        code = self.generate(problem, algorithm)
                        _gen_span.set(chars=len(code or ""), algorithm=algorithm, reference=reference)
                else:
                    with span("codegen.repair", from_error=feedback[:120]) as _rep_span:
                        code = self.repair(code, feedback, problem, algorithm)
                        _rep_span.set(chars=len(code or ""))

                with span("codegen.compile_and_estimate") as _est_span:
                    est = self.compile_and_estimate(code, multi_profile=multi_profile)
                    width = est.get("num_qubits")
                    quantum_work = None if width is None or not est.get("compiled") else width >= min_qubits
                    est["quantum_work"] = quantum_work
                    _est_span.set(
                        compiled=bool(est.get("compiled")),
                        entry_expression=est.get("entry_expression"),
                        physical_qubits=est.get("physical_qubits"),
                        num_qubits=width,
                        quantum_work=quantum_work,
                        pareto_rows=len(est.get("pareto_table") or []),
                        pareto_errors=sum(1 for row in est.get("pareto_table") or [] if row.get("error")),
                    )
                    if est.get("error"):
                        _est_span.set(compile_error=(est.get("error") or "")[:200])
                    if est.get("estimate_error"):
                        _est_span.set(estimate_error=est["estimate_error"][:200])

                if quantum_work is False:
                    feedback = no_quantum_work(width, algorithm)
                else:
                    feedback = est.get("error_detail") or est.get("error") or ""
                attempts.append({"attempt": attempt, "compiled": bool(est.get("compiled")),
                                 "quantum_work": quantum_work,
                                 "error": (est.get("error") or (feedback if quantum_work is False else ""))[:300]})
                _attempt_span.set(compiled=bool(est.get("compiled")), quantum_work=quantum_work)
                if est.get("compiled") and quantum_work is not False:
                    break

        if est.get("quantum_work") is False:
            # An estimate of a placeholder is the cost of nothing; do not publish it.
            est["error"] = feedback
            for key in ("physical_qubits", "runtime_ns", "logical_depth", "logical_qubits"):
                est.pop(key, None)
            est["pareto_table"] = []
        est.pop("error_detail", None)
        est["attempts"] = attempts
        est["attempt_count"] = len(attempts)
        est["reference"] = reference
        # Which model wrote this. Three different models produced three different failures
        # on 2026-08-31 - empty output, uncompilable imports, and a 400 - and none of the
        # responses said which one had been used, so every diagnosis started from scratch.
        est["codegen_deployment"] = ROUTER_DEPLOYMENT if USE_ROUTER else CODEGEN_DEPLOYMENT
        est["codegen_model"] = getattr(self, "last_model_used", None)
        return {"qsharp_code": code, "estimation": est, "algorithm": algorithm}

    def repair(self, code: str, error: str, problem: str, algorithm: str) -> str:
        """Ask for a fix using the compiler's message, plus what the message cannot say.

        A parse error locates the problem without naming the replacement, which is why
        three attempts in a row failed on `new Result[n]`. stdlib_index checks the called
        names against the library's own export list and suggests real ones, compiler_hints
        names the correct form for the type errors that were failing every attempt, and
        the family's exemplar shows the library calls working.
        """
        hint = diagnose(code)
        name_check = f"\nNAME CHECK:\n{hint}\n" if hint else ""
        fixes = hints_for(error)
        fixes = f"\n{fixes}\n" if fixes else ""
        reference = self._load_reference(algorithm)
        if error.startswith(NO_QUANTUM_WORK):
            header, label = "This Q# compiled, but it does no quantum work. Rewrite it.", "PROBLEM"
        else:
            header, label = "This Q# failed to compile. Fix it and return the corrected program.", "COMPILER ERROR"
        user_msg = f"""{header}

{label}:
{error[:3000]}
{fixes}{name_check}
PROGRAM:
{code}

REFERENCE (a complete program that compiles; follow how it calls the library):
{reference if reference else '(none)'}

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
