"""Index every name the Q# standard library actually exports, at the pinned tag.

The banlist in generate.py grows one entry per production incident: `new T[n]` and
`ConstantArray` are there because they each cost a day. That list encodes what we have
seen, not what is true.

The library states what is true. Every Std file ends with an `export` list, which is a
machine-readable allowlist of its public API. This reads those lists so a generated
program can be checked against the real surface before it is ever compiled, and so a
repair can name the replacement rather than only the location - which is the thing the
compiler's own message cannot do:

    x syntax error
    `-> expected `{`, found `[`

    python tooling/vendor_qdk_stdlib_index.py
    python tooling/vendor_qdk_stdlib_index.py --check   # verify, write nothing
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from importlib import metadata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEST = REPO / "libs" / "qdk_stdlib"
INDEX = DEST / "exports.json"

TAG = "v1.31.0"
RAW = "https://raw.githubusercontent.com/microsoft/qdk/{tag}/{path}"
CONTENTS = "https://api.github.com/repos/microsoft/qdk/contents/{dir}?ref={tag}"

# Std is the documented surface. Core holds Length, Repeated and the other names that
# resolve without any import, so omitting it flags them as unknown - which is worse than
# no check at all, because it sends a repair chasing a name that is fine.
SOURCE_DIRS = ("library/std/src/Std", "library/core")

# `export A, B, C;` and `export A as B;`. Non-greedy to the first semicolon: exports are
# statements, and a greedy match would swallow the rest of the file.
_EXPORT = re.compile(r"^\s*export\s+(.*?);", re.M | re.S)
_ALIAS = re.compile(r"\bas\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")

# Fallback for files with no export statement: top-level declarations are public there.
_DECL = re.compile(
    r"^\s*(?:internal\s+)?(?:function|operation|newtype|struct)\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)
_INTERNAL = re.compile(r"^\s*internal\s+", re.M)


def fetch(path: str) -> str:
    with urllib.request.urlopen(RAW.format(tag=TAG, path=path), timeout=60) as response:
        return response.read().decode("utf-8")


def list_qs_files(directory: str) -> list[str]:
    url = CONTENTS.format(dir=directory, tag=TAG)
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            entries = json.load(response)
    except urllib.error.HTTPError as exc:
        print(f"  SKIP {directory}: HTTP {exc.code}")
        return []
    return sorted(f"{directory}/{e['name']}" for e in entries
                  if e["type"] == "file" and e["name"].endswith(".qs"))


def exported_names(source: str) -> set[str]:
    """Names a file makes public: its export list, or its declarations if it has none."""
    names: set[str] = set()
    for block in _EXPORT.findall(source):
        for item in block.split(","):
            item = item.strip()
            if not item:
                continue
            alias = _ALIAS.search(item)
            # `Std.Arrays.Mapped as Map` publishes Map; a bare path publishes its last segment.
            names.add(alias.group(1) if alias else item.split(".")[-1].strip())
    if not names:
        for line in source.splitlines():
            if _INTERNAL.match(line):
                continue
            match = _DECL.match(line)
            if match:
                names.add(match.group(1))
    return {n for n in names if n.isidentifier()}


def build() -> dict[str, list[str]]:
    modules: dict[str, list[str]] = {}
    for directory in SOURCE_DIRS:
        for path in list_qs_files(directory):
            stem = Path(path).stem
            if stem.endswith("TestUtils") or "Internal" in stem:
                continue
            names = exported_names(fetch(path))
            if names:
                modules[stem] = sorted(names)
                print(f"  {stem:<20} {len(names):>4} names")
    return modules


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    version = metadata.version("qsharp")
    if TAG != f"v{version}":
        print(f"FAIL: pinned to {TAG} but qsharp {version} is installed.")
        return 1

    modules = build()
    flat = sorted({name for names in modules.values() for name in names})
    payload = {"tag": TAG, "qsharp_version": version, "modules": modules, "all": flat}

    if args.check:
        if not INDEX.exists():
            print("FAIL: no index; run without --check")
            return 1
        current = json.loads(INDEX.read_text(encoding="utf-8"))
        if current.get("all") != flat:
            added = sorted(set(flat) - set(current.get("all", [])))
            removed = sorted(set(current.get("all", [])) - set(flat))
            print(f"FAIL: index drifted from {TAG}. added={added[:8]} removed={removed[:8]}")
            return 1
        print(f"\nOK: {len(flat)} names match {TAG}")
        return 0

    DEST.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\n{len(flat)} names across {len(modules)} modules -> {INDEX.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
