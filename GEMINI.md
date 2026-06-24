# Career Architect — Gemini Context

This file is read automatically by the Gemini CLI. It provides the same grounding that `CLAUDE.md` provides for Claude Code.

---

## What this repo does

End-to-end job application pipeline. Given a job description, produce a tailored resume, cover letter, interview prep guide, ATS score report, and PDF/DOCX artifacts — all grounded in the user's personal experience lake.

---

## Before doing anything

Always run the setup validator first:

```bash
python scripts/check_setup.py
```

Parse the JSON output. If `ready` is `false`, tell the user what's missing and stop.

| Field | Meaning |
|---|---|
| `identity.ok: false` | `source_materials/identity.json` has placeholder values — ask the user to fill it in |
| `source_materials.ok: false` | No resumes or project docs found — ask the user to add them |
| `experience_lake.ok: false` | `master_experience.md` missing or too sparse — run the lake build |

Only proceed when `ready: true`.

---

## Key files

| File | Purpose |
|---|---|
| `source_materials/identity.json` | Contact info, preferences — **never hallucinate or guess any field** |
| `source_materials/master_experience.md` | Experience lake — single source of truth for resume bullets |
| `.prompts/main_orchestrator.md` | Full pipeline definition — follow every step in order |
| `applications/YYYY-MM-DD-company-role/` | Output folder per application |
| `TRACKER.md` | User's application tracker — update status after each action |

---

## Running the pipeline

When the user asks you to apply to a job or process a JD:

1. Run `python scripts/check_setup.py` — confirm `ready: true`
2. Create the application folder: `python scripts/career.py new --company "<co>" --role "<role>"`
3. Read `source_materials/identity.json` and `source_materials/master_experience.md`
4. Read and follow `.prompts/main_orchestrator.md` exactly — all steps, all quality gates
5. Write outputs to `applications/YYYY-MM-DD-company-role/`
6. Run ATS scoring: `python scripts/ats_score.py applications/<folder>/`
7. Build artifacts: `python scripts/build_resume.py applications/<folder>/resume.md --template <template>`
8. Update `TRACKER.md` with the new row

## Template routing

| Role type | Template |
|---|---|
| engineering, business | `default` (or `executive` for Director+) |
| creative | `creative` |
| healthcare, academic | `minimal` |

---

## Critical rules

1. **Never hallucinate contact info.** Every name, email, phone, and URL must come from `source_materials/identity.json` verbatim.
2. **No H1 headers in `resume.md`.** The build script injects the name/header — an H1 breaks the PDF.
3. **YAML frontmatter required** on every generated document (`company`, `role`, `date`, `status`).
4. **ATS gate:** if `ats_score.py` returns <50%, revise the resume before building artifacts.
5. **Role boundaries:** use only the prompts from the detected `role_category` directory — never mix frameworks.

---

## Available scripts

```bash
python scripts/check_setup.py                           # setup validator, exit 0 = ready
python scripts/career.py new --company X --role Y       # create application folder
python scripts/career.py list                           # list all applications
python scripts/career.py status                         # application status summary
python scripts/build_resume.py <folder>/resume.md       # build PDF/DOCX/TXT
python scripts/ats_score.py <folder>/                   # ATS keyword score
python scripts/export_resume.py all <folder>            # TXT + JSON Resume export
```
