## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/career:setup` — it takes about 5 minutes."
  List the specific issues from the JSON.

Only proceed past this gate if `ready: true`.

---

Rebuild PDF, DOCX, and TXT artifacts for an existing application without regenerating the resume or cover letter content.

Use this when:
- You updated `source_materials/identity.json` and need the header to re-render
- You edited `resume.md` or `cover_letter.md` manually and need fresh PDFs
- You want to switch templates (`default`, `minimal`, `creative`, `executive`)
- A previous build failed and you want to retry

## What to do

1. Identify the target application folder:
   - If args include a company/role name or folder path, find the matching folder under `applications/`.
   - If there is only one folder, use it.
   - If ambiguous, list available folders and ask the user to pick.
   - If no args and multiple folders exist, use the most recently modified one and confirm with the user.

2. Check that `resume.md` exists in the folder. If it doesn't, tell the user:
   > "No resume.md found in `applications/<folder>/`. Run `/career:tailor` to generate one first."

3. Determine the template to use:
   - If args include a template name (`default`, `minimal`, `creative`, `executive`), use it.
   - Otherwise use the preference from `source_materials/identity.json → preferences.template`.
   - Default to `default` if not set.

4. Run the build for `resume.md`:
   ```bash
   python scripts/build_resume.py applications/<folder>/resume.md --template <template>
   ```

5. If `cover_letter.md` exists in the folder, rebuild it too:
   ```bash
   python scripts/build_resume.py applications/<folder>/cover_letter.md
   ```

6. Run ATS score to confirm nothing regressed:
   ```bash
   python scripts/ats_score.py applications/<folder>/
   ```

7. Report the results:

   ```
   ## Artifacts rebuilt: applications/<folder>/

   | File              | Size   | Status   |
   |-------------------|--------|----------|
   | resume.pdf        | X KB   | ✅ Ready |
   | resume.docx       | X KB   | ✅ Ready |
   | resume.txt        | X KB   | ✅ Ready |
   | cover_letter.pdf  | X KB   | ✅ Ready |

   Template: default | ATS score: 78%
   ```

   If any build fails, show the full error output so the user can diagnose.

## Args

Optional folder name, company/role, or template override, e.g.:
- `/career:rebuild` — rebuilds the most recent application
- `/career:rebuild stripe` — rebuilds the Stripe application folder
- `/career:rebuild stripe executive` — rebuilds with the executive template
- `/career:rebuild --template minimal` — rebuilds most recent with minimal template
