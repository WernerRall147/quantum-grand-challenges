"""Generation retries on a compile failure instead of publishing what it produced.

Three consecutive runs of the same prompt gave an adjoint violation, a clean compile, and
legacy `for (i in ...)` parentheses. Whether the demo showed working code was luck. The
compiler already says what is wrong, so it is handed back rather than guessed at.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from agents.code_generator.generate import (  # noqa: E402
    MAX_GENERATION_ATTEMPTS, SYSTEM_PROMPT, QSharpCodeGenerator,
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
