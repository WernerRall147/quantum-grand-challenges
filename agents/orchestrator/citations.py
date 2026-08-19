"""Resolve citations before they reach a reader.

Measured over 22 cases on both paths: the chat path fabricated a Microsoft Learn
URL, and the agent path - with the Learn MCP attached - fabricated a different
one. Roughly 1 in 22 either way. Having a grounding tool available does not mean
the model calls it for every citation, so grounding cannot be assumed and has to
be checked.

A plausible but non-existent source is the most damaging thing this tool can
emit, so an unresolvable citation is moved out of `references` rather than shown.

Only 404 and 410 count as missing. Publishers block bots - Science.org answers
HEAD with 403 - and a blocked request is not evidence of fabrication. Anything
unproven is kept.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

_ARXIV_RE = re.compile(r"arxiv[:\s/]*(\d{4}\.\d{4,5})", re.IGNORECASE)
_BARE_ARXIV_RE = re.compile(r"\b(\d{4}\.\d{4,5})\b")
_DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s,;)\]]+)")
_URL_RE = re.compile(r"(https?://[^\s,;)\]]+)")

TIMEOUT_SECONDS = 8
MAX_WORKERS = 8


def citation_target(ref: str) -> tuple[str, str] | None:
    """The kind of citation and a URL that should resolve if it is real."""
    m = _ARXIV_RE.search(ref) or _BARE_ARXIV_RE.search(ref)
    if m:
        return "arxiv", f"https://arxiv.org/abs/{m.group(1)}"
    m = _DOI_RE.search(ref)
    if m:
        return "doi", f"https://doi.org/{m.group(1).rstrip('.')}"
    m = _URL_RE.search(ref)
    if m:
        return "url", m.group(1).rstrip(".,;)")
    return None


def _check_one(ref: str) -> dict:
    if not isinstance(ref, str):
        return {"ref": str(ref)[:120], "kind": "unresolvable", "status": "not_a_string"}

    target = citation_target(ref)
    if target is None:
        return {"ref": ref[:120], "kind": "unresolvable", "status": "no_target"}

    kind, url = target
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "qgc-eval/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = "resolved" if response.status < 400 else f"http_{response.status}"
    except urllib.error.HTTPError as exc:
        status = "missing" if exc.code in (404, 410) else f"http_{exc.code}"
    except Exception as exc:  # noqa: BLE001 - a network flake is not a fabrication
        status = f"unchecked ({type(exc).__name__})"
    return {"ref": ref[:120], "kind": kind, "url": url, "status": status}


def verify_citations(refs) -> list[dict]:
    """Resolve every citation that has a checkable target, in parallel."""
    items = list(refs or [])
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(items))) as pool:
        return list(pool.map(_check_one, items))


def partition_references(refs) -> tuple[list, list, list[dict]]:
    """Split references into ones a reader can trust and ones that do not exist.

    Returns (kept, rejected, checks). Only citations proven missing are rejected.
    """
    checks = verify_citations(refs)
    kept, rejected = [], []
    for ref, check in zip(refs or [], checks):
        (rejected if check.get("status") == "missing" else kept).append(ref)
    return kept, rejected, checks
