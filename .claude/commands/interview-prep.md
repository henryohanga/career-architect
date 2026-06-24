## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/setup` to complete the one-time onboarding. It takes about 5 minutes."
  List the specific issues from the JSON.

Only proceed past this gate if `ready: true`.

---

Execute `.prompts/core/role_detector.md` and the appropriate `.prompts/<role_category>/interview_prep.md`.

## What to do

1. Identify the target role:
   - If args include a company/role name or application folder path, use that.
   - If an `applications/` folder exists for the role, load `job_desc.md` from it.
   - Otherwise ask: "Which role and company are you preparing for?"
2. Read `source_materials/master_experience.md` for STAR story material.
3. Detect role category and route to the correct interview prep prompt.
4. Generate the prep guide covering:
   - **Behavioural questions** (5–8, with STAR story starters from the experience lake)
   - **Technical/domain questions** (5–8, specific to the role)
   - **Questions to ask the interviewer** (3–5)
   - **Company research hooks** (2–3 things to know cold)
5. Save to `applications/<folder>/interview_prep.md` if a folder exists, otherwise print to console.

## Args
Company name, role title, or path to an existing application folder, e.g. `/interview-prep Stripe Senior Engineer` or `/interview-prep applications/2026-06-24-stripe-senior-engineer/`.
