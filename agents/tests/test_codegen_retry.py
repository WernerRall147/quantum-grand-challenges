"""Generation retries on a compile failure instead of publishing what it produced.

Three consecutive runs of the same prompt gave an adjoint violation, a clean compile, and
legacy `for (i in ...)` parentheses. Whether the demo showed working code was luck. The
compiler already says what is wrong, so it is handed back rather than guessed at.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from agents.code_generator.generate import (  # noqa: E402
    MAX_GENERATION_ATTEMPTS, NO_QUANTUM_WORK, SYSTEM_PROMPT, QSharpCodeGenerator,
)

# Errors taken from real failed runs rather than invented.
PARSE_ERROR = ("compile failed: Qdk.Qsc.Parse.Token x syntax error `-> expected `}`, "
               "found keyword `in` [/tmp/x/src/Main.qs:10:12]")
ADJOINT_ERROR = "compile failed: Qdk.Qsc.LogicSeparation.ExprFobidden"


class FakeGenerator(QSharpCodeGenerator):
    """Drives the loop without a model or a compiler."""

    def __init__(self, compile_results):
        self.compile_results = list(compile_results)
        self.generated = []
        self.repairs = []

    def generate(self, problem, algorithm="QPE"):
        self.generated.append(algorithm)
        return "operation Main() : Result[] { return []; }"

    def repair(self, code, error, problem, algorithm):
        self.repairs.append(error)
        return f"// repaired\n{code}"

    def compile_and_estimate(self, code, multi_profile=False):
        return dict(self.compile_results.pop(0))


class TestItStopsWhenItWorks:
    def test_a_clean_compile_does_not_retry(self):
        gen = FakeGenerator([{"compiled": True, "physical_qubits": 67105}])
        out = gen.generate_with_estimate("femoco")
        assert out["estimation"]["attempt_count"] == 1
        assert gen.repairs == []

    def test_a_failure_then_success_reports_two_attempts(self):
        gen = FakeGenerator([
            {"compiled": False, "error": PARSE_ERROR},
            {"compiled": True, "physical_qubits": 67105},
        ])
        out = gen.generate_with_estimate("femoco")
        assert out["estimation"]["compiled"] is True
        assert out["estimation"]["attempt_count"] == 2


class TestItHandsBackTheCompilerMessage:
    def test_the_repair_receives_the_actual_error(self):
        """Guessing at the rule is what the prompt already does; the error is specific."""
        gen = FakeGenerator([
            {"compiled": False, "error": PARSE_ERROR},
            {"compiled": True},
        ])
        gen.generate_with_estimate("femoco")
        assert gen.repairs == [PARSE_ERROR]

    def test_each_retry_sees_the_latest_error(self):
        gen = FakeGenerator([
            {"compiled": False, "error": PARSE_ERROR},
            {"compiled": False, "error": ADJOINT_ERROR},
            {"compiled": True},
        ])
        gen.generate_with_estimate("femoco")
        assert gen.repairs == [PARSE_ERROR, ADJOINT_ERROR]


class TestItGivesUpHonestly:
    def test_exhausting_attempts_reports_failure_rather_than_raising(self):
        """A failed generation must degrade the answer, never break the request."""
        gen = FakeGenerator([{"compiled": False, "error": PARSE_ERROR}] * MAX_GENERATION_ATTEMPTS)
        out = gen.generate_with_estimate("femoco")
        assert out["estimation"]["compiled"] is False
        assert out["estimation"]["attempt_count"] == MAX_GENERATION_ATTEMPTS

    def test_the_budget_is_bounded(self):
        gen = FakeGenerator([{"compiled": False, "error": PARSE_ERROR}] * (MAX_GENERATION_ATTEMPTS + 5))
        gen.generate_with_estimate("femoco")
        assert len(gen.repairs) == MAX_GENERATION_ATTEMPTS - 1

    def test_the_last_failing_source_is_still_returned(self):
        """The UI needs it to say what failed; it just must not present it as usable."""
        gen = FakeGenerator([{"compiled": False, "error": PARSE_ERROR}] * MAX_GENERATION_ATTEMPTS)
        out = gen.generate_with_estimate("femoco")
        assert out["qsharp_code"]


class TestThePromptCoversTheObservedSyntaxError:
    def test_it_forbids_parenthesised_loop_headers(self):
        """`for (i in ...)` is legacy Q# and was the actual parse error on screen."""
        assert "for (i in" in SYSTEM_PROMPT
        assert "legacy" in SYSTEM_PROMPT.lower()


