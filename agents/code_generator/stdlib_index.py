"""Check generated Q# against the names the standard library actually exports.

The compiler tells the model *where* it went wrong, never *what to write instead*:

    x syntax error
    `-> expected `{`, found `[`

That is why `repair()` could not fix `new Result[n]` across three attempts, and why the
prompt in #233 had to name the replacement by hand. A banlist works, but it grows one
entry per production incident.

The library states its own API. `libs/qdk_stdlib/exports.json` is every exported name at
the pinned tag, so an unknown callable can be caught and a real alternative suggested,
generically, without anyone having to be burned by it first.

This is advisory. A false positive would send a repair chasing a name that is fine, which
is worse than no check, so the checks are deliberately conservative and
tests/test_stdlib_index.py measures the false-positive rate against every Q# file in this
repo that is known to compile.
"""

from __future__ import annotations

import difflib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "libs" / "qdk_stdlib" / "exports.json"

# A call site: an identifier immediately followed by `(`. The lookbehind drops attributes
# such as `@EntryPoint()` and `@Test()`, which are not calls into anything.
_CALL = re.compile(r"(?<![@\w])([A-Za-z_][A-Za-z0-9_]*)\s*\(")

# Doc comments are prose, and prose contains words followed by brackets. Left in, the
# checker reports `Copyright`, `EntryPoint` and `QDK` as missing stdlib functions.
_COMMENT = re.compile(r"//[^\n]*")

# So do message strings: `Message($"Classical: O(2^n)")` and "Monte Carlo (MC)" were
# reported as calls to O and Carlo.
_STRING = re.compile(r'\$?"(?:[^"\\\n]|\\.)*"')

# Declarations in the same file, which are obviously in scope.
_DECLARED = re.compile(
    r"\b(?:function|operation|newtype|struct)\s+([A-Za-z_][A-Za-z0-9_]*)", re.M
)

# Callables also arrive as parameters and local bindings - `f`, `Uf`, `phaseOracle` in the
# upstream samples - and calling one of those is not a call into the standard library.
_TYPED = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*:")
_BOUND = re.compile(r"\b(?:let|mutable|use|borrow)\s+\(?([A-Za-z_][A-Za-z0-9_,\s]*?)\)?\s*=")

# `for (state, initializer, basis) in tuples` binds three names, one of which is called.
_FOR = re.compile(r"\bfor\s+\(?([A-Za-z_][A-Za-z0-9_,\s]*?)\)?\s+in\b")

# Keywords and types that can appear before `(` and are not callables.
_NOT_CALLABLES = frozenset({
    "if", "elif", "else", "for", "while", "repeat", "until", "fixup", "return", "fail",
    "use", "borrow", "within", "apply", "let", "set", "mutable", "new", "not", "and",
    "or", "in", "import", "export", "internal", "function", "operation", "newtype",
    "struct", "namespace", "body", "adjoint", "controlled", "Adjoint", "Controlled",
    "Int", "BigInt", "Double", "Bool", "String", "Unit", "Result", "Qubit", "Pauli",
    "Range", "One", "Zero", "PauliI", "PauliX", "PauliY", "PauliZ", "true", "false",
})


@lru_cache(maxsize=1)
def exported_names() -> frozenset[str]:
    if not INDEX.exists():
        return frozenset()
    return frozenset(json.loads(INDEX.read_text(encoding="utf-8"))["all"])


@lru_cache(maxsize=1)
def index_tag() -> str:
    if not INDEX.exists():
        return ""
    return json.loads(INDEX.read_text(encoding="utf-8"))["tag"]


def in_scope(code: str) -> set[str]:
    """Everything the file itself introduces: declarations, parameters, local bindings."""
    names = set(_DECLARED.findall(code)) | set(_TYPED.findall(code))
    for binding in _BOUND.findall(code) + _FOR.findall(code):
        names.update(part.strip() for part in binding.split(",") if part.strip().isidentifier())
    return names


def unknown_names(code: str) -> list[str]:
    """Called names that the file does not define and the standard library does not export.

    Returns [] when the index is missing rather than flagging everything: an absent index
    must degrade to the old behaviour, not to a prompt full of phantom errors.
    """
    known = exported_names()
    if not known:
        return []
    source = _STRING.sub('""', _COMMENT.sub("", code))
    declared = in_scope(source)
    unknown = {
        name for name in _CALL.findall(source)
        if name not in known and name not in declared and name not in _NOT_CALLABLES
    }
    return sorted(unknown)


def suggest(name: str, limit: int = 3) -> list[str]:
    """Closest real names, so a repair can be told what to write instead."""
    return difflib.get_close_matches(name, exported_names(), n=limit, cutoff=0.6)


def diagnose(code: str) -> str:
    """A hint naming the replacement, or "" when nothing is wrong."""
    lines = []
    for name in unknown_names(code):
        matches = suggest(name)
        if matches:
            lines.append(f"- `{name}` does not exist. Closest real names: {', '.join(matches)}.")
        else:
            lines.append(f"- `{name}` does not exist in the Q# standard library.")
    if not lines:
        return ""
    return (
        "These names are not in the Q# standard library at "
        f"{index_tag()} and are not defined in the program:\n" + "\n".join(lines)
    )
