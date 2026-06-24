## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/career:setup` to complete the one-time onboarding. It takes about 5 minutes."
  List the specific issues from the JSON.

Only proceed past this gate if `ready: true`.

---

Execute `.prompts/core/cover_letter.md` for an existing application.

## What to do

1. Identify the application folder:
   - If args include a folder path or company/role, find the matching folder under `applications/`.
   - If there is only one application folder, use it.
   - If ambiguous, list available folders and ask the user to pick one.
2. Verify `job_desc.md` and `resume.md` exist in the folder. If not, say which is missing and stop.
3. Read `source_materials/identity.json` for tone and style preferences.
4. Execute `.prompts/core/cover_letter.md`.
5. Execute `.prompts/core/quality_gates.md` (Gate D) on the output.
6. Save to `applications/<folder>/cover_letter.md`.
7. Build PDF: `python scripts/build_resume.py applications/<folder>/cover_letter.md`

## Args
Folder name or company/role slug, e.g. `/cover-letter stripe-senior-engineer` or `/cover-letter applications/2026-06-24-stripe-senior-engineer/`.
If no args, auto-detect the most recent application folder.