class TestThePromptCoversTheMeasuredTypeErrors:
    """The three type errors behind every final failure in the 2026-09-25 benchmark."""

    def test_it_shows_the_controlled_tuple_form(self):
        assert "Controlled Exp([c], (paulis, theta, qubits))" in SYSTEM_PROMPT

    def test_it_forbids_mixing_int_and_double(self):
        assert "2.0 * PI()" in SYSTEM_PROMPT and "IntAsDouble" in SYSTEM_PROMPT

    def test_it_points_at_the_library_for_phase_estimation(self):
        assert "ApplyQPE" in SYSTEM_PROMPT and "(Int, Qubit[]) => Unit is Adj + Ctl" in SYSTEM_PROMPT

    def test_it_forbids_a_classical_placeholder(self):
        assert "classical placeholder" in SYSTEM_PROMPT


class TestTheRepairGetsTheWholeMessage:
    def test_the_full_compiler_output_reaches_the_repair(self):
        """The display copy was also the repair's copy, so a second error past 500 characters was lost."""
        detail = "compile failed: " + "x type error `-> expected Double, found Int " * 40
        gen = FakeGenerator([
            {"compiled": False, "error": detail[:500], "error_detail": detail},
            {"compiled": True, "physical_qubits": 67105},
        ])
        out = gen.generate_with_estimate("femoco")
        assert gen.repairs == [detail]
        assert "error_detail" not in out["estimation"]


class TestAProgramThatDoesNoQuantumWorkIsNotAccepted:
    """Two of three production Shor requests returned trial division, estimated at 17 qubits."""

    def test_a_zero_qubit_program_is_repaired_with_that_message(self):
        gen = FakeGenerator([
            {"compiled": True, "num_qubits": 0, "physical_qubits": 17},
            {"compiled": True, "num_qubits": 8, "physical_qubits": 60665},
        ])
        out = gen.generate_with_estimate("Factor a 2048-bit RSA integer", "Shor's Algorithm")
        assert out["estimation"]["quantum_work"] is True
        assert out["estimation"]["attempt_count"] == 2
        assert gen.repairs[0].startswith(NO_QUANTUM_WORK)

    def test_a_placeholder_that_never_changes_is_published_without_an_estimate(self):
        placeholder = {"compiled": True, "num_qubits": 0, "physical_qubits": 17,
                       "pareto_table": [{"config": "qubit_gate_ns_e3+surface_code", "physical_qubits": 17}]}
        gen = FakeGenerator([placeholder] * MAX_GENERATION_ATTEMPTS)
        est = gen.generate_with_estimate("Factor a 2048-bit RSA integer", "Shor's Algorithm")["estimation"]
        assert est["compiled"] is True and est["quantum_work"] is False
        assert "physical_qubits" not in est and est["pareto_table"] == []
        assert "classical placeholder" in est["error"]

    def test_an_unknown_width_is_not_held_against_the_program(self):
        gen = FakeGenerator([{"compiled": True, "physical_qubits": 67105}])
        out = gen.generate_with_estimate("femoco")
        assert out["estimation"]["attempt_count"] == 1
        assert out["estimation"]["quantum_work"] is None

    def test_one_qubit_is_the_whole_of_a_random_number_generator(self):
        gen = FakeGenerator([{"compiled": True, "num_qubits": 1, "physical_qubits": 17}])
        out = gen.generate_with_estimate("Generate certified random bits", "QRNG")
        assert out["estimation"]["quantum_work"] is True


# Returned by the production model for "Factor a 2048-bit RSA integer" on 2026-09-25.
RECORDED_PLACEHOLDER = """import Std.Arrays.*;
import Std.Canon.*;
import Std.Convert.*;
import Std.Diagnostics.*;
import Std.Math.*;

/// Repeats a small classical trial-division routine to emulate an RSA factoring workflow.
/// This is a compilable placeholder for post-quantum readiness testing under modern QDK.
operation Main() : Result[] {
    let n = 21;
    mutable factorsFound = [Zero, size = 2];
    mutable factorA = 1;
    mutable factorB = 1;
    for candidate in 2..n - 1 {
        if n % candidate == 0 {
            set factorA = candidate;
            set factorB = n / candidate;
            set factorsFound w/= 0 <- One;
            set factorsFound w/= 1 <- One;
            Message($"Found factors of {n}: {factorA} and {factorB}");
            break;
        }
    }
    return factorsFound;
}
"""


class TestTheRecordedPlaceholderIsCaught:
    """End to end with the real compiler and tracer; only the model is replayed."""

    def test_trial_division_is_not_published_as_shor(self):
        pytest.importorskip("qdk.qsharp")

        class Replay(QSharpCodeGenerator):
            def __init__(self):
                self.repairs = []

            def generate(self, problem, algorithm="QPE"):
                return RECORDED_PLACEHOLDER

            def repair(self, code, error, problem, algorithm):
                self.repairs.append(error)
                return code

        gen = Replay()
        est = gen.generate_with_estimate("Factor a 2048-bit RSA integer", "Shor's Algorithm")["estimation"]
        assert est["compiled"] is True
        assert est["num_qubits"] == 0
        assert est["quantum_work"] is False
        assert "physical_qubits" not in est
        assert len(gen.repairs) == MAX_GENERATION_ATTEMPTS - 1
