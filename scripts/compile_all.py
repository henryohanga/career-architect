#!/usr/bin/env python3
"""Batch compile job application documents.

This script builds resumes and cover letters for job applications,
with smart detection of which files need rebuilding.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_resume import BLOCK, validate_file  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
APPLICATIONS_DIR = ROOT / "applications"
BUILD_SCRIPT = ROOT / "scripts" / "build_resume.py"

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def log(icon: str, msg: str, color: str = RESET):
    """Print colored log message."""
    print(f"{color}{icon}{RESET} {msg}")


def get_document_paths(
    base_dir: Path,
    application: str = None,
    all_apps: bool = False,
    doc_types: list = None,
):
    """Get document paths to process based on options.

    Args:
        base_dir: Base applications directory
        application: Specific application folder name
        all_apps: Process all applications
        doc_types: List of document types to include (e.g., ['resume', 'cover_letter'])

    Returns:
        List of (app_dir, doc_paths) tuples
    """
    if doc_types is None:
        doc_types = ["resume", "cover_letter"]

    results = []

    if application:
        # Process specific application
        app_dir = base_dir / application
        if not app_dir.exists():
            log("✗", f"Application not found: {application}", RED)
            return []
        docs = [
            app_dir / f"{dt}.md" for dt in doc_types if (app_dir / f"{dt}.md").exists()
        ]
        if docs:
            results.append((app_dir, docs))
        else:
            log("✗", f"No documents found in {application}", RED)
        return results

    if not all_apps:
        # Default: process only the most recently modified application
        app_dirs = [d for d in base_dir.iterdir() if d.is_dir()]
        if not app_dirs:
            log("ℹ", "No applications found", BLUE)
            return []

        # Sort by modification time, most recent first
        app_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
        most_recent = app_dirs[0]
        docs = [
            most_recent / f"{dt}.md"
            for dt in doc_types
            if (most_recent / f"{dt}.md").exists()
        ]
        if docs:
            log("🎯", f"Processing most recent: {most_recent.name}", BLUE)
            results.append((most_recent, docs))
        else:
            log("⚠", f"No documents in {most_recent.name}", YELLOW)
        return results

    # Process all applications
    for app_dir in sorted(base_dir.iterdir()):
        if not app_dir.is_dir():
            continue
        docs = [
            app_dir / f"{dt}.md" for dt in doc_types if (app_dir / f"{dt}.md").exists()
        ]
        if docs:
            results.append((app_dir, docs))

    return results


def needs_rebuild(md_path: Path) -> bool:
    """Check if a document needs rebuilding."""
    pdf_path = md_path.with_suffix(".pdf")
    if not pdf_path.exists():
        return True
    return md_path.stat().st_mtime > pdf_path.stat().st_mtime


def auto_build(
    application: str = None,
    all_apps: bool = False,
    force: bool = False,
    formats: str = "pdf,docx,txt",
    doc_types: list = None,
    template: str = None,
):
    """Build documents for job applications.

    Args:
        application: Specific application folder name
        all_apps: Process all applications
        force: Force rebuild even if up to date
        formats: Output formats (comma-separated)
        doc_types: Document types to build
    """
    base_dir = APPLICATIONS_DIR

    if not base_dir.exists():
        log("ℹ", "No applications directory found", BLUE)
        return

    app_docs = get_document_paths(base_dir, application, all_apps, doc_types)

    if not app_docs:
        log("ℹ", "No documents to process", BLUE)
        return

    # Statistics
    total_docs = sum(len(docs) for _, docs in app_docs)
    built = 0
    skipped = 0
    failed = 0

    log("📋", f"Found {total_docs} document(s) in {len(app_docs)} application(s)", BLUE)
    print()

    for app_dir, doc_paths in app_docs:
        print(f"{BOLD}📁 {app_dir.name}{RESET}")

        for doc_path in doc_paths:
            doc_name = doc_path.stem

            if not force and not needs_rebuild(doc_path):
                log("⏭️", f" {doc_name} (up to date)", YELLOW)
                skipped += 1
                continue

            block_issues = [
                i for i in validate_file(doc_path) if i[0] == BLOCK
            ]
            if block_issues:
                log("✗", f" {doc_name} failed validation:", RED)
                for _, code, message in block_issues:
                    print(f"     [{code}] {message}")
                failed += 1
                continue

            log("🔨", f" Building {doc_name}...", BLUE)
            cmd = [
                sys.executable,
                str(BUILD_SCRIPT),
                str(doc_path),
                "--formats",
                formats,
            ]
            if template:
                cmd.extend(["--template", template])
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                built += 1
            else:
                log("✗", f" {doc_name} failed", RED)
                if result.stderr:
                    print(f"     {result.stderr[:200]}")
                failed += 1

        print()

    # Summary
    print(f"{BOLD}Summary:{RESET}")
    log("✓", f"Built: {built}", GREEN)
    if skipped:
        log("⏭️", f" Skipped: {skipped}", YELLOW)
    if failed:
        log("✗", f"Failed: {failed}", RED)


def list_applications():
    """List all applications with their status."""
    base_dir = APPLICATIONS_DIR
    if not base_dir.exists():
        log("ℹ", "No applications directory found", BLUE)
        return

    app_dirs = sorted(base_dir.iterdir(), key=lambda d: d.name, reverse=True)
    app_dirs = [d for d in app_dirs if d.is_dir()]

    if not app_dirs:
        log("ℹ", "No applications found", BLUE)
        return

    print(f"{BOLD}Applications ({len(app_dirs)}):{RESET}\n")

    for app_dir in app_dirs:
        resume = app_dir / "resume.md"
        cover = app_dir / "cover_letter.md"
        resume_pdf = app_dir / "resume.pdf"
        cover_pdf = app_dir / "cover_letter.pdf"

        # Status indicators
        r_status = "✓" if resume_pdf.exists() else ("○" if resume.exists() else "·")
        c_status = "✓" if cover_pdf.exists() else ("○" if cover.exists() else "·")

        # Parse date from folder name
        parts = app_dir.name.split("-")
        if len(parts) >= 3:
            date_str = "-".join(parts[:3])
            name = "-".join(parts[3:])
        else:
            date_str = "unknown"
            name = app_dir.name

        print(f"  [{r_status}R {c_status}C] {date_str}  {name}")

    print(f"\n  {GREEN}✓{RESET}=built  ○=source only  ·=missing")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build documents for job applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compile_all.py                    # Build most recent application
  python compile_all.py --all              # Build all applications
  python compile_all.py --application NAME # Build specific application
  python compile_all.py --list             # List all applications
  python compile_all.py --force            # Force rebuild even if up to date
  python compile_all.py --resume-only      # Build only resumes
        """,
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build all applications",
    )
    parser.add_argument(
        "--application",
        "-a",
        type=str,
        help="Build specific application by folder name",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all applications and their status",
    )
    parser.add_argument(
        "--force", "-f", action="store_true", help="Force rebuild even if up to date"
    )
    parser.add_argument(
        "--formats",
        default="pdf,docx,txt",
        help="Output formats: pdf,docx,txt (default: pdf,docx,txt)",
    )
    parser.add_argument(
        "--resume-only",
        action="store_true",
        help="Build only resumes, skip cover letters",
    )
    parser.add_argument(
        "--cover-only",
        action="store_true",
        help="Build only cover letters, skip resumes",
    )
    parser.add_argument(
        "--template",
        "-t",
        choices=["default", "minimal", "creative", "executive"],
        help="Resume template to use",
    )

    args = parser.parse_args()

    # Handle list command
    if args.list:
        list_applications()
        sys.exit(0)

    # Validate arguments
    if args.all and args.application:
        parser.error("--all and --application cannot be used together")

    if args.resume_only and args.cover_only:
        parser.error("--resume-only and --cover-only cannot be used together")

    # Determine document types
    doc_types = None
    if args.resume_only:
        doc_types = ["resume"]
    elif args.cover_only:
        doc_types = ["cover_letter"]

    auto_build(
        application=args.application,
        all_apps=args.all,
        force=args.force,
        formats=args.formats,
        doc_types=doc_types,
        template=args.template,
    )
