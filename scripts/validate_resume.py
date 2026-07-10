#!/usr/bin/env python3
"""Resume/cover-letter validator - code-enforced quality guardrails.

Enforces the rules that previously lived only in prompts:
  BLOCK (exit 1, refuses build):
    - missing or invalid YAML frontmatter (company, role, date required)
    - H1 heading in the body (the LaTeX template renders the name header)
    - contact info (email / phone / linkedin / github) that contradicts
      source_materials/identity.json - hallucinated contact info
    - resume with no experience-type section
  WARN (printed, does not fail):
    - placeholder text left in the document
    - missing skills/education sections
    - very long lines (LaTeX overflow risk)

Usage:
    python scripts/validate_resume.py <resume.md | application_folder> [--json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY_JSON = ROOT / "source_materials" / "identity.json"

BLOCK = "BLOCK"
WARN = "WARN"

REQUIRED_FRONTMATTER = ("company", "role", "date")

# A resume must contain at least one of these section headings (## level).
EXPERIENCE_SECTIONS = {
    "experience", "professional experience", "work experience", "employment",
    "work history", "research experience", "clinical experience",
    "teaching experience", "selected experience", "relevant experience",
}
RECOMMENDED_SECTIONS = {"skills", "education"}

PLACEHOLDER_PATTERNS = [
    r"lorem ipsum",
    r"\byour name\b",
    r"your@email\.com",
    r"\bTODO\b",
    r"\[company name\]",
    r"\[role title\]",
    r"\[insert [^\]]*\]",
    r"xxx-xxx",
]

MAX_LINE_LENGTH = 300


def parse_frontmatter(text: str) -> dict | None:
    """Parse simple YAML frontmatter. Returns None if absent."""
    m = re.match(r"^---\n([\s\S]*?)\n---\n?", text)
    if not m:
        return None
    result = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = v.strip().strip("\"'")
    return result


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n[\s\S]*?\n---\n?", "", text)


def _normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")


def _is_placeholder_identity(value: str) -> bool:
    if not value:
        return True
    v = value.strip().lower()
    return (
        v.startswith("your")
        or "example.com" in v
        or v in {"+254 712 345 678", "city, country"}
    )


def load_identity() -> dict:
    if IDENTITY_JSON.exists():
        try:
            return json.loads(IDENTITY_JSON.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def validate_text(text: str, identity: dict | None = None, doc_type: str = "resume") -> list:
    """Validate document text. Returns list of (severity, code, message)."""
    if identity is None:
        identity = load_identity()
    issues = []

    # --- frontmatter ---
    fm = parse_frontmatter(text)
    if fm is None:
        issues.append((BLOCK, "FRONTMATTER_MISSING",
                       "No YAML frontmatter found (--- block with company/role/date)"))
    else:
        for field in REQUIRED_FRONTMATTER:
            if not fm.get(field):
                issues.append((BLOCK, "FRONTMATTER_FIELD",
                               f"Frontmatter is missing required field '{field}'"))

    body = strip_frontmatter(text)

    # --- no H1 in body (template renders the name header) ---
    in_code_block = False
    for i, line in enumerate(body.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block and re.match(r"^#\s+", line):
            issues.append((BLOCK, "H1_IN_BODY",
                           f"H1 heading in body (line {i}): '{line.strip()[:60]}' - "
                           "the LaTeX template renders the name header; use ## sections"))

    # --- contact info must match identity.json ---
    email = (identity.get("email") or "").strip()
    if email and not _is_placeholder_identity(email):
        for found in re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", body):
            if found.lower() != email.lower() and "example.com" not in found.lower():
                issues.append((BLOCK, "CONTACT_EMAIL",
                               f"Email '{found}' does not match identity.json ('{email}')"))

    phone = _normalize_phone(identity.get("phone", ""))
    if phone and not _is_placeholder_identity(identity.get("phone", "")):
        for found in re.findall(r"\+?[\d][\d\s().-]{7,}\d", body):
            found_norm = _normalize_phone(found)
            if len(found_norm) >= 9 and found_norm[-9:] != phone[-9:]:
                issues.append((BLOCK, "CONTACT_PHONE",
                               f"Phone '{found.strip()}' does not match identity.json"))

    for field, domain in (("linkedin", "linkedin.com"), ("github", "github.com")):
        expected = (identity.get(field) or "").strip().rstrip("/").lower()
        if not expected:
            continue
        for found in re.findall(rf"https?://[^\s)\]]*{re.escape(domain)}[^\s)\]]*", body):
            if found.rstrip("/").lower() != expected:
                issues.append((BLOCK, f"CONTACT_{field.upper()}",
                               f"{field} URL '{found}' does not match identity.json"))

    # --- required sections (resumes only) ---
    if doc_type == "resume":
        headings = {
            re.sub(r"[^a-z ]", "", h.strip().lower()).strip()
            for h in re.findall(r"^##\s+(.+)$", body, flags=re.MULTILINE)
        }
        if not headings & EXPERIENCE_SECTIONS:
            issues.append((BLOCK, "SECTION_EXPERIENCE",
                           "No experience section found (expected a '## Experience' "
                           "or equivalent heading)"))
        for section in sorted(RECOMMENDED_SECTIONS):
            if not any(section in h for h in headings):
                issues.append((WARN, "SECTION_RECOMMENDED",
                               f"No '{section}' section found - recommended for ATS"))

    # --- placeholder text ---
    for pattern in PLACEHOLDER_PATTERNS:
        m = re.search(pattern, body, flags=re.IGNORECASE)
        if m:
            issues.append((WARN, "PLACEHOLDER",
                           f"Possible placeholder text: '{m.group()[:40]}'"))

    # --- long lines (LaTeX overflow risk) ---
    for i, line in enumerate(body.splitlines(), 1):
        if len(line) > MAX_LINE_LENGTH:
            issues.append((WARN, "LONG_LINE",
                           f"Line {i} is {len(line)} chars - may overflow in PDF"))

    return issues


def validate_file(path: Path, identity: dict | None = None) -> list:
    """Validate a markdown file. Doc type inferred from filename."""
    doc_type = "cover_letter" if "cover_letter" in path.stem else "resume"
    return validate_text(path.read_text(encoding="utf-8"), identity, doc_type)


def _print_issues(path: Path, issues: list):
    if not issues:
        print(f"\033[92m✓\033[0m {path.name}: all checks passed")
        return
    for severity, code, message in issues:
        color = "\033[91m" if severity == BLOCK else "\033[93m"
        print(f"{color}{severity}\033[0m [{code}] {path.name}: {message}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate resume/cover letter against quality guardrails"
    )
    parser.add_argument("path", help="Path to a .md file or an application folder")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    path = Path(args.path)
    if path.is_dir():
        targets = [p for p in (path / "resume.md", path / "cover_letter.md") if p.exists()]
        if not targets:
            print(f"\033[91m✗\033[0m No resume.md or cover_letter.md in {path}", file=sys.stderr)
            return 1
    elif path.exists():
        targets = [path]
    else:
        print(f"\033[91m✗\033[0m File not found: {path}", file=sys.stderr)
        return 1

    identity = load_identity()
    all_results = {}
    has_block = False
    for target in targets:
        issues = validate_file(target, identity)
        all_results[str(target)] = [
            {"severity": s, "code": c, "message": m} for s, c, m in issues
        ]
        has_block = has_block or any(s == BLOCK for s, _, _ in issues)
        if not args.json:
            _print_issues(target, issues)

    if args.json:
        print(json.dumps({"pass": not has_block, "results": all_results}, indent=2))

    return 1 if has_block else 0


if __name__ == "__main__":
    sys.exit(main())
