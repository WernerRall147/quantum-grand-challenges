"""The uptime probe's documented cadence must match the workflow, and its real behaviour.

Two different claims got confused, and the confusion survived for weeks.

`.github/workflows/uptime-evaluator-api.yml` sets `cron: "*/30 * * * *"`, so the workflow
*asks* to run every 30 minutes. GitHub throttles scheduled workflows on public
repositories and silently drops most of them: the observed cadence on 18 Sep 2026 was 43
runs in seven days, about one every four hours, against the 336 a literal reading implies.

The runbook said the probe "has run every 30 minutes since 2026-08-14 with no failures".
The second half was true - 43 runs, 0 failures - and the first half was wrong by roughly
eight times. That matters because it is the answer to a judge asking how we know the demo
is up, and "every 30 minutes" is a claim about evidence we do not have.

What is checked here:

- The cron expression the docs attribute to the workflow is the one the workflow has.
  Offline and exact, so changing the schedule without updating the prose fails.
- No live document claims the probe *runs* on that cadence. Saying the cron asks for it is
  accurate; saying it happens is not, and that is the sentence that was wrong.

The observed cadence itself is deliberately not asserted here. It needs the GitHub API, it
moves with GitHub's scheduling load, and a test that needs the network to decide is a test
people learn to skip. The docs state it as a dated measurement instead.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "uptime-evaluator-api.yml"

# Records of a moment, not claims about now. Mirrors tooling/test_doc_claims.py.
ARCHIVAL = (
    "docs/Hackathon2026/",
    "docs/AI_Expanations/",
    "docs/planning/",
    "docs/MILESTONE_",
    "docs/QAE_PROJECT_COMPLETION",
)
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "out", ".next", "problems"}

_CRON = re.compile(r'cron:\s*"([^"]+)"')

# "runs every 30 minutes", "has run every 30 minutes", "running every 30 minutes".
# Deliberately does not match "asks for every 30 minutes" or "every 30 minutes; GitHub
# throttles", which describe the schedule rather than the observed behaviour.
_CADENCE_CLAIM = re.compile(
    r"\b(?:runs?|ran|running|has\s+run)\s+(?:this\s+)?every\s+30\s+minutes", re.IGNORECASE
)


def _live_docs() -> list[Path]:
    return [
        path
        for path in REPO_ROOT.rglob("*.md")
        if not _SKIP_DIRS.intersection(path.parts)
        and not any(
            path.relative_to(REPO_ROOT).as_posix().startswith(prefix) for prefix in ARCHIVAL
        )
    ]


def test_the_workflow_still_declares_a_cron():
    """Guard the guard: no cron would make the comparison below vacuous."""
    assert WORKFLOW.exists(), f"missing {WORKFLOW}"
    assert _CRON.search(WORKFLOW.read_text(encoding="utf-8")), (
        f"no cron expression found in {WORKFLOW.name}; the checks below would pass "
        f"without checking anything."
    )


def test_docs_attribute_the_right_cron_to_the_probe():
    """If the schedule changes, the prose describing it has to change too."""
    cron = _CRON.search(WORKFLOW.read_text(encoding="utf-8")).group(1)
    assert cron == "*/30 * * * *", (
        f"the uptime probe's cron is now {cron!r}. The runbook describes it as asking for "
        f"every 30 minutes - update docs/AzureFriday/README.md and this test together."
    )


def test_no_live_doc_claims_the_probe_actually_runs_every_30_minutes():
    """The claim that was wrong for weeks, made checkable.

    GitHub drops most scheduled runs on public repos. Stating the cron is fine; stating
    that the probe runs on it is a claim about evidence the run history contradicts.
    """
    offenders = []
    for path in _live_docs():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if _CADENCE_CLAIM.search(line):
                offenders.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{lineno}")

    assert not offenders, (
        "these lines claim the uptime probe runs every 30 minutes: "
        + ", ".join(offenders)
        + ". The cron asks for that; GitHub throttles scheduled workflows on public repos "
        "and the observed cadence is roughly one run every four hours. Describe the cron, "
        "or state the measured cadence with its date."
    )
