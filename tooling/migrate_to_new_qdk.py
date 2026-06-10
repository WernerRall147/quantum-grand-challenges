#!/usr/bin/env python3
"""Migrate all Q# problems from old Microsoft.Quantum.Sdk to modern QDK.

Performs:
  1. Renames old .csproj and Program.qs to .old
  2. Creates qsharp.json + src/ directory
  3. Converts Q# source: strips namespace block, converts open→import
  4. Handles multi-file projects (e.g. problem 15)
  5. Handles C# host projects (e.g. problem 05)
"""

import re
import shutil
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

# Mapping of old `open Microsoft.Quantum.X` to new `import Std.X.*`
IMPORT_MAP = {
    "Microsoft.Quantum.Arrays": "Std.Arrays.*",
    "Microsoft.Quantum.Canon": "Std.Canon.*",
    "Microsoft.Quantum.Convert": "Std.Convert.*",
    "Microsoft.Quantum.Diagnostics": "Std.Diagnostics.*",
    "Microsoft.Quantum.Intrinsic": None,  # Intrinsic is auto-imported
    "Microsoft.Quantum.Math": "Std.Math.*",
    "Microsoft.Quantum.Measurement": "Std.Measurement.*",
    "Microsoft.Quantum.ResourceEstimation": "Std.ResourceEstimation.*",
}


def convert_qs_source(source: str, filename: str = "Main.qs") -> str:
    """Convert old-SDK Q# source to modern QDK format."""
    lines = source.splitlines()
    out_lines: list[str] = []
    
    # Header comment
    out_lines.append(f"// {filename}  Migrated to modern QDK (qsharp.json project format)")
    out_lines.append("")
    
    # Collect imports and strip namespace/open
    imports: list[str] = []
    in_namespace = False
    namespace_indent = 0
    brace_depth = 0
    body_lines: list[str] = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip namespace declaration
        if stripped.startswith("namespace ") and "{" in stripped:
            in_namespace = True
            namespace_indent = len(line) - len(line.lstrip())
            brace_depth = 1
            continue
        
        # Collect open statements
        m = re.match(r'\s*open\s+(Microsoft\.Quantum\.\w+)\s*;', line)
        if m:
            ns = m.group(1)
            mapped = IMPORT_MAP.get(ns)
            if mapped is not None:  # None means skip (auto-imported)
                imports.append(f"import {mapped};")
            continue
        
        if in_namespace:
            # Track brace depth to find the closing brace of namespace
            for ch in stripped:
                if ch == '{':
                    brace_depth += 1
                elif ch == '}':
                    brace_depth -= 1
            
            if brace_depth <= 0:
                # This is the closing brace of the namespace  skip it
                in_namespace = False
                continue
            
            # De-indent by one level (4 spaces or 1 tab)
            if line.startswith("    "):
                body_lines.append(line[4:])
            elif line.startswith("\t"):
                body_lines.append(line[1:])
            else:
                body_lines.append(line)
        else:
            body_lines.append(line)
    
    # Write imports
    for imp in sorted(set(imports)):
        out_lines.append(imp)
    if imports:
        out_lines.append("")
    
    # Write body (skip leading/trailing blank lines)
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    
    out_lines.extend(body_lines)
    out_lines.append("")  # trailing newline
    
    return "\n".join(out_lines)


