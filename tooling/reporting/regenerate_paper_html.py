#!/usr/bin/env python3
"""Regenerate the methodology paper HTML from markdown source."""

import markdown
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
md_path = REPO / "docs" / "paper" / "methodology-paper.md"
html_path = REPO / "docs" / "paper" / "methodology-paper.html"

md_text = md_path.read_text(encoding="utf-8")
html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc"])

CSS = """
@page { size: A4; margin: 25mm; }
@media print { body { font-size: 10pt; } }
body { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.65; color: #1a1a1a; }
h1 { font-size: 20pt; color: #1a1a2e; margin-bottom: 0.3em; }
h2 { font-size: 14pt; color: #16213e; border-bottom: 2px solid #667eea; padding-bottom: 4px; margin-top: 2em; }
h3 { font-size: 12pt; color: #0f3460; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 9.5pt; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; }
th { background: #f0f4ff; font-weight: 600; color: #16213e; }
tr:nth-child(even) { background: #fafafa; }
code { background: #f5f5f5; padding: 2px 5px; border-radius: 3px; font-size: 9.5pt; font-family: 'Cascadia Code', Consolas, monospace; }
pre { background: #f5f5f5; padding: 14px; border-radius: 6px; overflow-x: auto; font-size: 9pt; border: 1px solid #e0e0e0; }
blockquote { border-left: 3px solid #667eea; margin-left: 0; padding-left: 1em; color: #555; font-style: italic; }
a { color: #0f3460; text-decoration: none; }
a:hover { text-decoration: underline; }
em { color: #555; }
strong { color: #1a1a2e; }
"""

html = f"""<!DOCTYPE html>
<html><head>
<meta charset=utf-8>
<title>Quantum Grand Challenges - Methodology Paper</title>
<style>{CSS}</style>
</head><body>
{html_body}
</body></html>"""

html_path.write_text(html, encoding="utf-8")
print(f"Regenerated: {html_path.relative_to(REPO)}")
