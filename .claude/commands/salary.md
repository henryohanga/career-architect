## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/setup` first — it only takes about 5 minutes."
  List the specific issues from the JSON.

Only proceed past this gate if `ready: true`.

---

Execute `.prompts/core/salary_negotiation.md` with context from the job and identity.

## What to do

1. Identify the role:
   - If args include company/role or a folder path, load `job_desc.md` for salary range, company size, and location.
   - Otherwise ask: "Which role and company? And what's your current/target salary range?"
2. Read `source_materials/identity.json` for `logistics.salary_expectation`, `logistics.salary_currency`, and `logistics.salary_notes`.
3. Execute `.prompts/core/salary_negotiation.md`.
4. Output a structured negotiation brief:
   - **Market range** (based on role, location, company tier)
   - **Your anchor number** (the first number to say — 10–15% above midpoint)
   - **Walk-away floor** (do not disclose — internal reference only)
   - **3 negotiation talking points** (value-based, not need-based)
   - **Counter-offer script** (what to say if they low-ball)
   - **Benefits to negotiate** if cash is fixed (equity, PTO, remote, signing bonus)
5. Save to `applications/<folder>/salary_brief.md` if a folder exists.

## Args
Company/role name, folder path, or salary range, e.g. `/salary Stripe Senior Engineer 150k-180k`.
