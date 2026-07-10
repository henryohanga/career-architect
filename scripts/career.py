#!/usr/bin/env python3
"""Career Architect CLI - Unified command interface for job application workflow.

Usage:
    python scripts/career.py <command> [options]

Commands:
    new         Create a new job application
    build       Build documents for an application
    list        List all applications
    status      Show project status and statistics
    validate    Validate source materials
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICATIONS_DIR = ROOT / "applications"
SOURCE_DIR = ROOT / "source_materials"
IDENTITY_JSON = SOURCE_DIR / "identity.json"
MASTER_EXP = SOURCE_DIR / "master_experience.md"

# Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def log(icon: str, msg: str, color: str = RESET):
    print(f"{color}{icon}{RESET} {msg}")


def cmd_new(args):
    """Create a new job application directory."""
    date = datetime.now().strftime("%Y-%m-%d")

    # Get company and role
    company = args.company or input("Company name: ").strip()
    role = args.role or input("Role title: ").strip()

    if not company or not role:
        log("✗", "Company and role are required", RED)
        return 1

    # Create slug
    slug = f"{company}-{role}".lower()
    slug = "-".join(slug.split())
    slug = "".join(c if c.isalnum() or c == "-" else "-" for c in slug)
    slug = "-".join(filter(None, slug.split("-")))

    folder_name = f"{date}-{slug}"
    app_dir = APPLICATIONS_DIR / folder_name

    if app_dir.exists():
        log("⚠", f"Application already exists: {folder_name}", YELLOW)
        return 1

    app_dir.mkdir(parents=True, exist_ok=True)

    # Create job_desc.md
    job_desc = app_dir / "job_desc.md"
    job_desc.write_text(
        f"""---
company: {company}
role: {role}
date: {date}
status: draft
---

# {company} - {role}

## Job Description

Paste the job description here.

## Key Requirements

-

## Notes

