#!/usr/bin/env python3
"""Build resume and cover letter outputs from Markdown.

This script converts Markdown files to PDF, DOCX, and TXT formats
using Pandoc with custom LaTeX styling.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from shutil import which
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "templates"
APPLICATIONS_DIR = ROOT / "applications"
SOURCE_MATERIALS_DIR = ROOT / "source_materials"
IDENTITY_JSON = SOURCE_MATERIALS_DIR / "identity.json"

# Available resume templates
TEMPLATES = {
    "default": TEMPLATES_DIR / "style.tex",
    "minimal": TEMPLATES_DIR / "minimal.tex",
    "creative": TEMPLATES_DIR / "creative.tex",
    "executive": TEMPLATES_DIR / "executive.tex",
}
COVER_LETTER_STYLE_TEX = TEMPLATES_DIR / "cover_letter_style.tex"


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def read_file(path: Path) -> str:
    """Read file contents with UTF-8 encoding."""
    return path.read_text(encoding="utf-8")


def log_success(msg: str):
    """Print success message in green."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")


def log_warning(msg: str):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")


def log_error(msg: str):
    """Print error message in red."""
    print(f"{Colors.RED}✗{Colors.RESET} {msg}", file=sys.stderr)


def log_info(msg: str):
    """Print info message in blue."""
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")


