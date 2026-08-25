"""Which operation the resource estimator should be pointed at.

Estimation invokes an entry by expression and both call sites hardcoded `Main()`. The
prompt asked for Main but said "or similar", so the model named the operation after the
problem instead and every row of the Pareto sweep rendered
`Qdk.Qsc.Resolve.NotFound ... 'Main' not found` on screen, in the beat that exists to show
resource estimates.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from agents.code_generator.generate import SYSTEM_PROMPT, entry_expression  # noqa: E402


class TestPickingTheEntry:
    def test_main_is_preferred_when_present(self):
        code = """import Std.Arrays.*;
        operation PrepareState() : Unit { }
        operation Main() : Result[] { return []; }
        """
        assert entry_expression(code) == "Main()"

    def test_main_wins_even_when_declared_last(self):
        """Order must not decide it; a helper declared first is still a helper."""
        code = """operation Helper() : Unit { }
        operation Another() : Unit { }
        operation Main() : Result[] { return []; }
        """
        assert entry_expression(code) == "Main()"

    def test_the_observed_failure_now_resolves(self):
        """What the model actually emitted: named for the problem, no Main anywhere."""
        code = """import Std.Arrays.*;
        /// Estimate the FeMoco ground state energy.
        operation EstimateFeMocoGroundState() : Result[] { return []; }
        """
        assert entry_expression(code) == "EstimateFeMocoGroundState()"

    def test_an_operation_taking_arguments_is_not_an_entry(self):
        """`Op()` would not compile against `operation Op(n : Int)`, so it is not a candidate."""
        code = """operation WithArgs(n : Int) : Unit { }
        operation NoArgs() : Result[] { return []; }
        """
        assert entry_expression(code) == "NoArgs()"

    def test_whitespace_between_name_and_parens_is_tolerated(self):
        assert entry_expression("operation Spaced () : Unit { }") == "Spaced()"

    def test_nothing_callable_falls_back_rather_than_raising(self):
        """A degraded estimate beats no code at all; the estimator reports the real reason."""
        assert entry_expression("import Std.Arrays.*;") == "Main()"
        assert entry_expression("operation OnlyWithArgs(q : Qubit) : Unit { }") == "Main()"


class TestThePromptStoppedLicensingIt:
    def test_the_prompt_no_longer_says_or_similar(self):
        """"or similar" is what permitted the drift; the requirement is now exact."""
        assert "or similar" not in SYSTEM_PROMPT

    def test_the_prompt_states_the_reason(self):
        """A rule with a reason attached survives future edits better than a bare rule."""
        assert "Main()" in SYSTEM_PROMPT
        assert "estimation" in SYSTEM_PROMPT.lower()