-
""",
        encoding="utf-8",
    )

    log("✓", f"Created: {app_dir.relative_to(ROOT)}", GREEN)
    log("ℹ", f"Next: Edit {job_desc.relative_to(ROOT)}", BLUE)

    return 0


def cmd_build(args):
    """Build documents using compile_all.py."""
    cmd = [sys.executable, str(ROOT / "scripts" / "compile_all.py")]

    if args.all:
        cmd.append("--all")
    if args.application:
        cmd.extend(["--application", args.application])
    if args.force:
        cmd.append("--force")
    if args.formats:
        cmd.extend(["--formats", args.formats])

    return subprocess.run(cmd, cwd=str(ROOT)).returncode


def cmd_list(args):
    """List applications using compile_all.py."""
    cmd = [sys.executable, str(ROOT / "scripts" / "compile_all.py"), "--list"]
    return subprocess.run(cmd, cwd=str(ROOT)).returncode


def cmd_stats(args):
    """Show detailed application statistics and analytics."""
    print(f"\n{BOLD}Application Analytics{RESET}\n")

    if not APPLICATIONS_DIR.exists():
        log("✗", "No applications directory found", RED)
        return 1

    apps = [
        d
        for d in APPLICATIONS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]

    if not apps:
        log("ℹ", "No applications yet", BLUE)
        return 0

    # Gather statistics
    total = len(apps)
    by_status = {"draft": 0, "applied": 0, "interview": 0, "rejected": 0}
    by_month = {}
    companies = set()
    has_resume = 0
    has_cover = 0

    for app in apps:
        name = app.name
        if len(name) >= 7 and name[4] == "-" and name[7] == "-":
            month = name[:7]
            by_month[month] = by_month.get(month, 0) + 1

        if (app / "resume.md").exists():
            has_resume += 1
        if (app / "cover_letter.md").exists():
            has_cover += 1

        job_desc = app / "job_desc.md"
        if job_desc.exists():
            content = job_desc.read_text()
            for status in by_status.keys():
                if f"status: {status}" in content:
                    by_status[status] += 1
                    break
            for line in content.split("\n"):
                if line.startswith("company:"):
                    companies.add(line.split(":", 1)[1].strip())

    # Print stats
    print(f"  {BOLD}Overview{RESET}")
    print(f"  Total applications: {total}")
    print(f"  Unique companies:   {len(companies)}")
    print()

    print(f"  {BOLD}By Status{RESET}")
    for status, count in by_status.items():
        if count > 0:
            print(f"  {status:<10} {count:>3} {'█' * count}")
    print()

    print(f"  {BOLD}Documents{RESET}")
    print(f"  With resume:       {has_resume}/{total}")
    print(f"  With cover letter: {has_cover}/{total}")
    print()

    if by_month:
        print(f"  {BOLD}By Month{RESET}")
        for month in sorted(by_month.keys(), reverse=True)[:6]:
            print(f"  {month}  {by_month[month]:>3} {'█' * by_month[month]}")

    return 0


def cmd_status(args):
    """Show project status and statistics."""
    print(f"\n{BOLD}Career Architect Status{RESET}\n")

    # Check source materials
    print(f"{BOLD}Source Materials:{RESET}")

    if IDENTITY_JSON.exists():
        try:
            identity = json.loads(IDENTITY_JSON.read_text())
            name = identity.get("full_name", "Not set")
            if name == "Your Name":
                log("⚠", f"Identity: {name} (update required)", YELLOW)
            else:
                log("✓", f"Identity: {name}", GREEN)
        except json.JSONDecodeError:
            log("✗", "Identity: Invalid JSON", RED)
    else:
        log("✗", "Identity: Missing", RED)

    if MASTER_EXP.exists():
        content = MASTER_EXP.read_text()
        lines = len(content.splitlines())
        if lines > 50:
            log("✓", f"Master Experience: {lines} lines", GREEN)
        else:
            log("⚠", f"Master Experience: {lines} lines (needs more content)", YELLOW)
    else:
        log("✗", "Master Experience: Missing", RED)

    # Count applications
    print(f"\n{BOLD}Applications:{RESET}")

    if APPLICATIONS_DIR.exists():
        apps = [d for d in APPLICATIONS_DIR.iterdir() if d.is_dir()]
        total = len(apps)

        with_resume = sum(1 for a in apps if (a / "resume.md").exists())
        with_cover = sum(1 for a in apps if (a / "cover_letter.md").exists())
        with_pdf = sum(1 for a in apps if (a / "resume.pdf").exists())

        log("📁", f"Total: {total}", BLUE)
        log("📄", f"With resume.md: {with_resume}", BLUE)
        log("✉️", f"With cover_letter.md: {with_cover}", BLUE)
        log("📑", f"With PDF: {with_pdf}", BLUE)
    else:
        log("ℹ", "No applications yet", BLUE)

    print()
    return 0


def cmd_ats(args):
    """Run ATS keyword scoring."""
    cmd = [sys.executable, str(ROOT / "scripts" / "ats_score.py")]

    if args.path:
        cmd.append(args.path)
    else:
        # Find most recent application
        if APPLICATIONS_DIR.exists():
            apps = sorted(
                [d for d in APPLICATIONS_DIR.iterdir() if d.is_dir()], reverse=True
            )
            if apps:
                cmd.append(str(apps[0]))
            else:
                log("✗", "No applications found", RED)
                return 1
        else:
            log("✗", "Applications directory not found", RED)
            return 1

    if args.json:
        cmd.append("--json")

    return subprocess.run(cmd, cwd=str(ROOT)).returncode


def cmd_scrape(args):
    """Scrape job description from URL."""
    from job_scraper import fetch_job, create_application

    print(f"\n{BOLD}Job Scraper{RESET}\n")

    data = fetch_job(args.url)
    if not data:
        return 1

    log("✓", f"Company: {data.get('company', 'Unknown')}", GREEN)
    log("✓", f"Role: {data.get('role', 'Unknown')}", GREEN)

    if args.create:
        app_dir = create_application(data)
        if app_dir:
            log("✓", f"Created: {app_dir.name}", GREEN)
    else:
        desc = data.get("description", "")[:500]
        if desc:
            print(f"\nDescription preview:\n{desc}...")
        print("\nRun with --create to create application folder")

    return 0


def cmd_batch(args):
    """Batch process multiple job descriptions."""
    from batch_process import process_folder

    input_dir = Path(args.input)
    print(f"\n{BOLD}Batch Processing Job Descriptions{RESET}\n")

    if args.dry_run:
        log("ℹ", "DRY RUN - No folders will be created", BLUE)

    results = process_folder(input_dir, args.dry_run)

    print(f"\n{BOLD}Summary{RESET}")
    print(f"  Processed: {len(results['processed'])}")
    print(f"  Skipped:   {len(results['skipped'])}")
    print(f"  Errors:    {len(results['errors'])}")

    return 0 if not results["errors"] else 1


def cmd_export(args):
    """Export resume to ATS-friendly formats."""
    from export_resume import export_txt, export_json_resume, find_latest_application

    # Find application folder
    if args.app:
        app_path = APPLICATIONS_DIR / args.app
        if not app_path.exists():
            app_path = Path(args.app)
    else:
        app_path = find_latest_application()

    if not app_path or not app_path.exists():
        log("✗", "No application found", RED)
        return 1

    resume_path = app_path / "resume.md"
    if not resume_path.exists():
        log("✗", f"No resume.md in {app_path.name}", RED)
        return 1

    output_dir = Path(args.output) if args.output else app_path
    log("ℹ", f"Exporting from: {app_path.name}", BLUE)

    success = True
    if args.format in ("txt", "all"):
        txt_path = output_dir / "resume.txt"
        if export_txt(resume_path, txt_path):
            log("✓", f"Created: {txt_path.name}", GREEN)
        else:
            log("✗", "Failed to create TXT", RED)
            success = False

    if args.format in ("json", "all"):
        json_path = output_dir / "resume.json"
        if export_json_resume(resume_path, json_path):
            log("✓", f"Created: {json_path.name}", GREEN)
        else:
            log("✗", "Failed to create JSON", RED)
            success = False

    return 0 if success else 1


def cmd_version(args):
    """Track resume versions."""
    from version_tracker import VersionTracker, find_latest_application

    # Find application folder
    if args.app:
        app_path = APPLICATIONS_DIR / args.app
        if not app_path.exists():
            app_path = Path(args.app)
    else:
        app_path = find_latest_application()

    if not app_path or not app_path.exists():
        log("✗", "No application found", RED)
        return 1

    tracker = VersionTracker(app_path)
    log("ℹ", f"Application: {app_path.name}", BLUE)

    if args.action == "save":
        result = tracker.save_version(args.file, args.message)
        if result:
            log("✓", f"Saved {result['id']}: {result['message']}", GREEN)
        else:
            log("⚠", "No changes to save", YELLOW)

    elif args.action == "list":
        versions = tracker.list_versions(args.file)
        print(f"\n  Version history for {args.file}:\n")
        if not versions:
            print("  No versions found")
        else:
            print(f"  {'Ver':<5} {'Date':<20} {'Message'}")
            print(f"  {'-'*5} {'-'*20} {'-'*30}")
            for v in versions:
                ts = v["timestamp"][:19].replace("T", " ")
                print(f"  {v['id']:<5} {ts:<20} {v['message']}")

    elif args.action == "diff":
        versions = tracker.list_versions(args.file)
        v1 = args.v1 or "v1"
        v2 = args.v2 or (versions[-1]["id"] if versions else "v1")
        diff = tracker.diff_versions(v1, v2, args.file)
        if diff:
            print(f"\n  Comparing {v1} → {v2}")
            print(f"  +{diff['added_count']} -{diff['removed_count']}")
        else:
            log("✗", "Could not compare versions", RED)

    elif args.action == "show":
        vid = args.id or tracker.get_current_version()
        if vid:
            content = tracker.get_version(vid, args.file)
            if content:
                print(f"\n--- {args.file} ({vid}) ---\n")
                print(content[:2000])
        else:
            log("✗", "No version specified", RED)

    elif args.action == "restore":
        if not args.id:
            log("✗", "Specify version with --id", RED)
            return 1
        if tracker.restore_version(args.id, args.file):
            log("✓", f"Restored {args.file} to {args.id}", GREEN)
        else:
            log("✗", f"Could not restore {args.id}", RED)

    return 0


def cmd_validate(args):
    """Validate source materials and configuration."""
    print(f"\n{BOLD}Validating Source Materials{RESET}\n")

    errors = 0
    warnings = 0

    # Check identity.json
    if not IDENTITY_JSON.exists():
        log("✗", "identity.json not found", RED)
        errors += 1
    else:
        try:
            identity = json.loads(IDENTITY_JSON.read_text())
            required = ["full_name", "email", "phone", "location"]
            for field in required:
                val = identity.get(field, "")
                if not val or val.startswith("Your") or val.startswith("your"):
                    log("⚠", f"identity.json: '{field}' needs to be set", YELLOW)
                    warnings += 1
                else:
                    log("✓", f"identity.json: '{field}' ✓", GREEN)
        except json.JSONDecodeError as e:
            log("✗", f"identity.json: Invalid JSON - {e}", RED)
            errors += 1

    # Check master_experience.md
    if not MASTER_EXP.exists():
        log("✗", "master_experience.md not found", RED)
        errors += 1
    else:
        content = MASTER_EXP.read_text()
        if "[Company Name]" in content:
            log("⚠", "master_experience.md: Contains template placeholders", YELLOW)
            warnings += 1
        else:
            log("✓", "master_experience.md: Exists", GREEN)

    # Check templates
    templates = ROOT / "templates"
    for tmpl in ["style.tex", "minimal.tex", "creative.tex", "executive.tex", "cover_letter_style.tex"]:
        if (templates / tmpl).exists():
            log("✓", f"templates/{tmpl}: Exists", GREEN)
        else:
            log("✗", f"templates/{tmpl}: Missing", RED)
            errors += 1

    # Summary
    print(f"\n{BOLD}Summary:{RESET}")
    if errors == 0 and warnings == 0:
        log("✓", "All checks passed!", GREEN)
    else:
        if errors:
            log("✗", f"{errors} error(s)", RED)
        if warnings:
            log("⚠", f"{warnings} warning(s)", YELLOW)

    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(
        prog="career",
        description="Career Architect - Job Application Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # new command
    new_parser = subparsers.add_parser("new", help="Create new application")
    new_parser.add_argument("--company", "-c", help="Company name")
    new_parser.add_argument("--role", "-r", help="Role title")

    # build command
    build_parser = subparsers.add_parser("build", help="Build documents")
    build_parser.add_argument("--all", action="store_true", help="Build all")
    build_parser.add_argument("--application", "-a", help="Specific application")
    build_parser.add_argument(
        "--force", "-f", action="store_true", help="Force rebuild"
    )
    build_parser.add_argument(
        "--formats", default="pdf,docx,txt", help="Output formats"
    )

    # list command
    subparsers.add_parser("list", help="List applications")

    # status command
    subparsers.add_parser("status", help="Show project status")

    # stats command
    subparsers.add_parser("stats", help="Application analytics")

    # validate command
    subparsers.add_parser("validate", help="Validate source materials")

    # ats command
    ats_parser = subparsers.add_parser("ats", help="ATS keyword scoring")
    ats_parser.add_argument("path", nargs="?", help="Application folder")
    ats_parser.add_argument("--json", action="store_true", help="JSON output")

    # version command
    ver_parser = subparsers.add_parser("version", help="Track resume versions")
    ver_parser.add_argument(
        "action",
        nargs="?",
        default="list",
        choices=["save", "list", "diff", "restore", "show"],
        help="Action to perform",
    )
    ver_parser.add_argument("--app", "-a", help="Application folder")
    ver_parser.add_argument("--file", "-f", default="resume.md", help="File")
    ver_parser.add_argument("--message", "-m", help="Version message")
    ver_parser.add_argument("--v1", help="First version for diff")
    ver_parser.add_argument("--v2", help="Second version for diff")
    ver_parser.add_argument(
        "--id", "--version", dest="id", help="Version ID for restore/show"
    )

    # export command
    exp_parser = subparsers.add_parser("export", help="Export to ATS formats")
    exp_parser.add_argument(
        "format",
        nargs="?",
        default="all",
        choices=["txt", "json", "all"],
        help="Export format",
    )
    exp_parser.add_argument("--app", "-a", help="Application folder")
    exp_parser.add_argument("--output", "-o", help="Output directory")

    # batch command
    batch_parser = subparsers.add_parser("batch", help="Batch process JDs")
    batch_parser.add_argument("input", help="Folder with JD files")
    batch_parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Preview only"
    )

    # scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Import from URL")
    scrape_parser.add_argument("url", help="Job posting URL")
    scrape_parser.add_argument(
        "--create", "-c", action="store_true", help="Create application"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "new": cmd_new,
        "build": cmd_build,
        "list": cmd_list,
        "status": cmd_status,
        "stats": cmd_stats,
        "validate": cmd_validate,
        "ats": cmd_ats,
        "version": cmd_version,
        "export": cmd_export,
        "batch": cmd_batch,
        "scrape": cmd_scrape,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