def load_identity() -> Optional[dict]:
    """Load identity data from source materials."""
    if not IDENTITY_JSON.exists():
        return None
    try:
        return json.loads(IDENTITY_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log_warning(f"Invalid identity.json: {e}")
        return None


def validate_contact_info(text: str, identity: dict) -> list:
    """Validate that contact info in document matches identity.json."""
    warnings = []
    email = identity.get("email", "")

    if email and email != "your@email.com":
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        found_emails = re.findall(email_pattern, text)
        for found in found_emails:
            if found.lower() != email.lower():
                if "example.com" not in found.lower():
                    warnings.append(
                        f"Email mismatch: found '{found}', expected '{email}'"
                    )

    return warnings


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from Markdown text."""
    m = re.match(r"^---\n([\s\S]*?)\n---\n?", text)
    if not m:
        return {}
    raw = m.group(1)
    result = {}
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = v.strip()
    return result


def slugify(s: str) -> str:
    """Convert string to URL-friendly slug."""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"


def ensure_dirs():
    """Ensure required directories exist."""
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    APPLICATIONS_DIR.mkdir(parents=True, exist_ok=True)


def run(cmd: list, cwd: Path, timeout: int = 120):
    """Run a command with timeout."""
    try:
        return subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            cmd, returncode=1, stdout="", stderr="Build timed out"
        )


def check_dependencies() -> bool:
    """Check that required dependencies are installed."""
    missing = []
    if which("pandoc") is None:
        missing.append("pandoc")
    if which("pdflatex") is None:
        missing.append("pdflatex (LaTeX distribution)")

    if missing:
        log_error(f"Missing dependencies: {', '.join(missing)}")
        log_info("Install pandoc: https://pandoc.org/installing.html")
        log_info("Install LaTeX: brew install --cask mactex-no-gui (macOS)")
        return False
    return True


def _escape_latex(value: str) -> str:
    """Escape special LaTeX characters in a string value."""
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for char, escaped in replacements:
        value = value.replace(char, escaped)
    return value


def build_contact_header_file(identity: dict) -> Optional[str]:
    """Write a temp .tex file with the \\contactline call from identity.json.

    Returns the file path, or None if identity is missing / placeholder-only.
    The caller is responsible for deleting the file after pandoc runs.
    """
    PLACEHOLDERS = {"Your Name", "your@email.com", "+254 712 345 678", "Nairobi, Kenya", "", None}

    name = identity.get("full_name", "")
    if name in PLACEHOLDERS:
        return None  # identity not filled in — skip header injection

    def field(key: str, fallback: str = "") -> str:
        val = identity.get(key) or fallback
        return _escape_latex(val)

    name_tex = field("full_name")
    location_tex = field("location")
    phone_tex = field("phone")
    email_tex = field("email")
    linkedin = identity.get("linkedin") or ""
    github = identity.get("github") or ""
    portfolio = identity.get("portfolio") or ""

    # Build the \contactline call — use raw URLs (not escaped) for href args
    contact_line = (
        f"\\contactline{{{name_tex}}}"
        f"{{{location_tex}}}"
        f"{{{phone_tex}}}"
        f"{{{email_tex}}}"
        f"{{{linkedin or 'https://linkedin.com'}}}"
        f"{{{github or 'https://github.com'}}}"
        f"{{{portfolio or 'https://example.com'}}}"
    )

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".tex", delete=False, encoding="utf-8"
    )
    tmp.write(contact_line + "\n")
    tmp.close()
    return tmp.name


def build_format(
    input_md: Path,
    out_dir: Path,
    fmt: str,
    style_file: Path,
    contact_header_file: Optional[str] = None,
) -> tuple:
    """Build a single format. Returns (format, success, output_path, error)."""
    base_name = input_md.stem

    if fmt == "pdf":
        out_path = out_dir / f"{base_name}.pdf"
        cmd = [
            "pandoc",
            str(input_md),
            "-o",
            str(out_path),
            "--include-in-header",
            str(style_file),
            "--pdf-engine",
            "pdflatex",
            "--metadata=title=",
            "--metadata=author=",
            "--metadata=date=",
        ]
        if contact_header_file:
            cmd += ["--include-before-body", contact_header_file]
    elif fmt == "docx":
        out_path = out_dir / f"{base_name}.docx"
        cmd = ["pandoc", str(input_md), "-o", str(out_path)]
    elif fmt == "txt":
        out_path = out_dir / f"{base_name}.txt"
        cmd = ["pandoc", str(input_md), "-t", "plain", "-o", str(out_path)]
    else:
        return (fmt, False, None, f"Unknown format: {fmt}")

    r = run(cmd, ROOT)
    if r.returncode != 0:
        return (fmt, False, out_path, r.stderr)
    return (fmt, True, out_path, None)


def get_template(template_name: str = None) -> Path:
    """Get the template file path.

    Priority:
    1. Explicit template_name argument
    2. identity.json -> preferences.template
    3. Default template (style.tex)
    """
    if template_name and template_name in TEMPLATES:
        return TEMPLATES[template_name]

    # Check identity.json for preference
    identity = load_identity()
    if identity:
        prefs = identity.get("preferences", {})
        pref_template = prefs.get("template", "default")
        if pref_template in TEMPLATES:
            return TEMPLATES[pref_template]

    return TEMPLATES["default"]


def build_outputs(
    input_md: Path,
    company: str,
    role: str,
    formats: list,
    validate: bool = True,
    parallel: bool = True,
    template: str = None,
):
    """Build all requested output formats from Markdown input."""
    ensure_dirs()

    # Determine output directory
    if APPLICATIONS_DIR in input_md.parents:
        out_dir = input_md.parent
    else:
        out_dir = APPLICATIONS_DIR / f"{slugify(company)}-{slugify(role)}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Load and validate identity
    text = read_file(input_md)
    identity = load_identity()
    if validate and identity:
        for warning in validate_contact_info(text, identity):
            log_warning(f"CONTACT VALIDATION: {warning}")

    # Determine style file
    base_name = input_md.stem
    is_cover_letter = "cover_letter" in base_name
    if is_cover_letter:
        style_file = COVER_LETTER_STYLE_TEX
    else:
        style_file = get_template(template)
        log_info(f"Using template: {style_file.stem}")

    if not style_file.exists():
        log_error(f"Style file not found: {style_file}")
        sys.exit(1)

    # Build contact header from identity.json for resume PDFs
    contact_header_file = None
    if not is_cover_letter and identity:
        contact_header_file = build_contact_header_file(identity)
        if contact_header_file:
            log_info(f"Injecting contact header for: {identity.get('full_name', '')}")
        else:
            log_warning("identity.json appears unfilled — PDF will have no name/contact header")

    log_info(f"Building {base_name} → {', '.join(formats)}")

    # Build formats (parallel or sequential)
    results = []
    try:
        if parallel and len(formats) > 1:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(
                        build_format, input_md, out_dir, fmt, style_file, contact_header_file
                    ): fmt
                    for fmt in formats
                }
                for future in as_completed(futures):
                    results.append(future.result())
        else:
            for fmt in formats:
                results.append(build_format(input_md, out_dir, fmt, style_file, contact_header_file))
    finally:
        # Always clean up the temp header file
        if contact_header_file:
            Path(contact_header_file).unlink(missing_ok=True)

    # Report results
    success_count = 0
    for fmt, success, out_path, error in results:
        if success:
            log_success(f"Built {out_path}")
            success_count += 1
        else:
            log_error(f"{fmt.upper()} build failed: {error}")

    # Summary
    if success_count == len(formats):
        log_success(f"All {success_count} formats built successfully")
    elif success_count > 0:
        log_warning(f"{success_count}/{len(formats)} formats built")
    else:
        log_error("All builds failed")
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(
        prog="build_resume",
        description="Build resume/cover letter outputs from Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_resume.py resume.md
  python build_resume.py resume.md --formats pdf
  python build_resume.py cover_letter.md --company "Acme Inc" --role "Senior Engineer"
        """,
    )
    p.add_argument("input", help="Path to input Markdown file")
    p.add_argument("--company", help="Company name override")
    p.add_argument("--role", help="Role name override")
    p.add_argument(
        "--formats",
        default="pdf,docx,txt",
        help="Comma-separated formats: pdf,docx,txt (default: pdf,docx,txt)",
    )
    p.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip contact info validation against identity.json",
    )
    p.add_argument(
        "--sequential",
        action="store_true",
        help="Build formats sequentially instead of in parallel",
    )
    p.add_argument(
        "--template",
        "-t",
        choices=["default", "minimal", "creative", "executive"],
        help="Resume template (default: from identity.json or 'default')",
    )
    args = p.parse_args()

    input_md = Path(args.input).resolve()
    if not input_md.exists():
        log_error(f"Input file not found: {input_md}")
        sys.exit(1)

    if not input_md.suffix.lower() == ".md":
        log_warning(f"Input file may not be Markdown: {input_md.suffix}")

    text = read_file(input_md)
    fm = parse_frontmatter(text)
    company = args.company or fm.get("company") or "Company"
    role = args.role or fm.get("role") or "Role"
    formats = [f.strip().lower() for f in args.formats.split(",") if f.strip()]

    # Validate formats
    valid_formats = {"pdf", "docx", "txt"}
    invalid = set(formats) - valid_formats
    if invalid:
        log_error(
            f"Invalid formats: {', '.join(invalid)}. Valid: {', '.join(valid_formats)}"
        )
        sys.exit(1)

    build_outputs(
        input_md,
        company,
        role,
        formats,
        validate=not args.no_validate,
        parallel=not args.sequential,
        template=args.template,
    )


if __name__ == "__main__":
    main()
