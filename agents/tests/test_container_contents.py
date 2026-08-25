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
DOCKERIGNORE = REPO / ".dockerignore"


def copied_paths() -> list[str]:
    """Source paths the Dockerfile copies into the image."""
    paths = []
    for line in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^COPY\s+(?!--)(\S+)\s+(\S+)", line.strip())
        if match:
            paths.append(match.group(1))
    return paths


def dockerignore_rules() -> list[str]:
    return [line.strip() for line in DOCKERIGNORE.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")]


def in_build_context(relative: str, rules: list[str]) -> bool:
    """True when .dockerignore lets a path reach the build context.

    Only models the whitelist form this repo uses - a bare `*` excluding everything,
    then `!` rules re-including named paths. That is enough to catch the failure this
    was written for: a COPY of a path nothing re-includes.
    """
    target = relative.replace("\\", "/")
    if "*" not in rules:
        return True
    for rule in rules:
        if not rule.startswith("!"):
            continue
        allowed = rule[1:].rstrip("/")
        if allowed.endswith("/**"):
            allowed = allowed[:-3]
        if target == allowed or target.startswith(allowed + "/"):
            return True
    return False


def is_in_image(relative: str, copied: list[str]) -> bool:
    """True when a repo-relative path is covered by a COPY, directly or via its directory."""
    target = relative.replace("\\", "/")
    for source in copied:
        source = source.rstrip("/")
        if target == source or target.startswith(source + "/"):
            return True
    return False


def reaches_the_image(relative: str) -> bool:
    """Both gates. A COPY of a path .dockerignore drops fails the build, not the request."""
    return (is_in_image(relative, copied_paths())
            and in_build_context(relative, dockerignore_rules()))


class TestTheImageHasWhatTheApiNeeds:
    def test_estimator_config_is_copied(self):
        """The exact import that was failing in production."""
        assert reaches_the_image("tooling/estimator_config.py"), (
            "generate.py imports estimator_config from /app/tooling. Without it, Q# "
            "generation raises and the API returns an empty string instead of code."
        )

    def test_every_reference_implementation_is_copied(self):
        from agents.code_generator.generate import REFERENCE_IMPLEMENTATIONS

        missing = [rel for rel in REFERENCE_IMPLEMENTATIONS.values()
                   if not reaches_the_image(rel)]
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

    def test_every_copied_path_survives_dockerignore(self):
        """The hole that let PR #204 fail. Checking the Dockerfile alone is not enough.

        .dockerignore is a whitelist here, so adding a COPY without a matching `!` rule
        builds green locally and dies in ACR with "file not found in build context".
        """
        rules = dockerignore_rules()
        dropped = [src for src in copied_paths()
                   if src != "Dockerfile" and not in_build_context(src.rstrip("/"), rules)]
        assert dropped == [], (
            f"COPY targets excluded by .dockerignore, so the image build will fail: {dropped}"
        )

    def test_the_api_package_is_copied(self):
        assert reaches_the_image("agents/api/main.py")


class TestExtrasTheImportsNeed:
    """Shipping a file is not enough if its dependencies were never installed.

    Fixing the missing COPY only moved the error along: estimator_config imported, then
    `No module named 'pandas'`. qdk declares `pandas>=2.1 ; extra == 'qre'`, and
    requirements.txt pinned bare `qdk==1.31.0`. Derived from the import rather than
    hardcoded, so dropping the extra fails with the reason attached.
    """

    def test_qre_extra_is_requested_when_the_code_imports_qdk_qre(self):
        requirements = (REPO / "agents" / "api" / "requirements.txt").read_text(encoding="utf-8")

        # Only what ships. A test or a scratch file mentioning qdk.qre says nothing about
        # what the container needs, and this test matches its own source otherwise.
        pattern = re.compile(r"^\s*(from|import)\s+qdk\.qre", re.M)
        importers = [
            path.relative_to(REPO).as_posix()
            for path in (list((REPO / "agents").rglob("*.py")) + list((REPO / "tooling").rglob("*.py")))
            if "tests" not in path.parts
            and reaches_the_image(path.relative_to(REPO).as_posix())
            and pattern.search(path.read_text(encoding="utf-8", errors="ignore"))
        ]
        if not importers:
            return

        assert re.search(r"^qdk\[[^\]]*\bqre\b[^\]]*\]", requirements, re.M), (
            f"these ship in the image and import qdk.qre, which needs the [qre] extra "
            f"for pandas: {importers}"
        )



class TestTheCoverageCheckItself:
    """A matcher that always returns True would make the tests above meaningless."""

    def test_a_directory_copy_covers_files_beneath_it(self):
        assert is_in_image("agents/api/main.py", ["agents/"])

    def test_an_uncopied_path_is_not_covered(self):
        assert not is_in_image("tooling/estimator_config.py", ["agents/", "knowledge/"])

    def test_a_prefix_that_is_not_a_directory_boundary_does_not_match(self):
        """"tooling_extra/x.py" must not be satisfied by a COPY of "tooling"."""
        assert not is_in_image("tooling_extra/x.py", ["tooling"])

    def test_the_whitelist_reader_drops_what_nothing_reincludes(self):
        rules = ["*", "!agents/", "!agents/**"]
        assert in_build_context("agents/api/main.py", rules)
        assert not in_build_context("tooling/estimator_config.py", rules)

    def test_without_a_bare_star_nothing_is_excluded(self):
        assert in_build_context("tooling/estimator_config.py", ["node_modules/"])

