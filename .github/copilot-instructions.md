# Career Architect — GitHub Copilot Instructions

This file is loaded automatically by GitHub Copilot agent mode. It tells Copilot how to work with this repository.

---

## What this repo does

Career Architect is an AI-powered job application pipeline. Given a job description, it generates a tailored resume, cover letter, interview prep guide, ATS keyword score, and PDF/DOCX artifacts — all drawn from the user's personal experience lake.

---

## Setup check (always run first)

Before any generation task, confirm the repo is set up:

```bash
python scripts/check_setup.py
```

Returns JSON. Proceed only if `ready: true`. If not, tell the user exactly which step is missing.

---

## Core workflow

When the user asks to apply to a role or process a job description:

```bash
# 1. Validate setup
python scripts/check_setup.py

# 2. Create application folder
python scripts/career.py new --company "Company" --role "Role Title"

# 3. Save job description to the folder as job_desc.md with YAML frontmatter

# 4. Follow .prompts/main_orchestrator.md — read it and execute every step

# 5. Run ATS scoring
python scripts/ats_score.py applications/<folder>/

# 6. Build artifacts (only if ATS ≥ 50%)
python scripts/build_resume.py applications/<folder>/resume.md --template <template>
python scripts/build_resume.py applications/<folder>/cover_letter.md

# 7. Update TRACKER.md with the new application row
```

---

## Source of truth files

| File | Rule |
|---|---|
| `source_materials/identity.json` | **Never guess or hallucinate any field.** Use verbatim. |
| `source_materials/master_experience.md` | Only source for resume bullets. Never invent experience. |
| `.prompts/main_orchestrator.md` | The pipeline definition. Follow it exactly. |
| `TRACKER.md` | Update after every application action. |

---

## Resume.md rules

- **No H1 headers** (`# Name`) — the build script injects the header from `identity.json`
- **No contact info** in the markdown body — same reason
- **YAML frontmatter required**: `company`, `role`, `date`, `status`
- **Sections use H2** (`## Summary`, `## Experience`, etc.)
- **ATS gate**: do not build PDF if score < 50%

---

## Template selection

| Role | Template |
|---|---|
| Software, Data, DevOps | `default` |
| Director, VP, C-level | `executive` |
| Design, Creative, Brand | `creative` |
| Healthcare, Academic | `minimal` |

---

## Key scripts

```bash
python scripts/check_setup.py          # → JSON, exit 0 = ready
python scripts/career.py status        # → application status list
python scripts/career.py stats         # → analytics summary
python scripts/ats_score.py <folder>/  # → keyword match %
python scripts/build_resume.py <md>    # → PDF + DOCX + TXT
```