def migrate_problem(problem_dir: Path, dry_run: bool = False) -> dict:
    """Migrate a single problem to the new QDK format.
    
    Returns dict with migration status and details.
    """
    qsharp_dir = problem_dir / "qsharp"
    result = {"problem": problem_dir.name, "status": "skipped", "details": []}
    
    if not qsharp_dir.exists():
        result["details"].append("No qsharp/ directory")
        return result
    
    # Skip if already migrated
    if (qsharp_dir / "qsharp.json").exists():
        result["status"] = "already_migrated"
        result["details"].append("qsharp.json already exists")
        return result
    
    # Find .csproj and .qs files
    csproj_files = list(qsharp_dir.glob("*.csproj"))
    qs_files = list(qsharp_dir.glob("*.qs"))
    
    if not qs_files:
        result["details"].append("No .qs files found")
        return result
    
    result["details"].append(f"Found {len(qs_files)} .qs files, {len(csproj_files)} .csproj files")
    
    if dry_run:
        result["status"] = "would_migrate"
        return result
    
    # Step 1: Create src/ directory
    src_dir = qsharp_dir / "src"
    src_dir.mkdir(exist_ok=True)
    
    # Step 2: Convert and move .qs files
    for qs_file in qs_files:
        if qs_file.suffix == ".old" or ".old" in qs_file.name:
            continue
        
        source = qs_file.read_text(encoding="utf-8")
        
        # Determine output filename
        if qs_file.name == "Program.qs":
            out_name = "Main.qs"
        else:
            out_name = qs_file.name
        
        converted = convert_qs_source(source, out_name)
        
        # Write converted file to src/
        (src_dir / out_name).write_text(converted, encoding="utf-8")
        result["details"].append(f"Converted {qs_file.name} → src/{out_name}")
        
        # Rename original to .old
        old_path = qs_file.with_suffix(qs_file.suffix + ".old")
        if not old_path.exists():
            qs_file.rename(old_path)
            result["details"].append(f"Renamed {qs_file.name} → {old_path.name}")
    
    # Step 3: Rename .csproj files to .old
    for csproj in csproj_files:
        old_path = csproj.with_suffix(csproj.suffix + ".old")
        if not old_path.exists():
            csproj.rename(old_path)
            result["details"].append(f"Renamed {csproj.name} → {old_path.name}")
    
    # Also handle C# host files (Driver.cs)  rename to .old
    for cs_file in qsharp_dir.glob("*.cs"):
        old_path = cs_file.with_suffix(cs_file.suffix + ".old")
        if not old_path.exists():
            cs_file.rename(old_path)
            result["details"].append(f"Renamed {cs_file.name} → {old_path.name}")
    
    # Handle host/ subdirectory (problem 05)
    host_dir = qsharp_dir / "host"
    if host_dir.exists():
        for f in host_dir.glob("*"):
            if f.is_file() and ".old" not in f.name:
                old_path = f.with_suffix(f.suffix + ".old")
                if not old_path.exists():
                    f.rename(old_path)
                    result["details"].append(f"Renamed host/{f.name} → {old_path.name}")
    
    # Step 4: Create qsharp.json
    (qsharp_dir / "qsharp.json").write_text("{}\n", encoding="utf-8")
    result["details"].append("Created qsharp.json")
    
    result["status"] = "migrated"
    return result


def main():
    import sys
    
    dry_run = "--dry-run" in sys.argv
    
    # Find all problem directories
    problem_dirs = sorted(
        [d for d in PROBLEMS_DIR.iterdir() if d.is_dir() and d.name[:2].isdigit()],
        key=lambda d: d.name,
    )
    
    print(f"Found {len(problem_dirs)} problem directories")
    if dry_run:
        print("[DRY RUN  no files will be modified]")
    print()
    
    results = []
    for problem_dir in problem_dirs:
        result = migrate_problem(problem_dir, dry_run=dry_run)
        results.append(result)
        status_icon = {
            "migrated": "✅",
            "already_migrated": "⏭️",
            "skipped": "⏭️",
            "would_migrate": "🔄",
        }.get(result["status"], "❓")
        print(f"{status_icon} {result['problem']}: {result['status']}")
        for detail in result["details"]:
            print(f"   {detail}")
    
    # Summary
    migrated = sum(1 for r in results if r["status"] == "migrated")
    already = sum(1 for r in results if r["status"] == "already_migrated")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    print(f"\nSummary: {migrated} migrated, {already} already done, {skipped} skipped")


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
