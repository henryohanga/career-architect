#!/usr/bin/env python3
"""Career Architect setup validator.

Exit codes:
  0 - fully set up, ready to use
  1 - setup incomplete (identity.json not filled out)
  2 - setup incomplete (no source materials found)
  3 - setup incomplete (master_experience.md missing or empty)

Prints a JSON object to stdout with field-level detail.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY_JSON = ROOT / "source_materials" / "identity.json"
MASTER_EXP = ROOT / "source_materials" / "master_experience.md"
RESUMES_DIR = ROOT / "source_materials" / "resumes"
PROJECTS_DIR = ROOT / "source_materials" / "projects"


def _is_placeholder(value) -> bool:
    """Return True if the value looks like an unfilled placeholder."""
    if value is None or str(value).strip() == "":
        return True
    v = str(value).strip().lower()
    # Catch "Your Name", "your@email.com", "your phone", etc.
    if v.startswith("your"):
        return True
    # Catch "example.com" addresses
    if "example.com" in v or "placeholder" in v:
        return True
    return False


def check() -> dict:
    result = {
        "ready": False,
        "identity": {"ok": False, "issues": []},
        "source_materials": {"ok": False, "issues": [], "files": []},
        "experience_lake": {"ok": False, "issues": []},
    }

    # --- Step 1: identity.json ---
    if not IDENTITY_JSON.exists():
        result["identity"]["issues"].append("identity.json not found")
    else:
        try:
            identity = json.loads(IDENTITY_JSON.read_text())
        except json.JSONDecodeError:
            result["identity"]["issues"].append("identity.json contains invalid JSON")
            identity = {}

        required = {
            "full_name": "Full name",
            "email": "Email address",
            "phone": "Phone number",
            "location": "Location/city",
        }
        for field, label in required.items():
            val = identity.get(field, "")
            if _is_placeholder(val):
                result["identity"]["issues"].append(f"{label} ({field}) is not filled out")

    result["identity"]["ok"] = len(result["identity"]["issues"]) == 0

    # --- Step 2: source materials ---
    source_files = []

    for directory in [RESUMES_DIR, PROJECTS_DIR]:
        if directory.exists():
            for f in directory.glob("*.md"):
                if f.name.lower() != "readme.md":
                    content = f.read_text()
                    if len(content.strip()) > 100:
                        source_files.append(str(f.relative_to(ROOT)))

    # Also accept any .md/.pdf/.txt directly in source_materials/
    for f in ROOT.joinpath("source_materials").glob("*"):
        if f.is_file() and f.suffix in {".md", ".txt", ".pdf"} and f.name not in {
            "master_experience.md", "README.md", "readme.md"
        }:
            if f.stat().st_size > 100:
                source_files.append(str(f.relative_to(ROOT)))

    result["source_materials"]["files"] = source_files
    if not source_files:
        result["source_materials"]["issues"].append(
            "No source materials found. Add your resumes/projects to "
            "source_materials/resumes/ or source_materials/projects/"
        )
    result["source_materials"]["ok"] = len(source_files) > 0

    # --- Step 3: experience lake ---
    if not MASTER_EXP.exists():
        result["experience_lake"]["issues"].append(
            "master_experience.md not found. Run the experience lake setup."
        )
    else:
        content = MASTER_EXP.read_text()
        lines = [ln for ln in content.splitlines() if ln.strip()]
        if len(lines) < 20:
            result["experience_lake"]["issues"].append(
                f"master_experience.md is too sparse ({len(lines)} non-empty lines). "
                "Run setup again with all your source materials."
            )
        elif "[Company Name]" in content or "[Role Title]" in content:
            result["experience_lake"]["issues"].append(
                "master_experience.md still contains template placeholders. "
                "Run the experience lake setup with your real source materials."
            )
        else:
            result["experience_lake"]["ok"] = True

    result["experience_lake"]["ok"] = len(result["experience_lake"]["issues"]) == 0

    result["ready"] = (
        result["identity"]["ok"]
        and result["source_materials"]["ok"]
        and result["experience_lake"]["ok"]
    )

    return result


def main():
    result = check()
    print(json.dumps(result, indent=2))

    if not result["identity"]["ok"]:
        sys.exit(1)
    if not result["source_materials"]["ok"]:
        sys.exit(2)
    if not result["experience_lake"]["ok"]:
        sys.exit(3)
    sys.exit(0)


if __name__ == "__main__":
    main()
