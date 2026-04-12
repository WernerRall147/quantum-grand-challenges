"""Extract problem READMEs into website/data/problemReadmes.json with HTML conversion."""

import html as html_mod
import json
import os
import re


def md_to_html(md: str) -> str:
    lines = md.split("\n")
    out = []
    in_code = False
    in_list = False
    for line in lines:
        if line.strip().startswith("```") or line.strip().startswith("~~~"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                lang = line.strip().lstrip("`").lstrip("~").strip()
                out.append(f'<pre><code class="language-{lang}">' if lang else "<pre><code>")
                in_code = True
            continue
        if in_code:
            out.append(html_mod.escape(line))
            continue
        if in_list and not line.strip().startswith("- ") and not line.strip().startswith("* "):
            out.append("</ul>")
            in_list = False
        if not line.strip():
            out.append("")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{m.group(2)}</h{level}>")
            continue
        m = re.match(r"^\s*[-*]\s+(.*)", line)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{m.group(1)}</li>")
            continue
        line = re.sub(r"`([^`]+)`", r"<code>\1</code>", line)
        line = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", line)
        line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', line)
        out.append(f"<p>{line}</p>")
    if in_list:
        out.append("</ul>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def main():
    readmes = {}
    for d in sorted(os.listdir("problems")):
        rp = os.path.join("problems", d, "README.md")
        if os.path.isfile(rp):
            md = open(rp, encoding="utf-8").read()
            readmes[d] = {"html": md_to_html(md)}
    out_path = os.path.join("website", "data", "problemReadmes.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(readmes, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(readmes)} READMEs to {out_path}")


if __name__ == "__main__":
    main()
"""Extract problem READMEs into website/data/problemReadmes.json with HTML conversion."""

import html as html_mod
import json
import os
import re


def md_to_html(md: str) -> str:
    lines = md.split("\n")
    out = []
    in_code = False
    in_list = False
    for line in lines:
        # Code blocks
        if line.strip().startswith("```") or line.strip().startswith("~~~"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                lang = line.strip().lstrip("`").lstrip("~").strip()
                out.append(f'<pre><code class="language-{lang}">' if lang else "<pre><code>")
                in_code = True
            continue
        if in_code:
            out.append(html_mod.escape(line))
            continue
        # Close list if needed
        if in_list and not line.strip().startswith("- ") and not line.strip().startswith("* "):
            out.append("</ul>")
            in_list = False
        # Empty lines
        if not line.strip():
            out.append("")
            continue
        # Headers
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            out.append(f"<h{level}>{text}</h{level}>")
            continue
        # List items
        m = re.match(r"^\s*[-*]\s+(.*)", line)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{m.group(1)}</li>")
            continue
        # Inline formatting
        line = re.sub(r"`([^`]+)`", r"<code>\1</code>", line)
        line = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", line)
        line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', line)
        out.append(f"<p>{line}</p>")
    if in_list:
        out.append("</ul>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def main():
    readmes = {}
    for d in sorted(os.listdir("problems")):
        rp = os.path.join("problems", d, "README.md")
        if os.path.isfile(rp):
            md = open(rp, encoding="utf-8").read()
            readmes[d] = {"html": md_to_html(md)}

    out_path = os.path.join("website", "data", "problemReadmes.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(readmes, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(readmes)} READMEs to {out_path}")


if __name__ == "__main__":
    main()
