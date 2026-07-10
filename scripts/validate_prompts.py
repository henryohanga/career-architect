#!/usr/bin/env python3
"""Validate the .prompts/ system for structural problems.

Checks every .prompts/**/*.md for:
  - empty files
  - unbalanced code fences (```)
  - mojibake (U+FFFD replacement characters)
  - referenced .prompts/... and scripts/... paths that don't exist
  - the anti-fabrication block in every domain analyser/tailor_resume prompt

Exit code 0 when clean, 1 when any check fails. Used by CI (ci.yml).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / ".prompts"

ANTI_FABRICATION_MARKER = "NON-NEGOTIABLE — NO FABRICATION"
DOMAINS = ("engineering", "business", "creative", "healthcare", "academic")
REQUIRE_ANTI_FABRICATION = [
    PROMPTS_DIR / domain / name
    for domain in DOMAINS
    for name in ("analyser.md", "tailor_resume.md")
]

# Matches concrete repo paths mentioned in prompts (skips [folder]-style templates)
PATH_RE = re.compile(r"`((?:\.prompts|scripts|templates|source_materials)/[A-Za-z0-9_./-]+)`")


def check_file(path: Path) -> list:
    errors = []
    rel = path.relative_to(ROOT)

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{rel}: not valid UTF-8"]

    if not text.strip():
        errors.append(f"{rel}: file is empty")
        return errors

    if "�" in text:
        errors.append(f"{rel}: contains U+FFFD replacement character (mojibake)")

    fence_count = len(re.findall(r"^\s*```", text, flags=re.MULTILINE))
    if fence_count % 2 != 0:
        errors.append(f"{rel}: unbalanced code fences ({fence_count} ``` markers)")

    for ref in PATH_RE.findall(text):
        if "[" in ref or "<" in ref or "*" in ref:
            continue
        target = ROOT / ref
        if not target.exists():
            errors.append(f"{rel}: references missing path `{ref}`")

    return errors


def main() -> int:
    if not PROMPTS_DIR.exists():
        print("No .prompts directory found", file=sys.stderr)
        return 1

    errors = []
    files = sorted(PROMPTS_DIR.rglob("*.md"))
    for path in files:
        errors.extend(check_file(path))

    for path in REQUIRE_ANTI_FABRICATION:
        if not path.exists():
            errors.append(f"{path.relative_to(ROOT)}: required prompt file missing")
        elif ANTI_FABRICATION_MARKER not in path.read_text(encoding="utf-8"):
            errors.append(
                f"{path.relative_to(ROOT)}: missing '{ANTI_FABRICATION_MARKER}' block"
            )

    if errors:
        print(f"✗ Prompt validation failed ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✓ {len(files)} prompt files validated - all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
