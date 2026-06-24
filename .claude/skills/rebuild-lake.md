---
name: rebuild-lake
description: Rebuild the experience lake (master_experience.md) from scratch using all current source materials. Use when the user has added new resumes or projects since initial setup, changed jobs, or wants to refresh their experience lake with updated content.
---

Re-run the experience lake build step from `/career:setup` without touching identity or preferences.

## What to do

1. Run `python scripts/check_setup.py` and parse the JSON output.
   - If identity is not set up (`identity.ok: false`), stop and redirect to `/career:setup`.
   - If no source materials exist (`source_materials.ok: false`), stop and say:
     > "No source materials found. Add your resumes and project docs to `source_materials/resumes/` or `source_materials/projects/` first, then run `/career:rebuild-lake` again."
   - If source materials exist, proceed even if `experience_lake.ok` is false (that's why we're here).

2. List what will be processed — show the user all source files found:
   ```
   Found X source files:
   - source_materials/resumes/your-file.md
   - source_materials/projects/your-project.md
   ...
   ```
   Ask: "Ready to rebuild your experience lake from these files? (yes/no)"

3. On confirmation, read ALL source material files:
   - All `.md` files in `source_materials/resumes/` (excluding README.md)
   - All `.md` files in `source_materials/projects/` (excluding README.md)
   - Any `.md` or `.txt` files directly in `source_materials/` (excluding `master_experience.md` and README.md)

4. If the user mentioned adding NEW materials since last setup, ask them to paste or provide the new content now before rebuilding.

5. Execute `.prompts/core/setup.md` in full — the extraction and structuring protocol.

6. **IMPORTANT**: Save the output to `source_materials/master_experience.md`, overwriting the previous version.

7. Run `python scripts/check_setup.py` to confirm the rebuilt lake passes validation.

8. Report:
   > "✅ Experience lake rebuilt — X lines across Y roles/projects extracted from Z source files.
   >
   > Your next application will draw from this updated knowledge base. Run `/career:tailor` to apply to a job."

## When to use this vs `/career:setup`
- `/career:setup` — first-time onboarding or if identity/source materials are also missing
- `/career:rebuild-lake` — you already have a working setup and just added new experience (new job, new project, new resume version)

## Args
Optional file path or description of new material to incorporate, e.g. `/rebuild-lake I just added my 2025 resume`.
