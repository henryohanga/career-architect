## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/career:setup` to complete the one-time onboarding. It takes about 5 minutes."
  List the specific issues from the JSON.

Only proceed past this gate if `ready: true`.

---

Run ATS scoring via `scripts/ats_score.py` and interpret the results.

## What to do

1. Identify the application folder (same logic as `/career:cover-letter`).
2. Run: `python scripts/ats_score.py applications/<folder>/`
3. Parse the output score and keyword report.
4. If score ≥ 70%: "✅ Strong ATS coverage ({score}%). Ready to submit."
5. If score 50–69%: "⚠️ Acceptable ({score}%) but these keywords are missing: [list]. Add them to the resume skills or summary section."
6. If score < 50%: "❌ Below threshold ({score}%). The resume needs these keywords before submitting: [list]. Run `/career:tailor` to regenerate or manually add the keywords."
7. Offer to patch the resume if score is below 70%: "Want me to add the missing keywords to `resume.md` and rebuild the PDF?"

## Args
Folder name or company/role slug. If no args, auto-detect the most recent application folder.
