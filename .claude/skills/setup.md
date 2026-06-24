---
name: setup
description: First-time onboarding for Career Architect. Guides the user through all required setup steps — filling out identity.json, adding source materials (resumes, project docs), and building the experience lake. Must be completed before any other skill will work. Use when the user is new, when setup validation fails, or when they explicitly ask to set up Career Architect.
---

Run `python scripts/check_setup.py` to check current setup status, then guide the user through any incomplete steps.

## Setup Steps (execute in order, skip completed ones)

### Step 1 — Identity (`source_materials/identity.json`)

Check if `identity.json` has real values (not placeholders like "Your Name").

If incomplete:
1. Read the current `source_materials/identity.json` to show the user what fields need filling.
2. Ask the user for each missing field interactively:
   - Full name
   - Email address
   - Phone number (with country code)
   - Location (City, Country)
   - LinkedIn URL (optional but recommended)
   - GitHub URL (optional)
   - Portfolio URL (optional)
3. Ask about preferences:
   - Preferred resume style: `modern_builder` (default), `traditional`, `academic`, or `creative`
   - Preferred tone: `professional` (default), `conversational`, or `formal`
4. Ask about logistics (used for application questions):
   - Salary expectation and currency
   - Notice period
   - Work authorization / visa status
   - Remote/hybrid/onsite preference
5. Write the completed values to `source_materials/identity.json`, preserving the existing structure and all unchanged fields.
6. Confirm: "✅ Identity saved."

### Step 2 — Source Materials

Check `source_materials/resumes/` and `source_materials/projects/` for `.md` files with real content (not just README.md).

If no source materials found:
1. Explain: "I need your existing experience to build your personal knowledge base. Please add your source materials in one of these ways:"
2. Show the user their options:

   **Option A — Paste directly** (fastest):
   > "Just paste your resume text here — I'll save it as `source_materials/resumes/my-resume.md` for you."

   **Option B — File path**:
   > "If you have a resume file already, tell me the path and I'll read it."

   **Option C — Multiple files**:
   > "If you have multiple resumes or project docs, paste them one at a time and tell me what each one is."

3. For each piece of content the user provides, save it to:
   - Resumes → `source_materials/resumes/YYYY-descriptive-name.md`
   - Projects → `source_materials/projects/project-name.md`
   - General experience docs → `source_materials/YYYY-descriptive-name.md`
4. Confirm each save: "✅ Saved to source_materials/resumes/your-file.md"
5. Keep asking "Anything else to add?" until the user says no.

### Step 3 — Build the Experience Lake

Check if `source_materials/master_experience.md` exists with real content (≥20 non-empty lines, no placeholders).

If missing or sparse:
1. Announce: "Now I'll read all your source materials and build your personal experience lake — a comprehensive `master_experience.md` that every future application will draw from."
2. Read ALL files from:
   - `source_materials/resumes/` (all .md files, excluding README.md)
   - `source_materials/projects/` (all .md files, excluding README.md)
   - Any other .md or .txt files directly in `source_materials/`
3. Execute `.prompts/core/setup.md` in full — this is the extraction protocol.
4. The output MUST be saved to `source_materials/master_experience.md`.
5. After saving, run `python scripts/check_setup.py` to confirm the experience lake passes validation.
6. Report: "✅ Experience lake built — X lines across Y roles/projects."

### Step 4 — Final Validation

Run `python scripts/check_setup.py` and parse the JSON output.

If `ready: true`:
> "🎉 Career Architect is fully set up!
>
> You're ready to apply. Next steps:
> - `/career:tailor` — paste a job description to generate a full application
> - `/career:analyze` — evaluate a JD before committing to a full application
> - `/career:interview-prep` — prepare for an upcoming interview"

If any step still fails, show what remains and offer to fix it immediately.

## Args
Optional. If the user passes a specific step number (e.g., `/setup 2`), jump directly to that step.
