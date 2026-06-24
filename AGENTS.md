# Career Architect — Agents SDK & Codex Instructions

This file tells AI agents (OpenAI Codex, Agents SDK, or any tool-calling LLM) how to use Career Architect. It mirrors the role that `CLAUDE.md` plays for Claude Code.

---

## What this repo does

End-to-end job application pipeline. Given a job description, it produces a tailored resume, cover letter, interview prep guide, ATS score report, and PDF/DOCX artifacts — all grounded in the user's personal experience lake (`source_materials/master_experience.md`).

---

## Prerequisites (check before doing anything)

Always run the setup validator first:

```bash
python scripts/check_setup.py
```

Parse the JSON output. If `ready` is `false`, tell the user what's missing and stop:

- `identity.ok: false` → `source_materials/identity.json` has placeholder values. Ask the user to fill it in.
- `source_materials.ok: false` → No resumes or project docs in `source_materials/resumes/` or `source_materials/projects/`. Ask the user to add them.
- `experience_lake.ok: false` → `source_materials/master_experience.md` is missing or too sparse. Run the experience lake build (see below).

Only proceed when `ready: true`.

---

## MCP Tool Interface

If connected via MCP, use these tools directly:

```
list_applications          → survey existing applications
create_application         → create a new folder for a job
get_pipeline_context       → returns the full orchestrator prompt + source material context
run_ats_score              → run keyword scoring on an application folder
build_resume               → build PDF/DOCX from resume.md
update_status              → mark an application applied/interview/offer/rejected
get_prompt                 → load any prompt file by path (e.g. "core/cover_letter.md")
```

### Recommended MCP flow

```
1. create_application(company, role, job_description)
2. get_pipeline_context(folder=<returned folder>)
3. Run the orchestrator prompt from step 2 with the provided source material context
4. Write resume.md and cover_letter.md into the application folder
5. run_ats_score(folder=<folder>)
6. If score ≥ 50%: build_resume(folder=<folder>, template=<detected template>)
7. update_status(folder=<folder>, status="applied") when done
```

---

## File-based Interface (no MCP)

If not using MCP, operate directly on the filesystem.

### Key files

| File | Purpose |
|---|---|
| `source_materials/identity.json` | Contact info, preferences, logistics — **never hallucinate these** |
| `source_materials/master_experience.md` | Experience lake — the only source for resume bullets |
| `.prompts/main_orchestrator.md` | Full pipeline definition — follow this exactly |
| `.prompts/core/setup.md` | Experience lake extraction protocol |
| `applications/YYYY-MM-DD-company-role/` | Output folder per application |

### Running the pipeline

1. Read `source_materials/identity.json` for preferences and contact info
2. Read `source_materials/master_experience.md` for experience data
3. Read `.prompts/main_orchestrator.md` and follow every step in order
4. Write outputs to `applications/YYYY-MM-DD-company-role/`

### Building artifacts

```bash
python scripts/build_resume.py applications/<folder>/resume.md --template <template>
python scripts/build_resume.py applications/<folder>/cover_letter.md
python scripts/ats_score.py applications/<folder>/
```

Templates: `default`, `minimal`, `creative`, `executive`

Template selection by role:
- `engineering`, `business` → `default` (or `executive` for Director+)
- `creative` → `creative`
- `healthcare`, `academic` → `minimal`

---

## Experience Lake Build

If `master_experience.md` is missing or sparse, run this build before any application:

```python
# Pseudocode for agents
source_files = glob("source_materials/resumes/*.md") + glob("source_materials/projects/*.md")
# Filter out README.md files
# Read all source files
# Load and execute .prompts/core/setup.md extraction protocol
# Write result to source_materials/master_experience.md
```

---

## Critical Rules

1. **Never hallucinate contact info.** All names, emails, phones, and URLs must come from `source_materials/identity.json` verbatim.
2. **No H1 headers in resume.md.** The LaTeX template injects the name/header — an H1 will break the PDF.
3. **YAML frontmatter is required** on every generated document (`company`, `role`, `date`, `status`).
4. **ATS gate:** If `ats_score.py` returns <50%, revise the resume before building artifacts.
5. **Never mix role frameworks.** Use only the prompts from the detected `role_category` directory.
6. **Setup gate first, always.** Run `check_setup.py` before any generation step.

---

## Example Agent Session

```
User: Apply to this job at Stripe as a Senior Backend Engineer. [JD text]

Agent:
1. python scripts/check_setup.py  → ready: true ✅
2. create_application("Stripe", "Senior Backend Engineer", "<JD text>")
   → folder: 2026-06-24-stripe-senior-backend-engineer
3. get_pipeline_context(folder="2026-06-24-stripe-senior-backend-engineer")
   → returns orchestrator + identity + master_experience
4. Execute orchestrator:
   - Detect role: engineering
   - Run .prompts/engineering/analyser.md → strategic_match_report.md
   - Pause: present Strategic Match Report, wait for "GO"
   - Run .prompts/engineering/tailor_resume.md → resume.md
   - Run .prompts/core/cover_letter.md → cover_letter.md
5. run_ats_score("2026-06-24-stripe-senior-backend-engineer") → 78% ⚠️
6. Add missing keywords to resume.md, re-score → 84% ✅
7. build_resume(folder="...", template="default")
   → resume.pdf, resume.docx, resume.txt created
8. update_status(folder="...", status="applied")

Done. Artifacts in applications/2026-06-24-stripe-senior-backend-engineer/
```

---

## Folder Output Structure

```
applications/2026-06-24-stripe-senior-backend-engineer/
├── job_desc.md              ← structured JD with YAML frontmatter
├── strategic_match_report.md ← gap analysis
├── resume.md                ← tailored resume (no H1, no contact info)
├── cover_letter.md          ← cover letter
├── interview_prep.md        ← question bank + STAR starters
├── extra_questions.md       ← application form answers (if any)
├── salary_brief.md          ← negotiation guide (if requested)
├── ats_score.txt            ← ATS keyword report
├── resume.pdf
├── resume.docx
├── resume.txt
├── cover_letter.pdf
└── cover_letter.docx
```
