# Career Architect — Claude Code Context

## What this repo does
End-to-end job application pipeline. Paste a job description → get a tailored resume, cover letter, interview prep, and PDFs. One command: `make build`.

## Key directories
- `source_materials/identity.json` — user contact info and preferences (source of truth)
- `source_materials/master_experience.md` — full experience lake to draw from
- `.prompts/` — modular prompt system, domain-specific (engineering, business, creative, healthcare, academic)
- `applications/YYYY-MM-DD-company-role/` — generated output per application
- `templates/` — LaTeX templates: default, minimal, creative, executive
- `scripts/` — Python scripts: build_resume.py, ats_score.py, career.py, export_resume.py

## Main pipeline (`.prompts/main_orchestrator.md`)
The full pipeline lives in `.prompts/main_orchestrator.md`. When a user says "apply to this job" or pastes a JD, execute that orchestrator end-to-end.

**Short form** — what the orchestrator does:
1. Read `source_materials/identity.json` for preferences/contact info
2. Detect role category (engineering / business / creative / healthcare / academic)
3. Analyse JD against `source_materials/master_experience.md`
4. Generate `resume.md` and `cover_letter.md` in `applications/YYYY-MM-DD-company-role/`
5. Run ATS score check (`python scripts/ats_score.py applications/<folder>/`)
6. Build PDF/DOCX artifacts (`python scripts/build_resume.py applications/<folder>/resume.md`)

## Skills available (slash commands)
| Command | What it does |
|---|---|
| `/tailor` | Full pipeline — paste JD, get all artifacts |
| `/analyze` | Analyse JD and produce strategic match report |
| `/interview-prep` | Generate interview question bank for a role |
| `/cover-letter` | Generate cover letter only (resume must exist) |
| `/ats-score` | Run ATS keyword scoring on an application folder |
| `/salary` | Salary research and negotiation talking points |

## Build commands
```bash
make build          # build all pending applications
make install        # pip install -r requirements.txt
python scripts/career.py validate   # check setup
python scripts/ats_score.py applications/<folder>/
python scripts/build_resume.py applications/<folder>/resume.md --template default
```

## Critical rules
- **Never hallucinate contact info** — always read from `source_materials/identity.json`
- **No H1 headers in resume.md** — LaTeX template handles the name/header
- **YAML frontmatter required** on every generated document
- ATS score must be ≥50% before marking an application ready
