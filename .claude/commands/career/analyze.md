---
description: Analyse a job description against your experience lake and produce a strategic match report
argument-hint: <JD text or file path>
---

## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/career:setup` to complete the one-time onboarding. It takes about 5 minutes."
  List the specific issues from the JSON.

Only proceed past this gate if `ready: true`.

---

Perform Steps 0–1 of the Career Architect pipeline only (analysis, no generation).

## What to do

1. If the user provided a JD as text or file path, use it. Otherwise ask: "Please paste the job description."
2. Read `source_materials/identity.json` for preferences.
3. Read `source_materials/master_experience.md` for experience data.
4. Create `applications/YYYY-MM-DD-company-role/job_desc.md` from the JD with `company`, `role`, and `date` frontmatter (role_detector edits this file's frontmatter; it must exist first).
5. Execute `.prompts/core/role_detector.md` to classify the role.
6. Execute the appropriate analyser from `.prompts/<role_category>/analyser.md`.
7. Execute `.prompts/core/quality_gates.md` (Gate B).
8. Output the Strategic Match Report to the console **and** save it to the same `applications/YYYY-MM-DD-company-role/` folder as `strategic_match_report.md`.
9. End with a clear YES/NO recommendation and top 3 gaps to address.

Do **not** generate a resume or cover letter — stop after the report.

## Args
JD text or file path passed inline, e.g. `/analyze <JD>`.
