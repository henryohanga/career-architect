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

## First-time setup (required before any skill works)

Run `/career:setup` — it walks through these 4 steps in order:

1. **Fill out identity** — edit `source_materials/identity.json` with your real name, email, phone, location, and job preferences
2. **Add source materials** — paste or drop your existing resumes and project docs into `source_materials/resumes/` and `source_materials/projects/` as `.md` files
3. **Build the experience lake** — Claude reads all source materials and creates `source_materials/master_experience.md`, the single source of truth every application draws from
4. **Done** — from here, just paste a job description and run `/career:tailor`

**Setup check:** `python scripts/check_setup.py` — returns JSON with per-step status and exits 0 only when fully ready. All skills run this automatically and redirect to `/career:setup` if not complete.

## Skills available (slash commands)
| Command | What it does |
|---|---|
| `/career:setup` | One-time onboarding — identity, source materials, experience lake |
| `/career:tailor` | Full pipeline — paste JD, get all artifacts |
| `/career:analyze` | Analyse JD and produce strategic match report |
| `/career:interview-prep` | Generate interview question bank for a role |
| `/career:cover-letter` | Generate cover letter only (resume must exist) |
| `/career:ats-score` | Run ATS keyword scoring on an application folder |
| `/career:salary` | Salary research and negotiation talking points |
| `/career:rebuild-lake` | Refresh experience lake after adding new resumes or projects |

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
