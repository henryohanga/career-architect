#!/usr/bin/env python3
"""Export Resume - Convert resumes to ATS-friendly formats.

Supported formats:
- TXT: Plain text, ATS-optimized
- JSON Resume: Standard JSON Resume schema (https://jsonresume.org)
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICATIONS_DIR = ROOT / "applications"
SOURCE_DIR = ROOT / "source_materials"
IDENTITY_JSON = SOURCE_DIR / "identity.json"


def load_identity() -> dict:
    """Load identity.json if it exists."""
    if IDENTITY_JSON.exists():
        try:
            return json.loads(IDENTITY_JSON.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"\033[93m⚠\033[0m Could not read identity.json: {e}", file=sys.stderr)
    return {}


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    # Remove headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    # Remove links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove code blocks
    text = re.sub(r"```[^`]*```", "", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove horizontal rules
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    # Remove YAML frontmatter
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    # Clean up extra whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def export_txt(resume_path: Path, output_path: Path) -> bool:
    """Export resume to plain text format.

    Args:
        resume_path: Path to resume.md
        output_path: Path for output .txt file

    Returns:
        True if successful
    """
    if not resume_path.exists():
        return False

    content = resume_path.read_text(encoding="utf-8")
    plain_text = strip_markdown(content)

    # Add header with contact info
    identity = load_identity()
    header_lines = []
    if identity.get("full_name"):
        header_lines.append(identity["full_name"].upper())
    if identity.get("email"):
        header_lines.append(identity["email"])
    if identity.get("phone"):
        header_lines.append(identity["phone"])
    if identity.get("location"):
        header_lines.append(identity["location"])
    if identity.get("linkedin"):
        header_lines.append(identity["linkedin"])

    if header_lines:
        header = "\n".join(header_lines) + "\n\n" + "=" * 50 + "\n\n"
        plain_text = header + plain_text

    output_path.write_text(plain_text, encoding="utf-8")
    return True


def parse_resume_sections(content: str) -> dict:
    """Parse resume markdown into sections."""
    sections = {
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
    }

    # Remove frontmatter
    content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)

    # Split by headers
    current_section = None
    current_content = []

    for line in content.split("\n"):
        header_match = re.match(r"^##?\s+(.+)$", line)
        if header_match:
            # Save previous section
            if current_section and current_content:
                section_text = "\n".join(current_content)
                if "summary" in current_section.lower():
                    sections["summary"] = strip_markdown(section_text)
                elif "experience" in current_section.lower():
                    sections["experience"] = parse_experience(section_text)
                elif "education" in current_section.lower():
                    sections["education"] = parse_education(section_text)
                elif "skill" in current_section.lower():
                    sections["skills"] = parse_skills(section_text)
                elif "project" in current_section.lower():
                    sections["projects"] = parse_projects(section_text)

            current_section = header_match.group(1)
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_section and current_content:
        section_text = "\n".join(current_content)
        if "experience" in current_section.lower():
            sections["experience"] = parse_experience(section_text)

    return sections


def parse_experience(text: str) -> list:
    """Parse experience section into structured data."""
    experiences = []
    # Split by company headers (### Company)
    parts = re.split(r"^###\s+", text, flags=re.MULTILINE)

    for part in parts[1:]:  # Skip first empty part
        lines = part.strip().split("\n")
        if not lines:
            continue

        exp = {
            "company": "",
            "position": "",
            "startDate": "",
            "endDate": "",
            "summary": "",
            "highlights": [],
        }

        # First line is company name
        exp["company"] = strip_markdown(lines[0])

        # Look for role and dates
        for line in lines[1:]:
            if line.startswith("**") or line.startswith("*"):
                # Role line
                role_match = re.search(r"\*\*([^*]+)\*\*", line)
                if role_match:
                    exp["position"] = role_match.group(1)
                # Date range
                date_match = re.search(r"\(([^)]+)\)", line)
                if date_match:
                    dates = date_match.group(1)
                    if " - " in dates:
                        start, end = dates.split(" - ", 1)
                        exp["startDate"] = start.strip()
                        exp["endDate"] = end.strip()
            elif line.startswith("- "):
                exp["highlights"].append(strip_markdown(line[2:]))

        if exp["company"]:
            experiences.append(exp)

    return experiences


def parse_education(text: str) -> list:
    """Parse education section.

    Expects the same convention as experience:
        ### Institution
        **Degree, Field** (2015 - 2019)
    """
    education = []
    lines = text.strip().split("\n")

    current_edu = None
    for line in lines:
        if line.startswith("###"):
            if current_edu:
                education.append(current_edu)
            current_edu = {
                "institution": strip_markdown(line.lstrip("# ")),
                "area": "",
                "studyType": "",
                "startDate": "",
                "endDate": "",
            }
        elif current_edu and line.strip():
            degree_match = re.search(r"\*\*([^*]+)\*\*", line)
            if degree_match and not current_edu["studyType"]:
                degree = degree_match.group(1)
                if "," in degree:
                    study_type, area = degree.split(",", 1)
                    current_edu["studyType"] = study_type.strip()
                    current_edu["area"] = area.strip()
                else:
                    current_edu["studyType"] = degree.strip()
            date_match = re.search(r"\(([^)]+)\)", line)
            if date_match and not current_edu["startDate"]:
                dates = date_match.group(1)
                if " - " in dates:
                    start, end = dates.split(" - ", 1)
                    current_edu["startDate"] = start.strip()
                    current_edu["endDate"] = end.strip()
                else:
                    current_edu["endDate"] = dates.strip()

    if current_edu:
        education.append(current_edu)

    return education


def parse_skills(text: str) -> list:
    """Parse skills section."""
    skills = []
    lines = text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if line.startswith("- "):
            # Could be "- **Category**: skill1, skill2"
            if ":" in line:
                parts = line[2:].split(":", 1)
                name = strip_markdown(parts[0])
                keywords = [k.strip() for k in parts[1].split(",")]
                skills.append({"name": name, "keywords": keywords})
            else:
                name = strip_markdown(line[2:])
                skills.append({"name": name, "keywords": []})

    return skills


def parse_projects(text: str) -> list:
    """Parse projects section."""
    projects = []
    parts = re.split(r"^###\s+", text, flags=re.MULTILINE)

    for part in parts[1:]:
        lines = part.strip().split("\n")
        if not lines:
            continue

        project = {
            "name": strip_markdown(lines[0]),
            "description": "",
            "highlights": [],
            "keywords": [],
        }

        for line in lines[1:]:
            if line.startswith("- "):
                project["highlights"].append(strip_markdown(line[2:]))
            elif line.strip() and not project["description"]:
                project["description"] = strip_markdown(line)

        if project["name"]:
            projects.append(project)

    return projects


def export_json_resume(resume_path: Path, output_path: Path) -> bool:
    """Export resume to JSON Resume format.

    Args:
        resume_path: Path to resume.md
        output_path: Path for output .json file

    Returns:
        True if successful
    """
    if not resume_path.exists():
        return False

    content = resume_path.read_text(encoding="utf-8")
    identity = load_identity()
    sections = parse_resume_sections(content)

    # Build JSON Resume schema
    json_resume = {
        "$schema": "https://jsonresume.org/schema",
        "basics": {
            "name": identity.get("full_name", ""),
            "label": "",
            "email": identity.get("email", ""),
            "phone": identity.get("phone", ""),
            "url": identity.get("github", ""),
            "summary": sections.get("summary", ""),
            "location": {
                "city": identity.get("location", "").split(",")[0].strip(),
                "countryCode": "",
                "region": "",
            },
            "profiles": [],
        },
        "work": sections.get("experience", []),
        "education": sections.get("education", []),
        "skills": sections.get("skills", []),
        "projects": sections.get("projects", []),
        "meta": {
            "version": "v1.0.0",
            "lastModified": datetime.now().isoformat(),
            "canonical": "https://jsonresume.org/schema",
        },
    }

    # Add profiles
    if identity.get("linkedin"):
        json_resume["basics"]["profiles"].append(
            {"network": "LinkedIn", "url": identity["linkedin"]}
        )
    if identity.get("github"):
        json_resume["basics"]["profiles"].append(
            {"network": "GitHub", "url": identity["github"]}
        )

    output_path.write_text(
        json.dumps(json_resume, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return True


def find_latest_application() -> Path:
    """Find the most recently modified application folder."""
    if not APPLICATIONS_DIR.exists():
        return None

    apps = [
        d
        for d in APPLICATIONS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]

    if not apps:
        return None

    return max(apps, key=lambda p: p.stat().st_mtime)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Export resume to ATS-friendly formats"
    )
    parser.add_argument(
        "format",
        choices=["txt", "json", "all"],
        help="Export format",
    )
    parser.add_argument(
        "app", nargs="?", help="Application folder (default: most recent)"
    )
    parser.add_argument(
        "--output", "-o", help="Output directory (default: application folder)"
    )

    args = parser.parse_args()

    # Find application
    if args.app:
        app_path = APPLICATIONS_DIR / args.app
        if not app_path.exists():
            app_path = Path(args.app)
    else:
        app_path = find_latest_application()

    if not app_path or not app_path.exists():
        print("\033[91m✗\033[0m No application found")
        return 1

    resume_path = app_path / "resume.md"
    if not resume_path.exists():
        print(f"\033[91m✗\033[0m No resume.md found in {app_path.name}")
        return 1

    output_dir = Path(args.output) if args.output else app_path
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\033[94mℹ\033[0m Exporting from: {app_path.name}")

    success = True
    if args.format in ("txt", "all"):
        txt_path = output_dir / "resume.txt"
        if export_txt(resume_path, txt_path):
            print(f"\033[92m✓\033[0m Created: {txt_path.name}")
        else:
            print("\033[91m✗\033[0m Failed to create TXT")
            success = False

    if args.format in ("json", "all"):
        json_path = output_dir / "resume.json"
        if export_json_resume(resume_path, json_path):
            print(f"\033[92m✓\033[0m Created: {json_path.name}")
        else:
            print("\033[91m✗\033[0m Failed to create JSON")
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
