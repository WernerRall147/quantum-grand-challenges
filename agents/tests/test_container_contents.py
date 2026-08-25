"""The image must contain the files the API reads at runtime, not just the ones it imports.

Q# generation was dead in production and nothing said so. generate.py puts /app/tooling on
sys.path and imports estimator_config from it; the Dockerfile copied agents/, knowledge/ and
a single JSON. The import raised ModuleNotFoundError, /api/evaluate caught it and set
qsharp_code to "", and the website renders that field only when truthy - so a broken feature
looked exactly like one nobody had asked for. The API answered 200 the whole time.

These read the real Dockerfile and the real path constants, so adding a reference
implementation without copying it fails here rather than degrading the prompt in silence.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

DOCKERFILE = REPO / "Dockerfile"


def copied_paths() -> list[str]:
    """Source paths the Dockerfile copies into the image."""
    paths = []
    for line in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^COPY\s+(?!--)(\S+)\s+(\S+)", line.strip())
        if match:
            paths.append(match.group(1))
    return paths


def is_in_image(relative: str, copied: list[str]) -> bool:
    """True when a repo-relative path is covered by a COPY, directly or via its directory."""
    target = relative.replace("\\", "/")
    for source in copied:
        source = source.rstrip("/")
        if target == source or target.startswith(source + "/"):
            return True
    return False


class TestTheImageHasWhatTheApiNeeds:
    def test_estimator_config_is_copied(self):
        """The exact import that was failing in production."""
        assert is_in_image("tooling/estimator_config.py", copied_paths()), (
            "generate.py imports estimator_config from /app/tooling. Without it, Q# "
            "generation raises and the API returns an empty string instead of code."
        )

    def test_every_reference_implementation_is_copied(self):
        from agents.code_generator.generate import REFERENCE_IMPLEMENTATIONS

        copied = copied_paths()
        missing = [rel for rel in REFERENCE_IMPLEMENTATIONS.values()
                   if not is_in_image(rel, copied)]
        assert missing == [], (
            "generate.py feeds these to the model as exemplars and falls back to an empty "
            f"snippet when they are absent, so the loss is invisible: {missing}"
        )

    def test_the_reference_implementations_exist_in_the_repo(self):
        """A COPY of a path that does not exist fails the build rather than the request."""
        from agents.code_generator.generate import REFERENCE_IMPLEMENTATIONS

        missing = [rel for rel in REFERENCE_IMPLEMENTATIONS.values()
                   if not (REPO / rel).exists()]
        assert missing == [], f"referenced but not in the repo: {missing}"

    def test_the_api_package_is_copied(self):
        assert is_in_image("agents/api/main.py", copied_paths())


class TestTheCoverageCheckItself:
    """A matcher that always returns True would make the tests above meaningless."""

    def test_a_directory_copy_covers_files_beneath_it(self):
        assert is_in_image("agents/api/main.py", ["agents/"])

    def test_an_uncopied_path_is_not_covered(self):
        assert not is_in_image("tooling/estimator_config.py", ["agents/", "knowledge/"])

    def test_a_prefix_that_is_not_a_directory_boundary_does_not_match(self):
        """"tooling_extra/x.py" must not be satisfied by a COPY of "tooling"."""
        assert not is_in_image("tooling_extra/x.py", ["tooling"])
