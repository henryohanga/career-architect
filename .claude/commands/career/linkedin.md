---
description: Optimise all LinkedIn profile sections for a target role
argument-hint: [target role or industry]
---

## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/career:setup` — it takes about 5 minutes."
  List the specific issues from the JSON.

Only proceed past this gate if `ready: true`.

---

Execute `.prompts/core/linkedin_optimizer.md` to generate optimised LinkedIn profile sections.

## What to do

1. Ask the user for their target direction (if not provided in args):
   - Target role or industry (e.g. "Senior Engineering Manager at a Series B startup")
   - Or: use the most recent application folder's `job_desc.md` as the target

2. Read `source_materials/master_experience.md` for experience data.
3. Read `source_materials/identity.json` for contact info and preferences.
4. If a recent application exists, read its `job_desc.md` to align LinkedIn with the target role.
5. Execute `.prompts/core/linkedin_optimizer.md`.

6. Generate all five sections ready to copy-paste:

   **Headline** (220 chars max)
   > [copy-paste ready]

   **About / Summary** (2,600 chars max)
   > [copy-paste ready]

   **Top 3 Experience Bullet Rewrites** (for the most relevant roles)
   > [copy-paste ready per role]

   **Skills List** (prioritised for target role, top 15)
   > [copy-paste ready]

   **Featured Section Suggestions** (what to pin and why)
   > [suggestions]

7. For each section, explain the key optimisation decision in one line (keyword targeting, recruiter hook, etc.).
8. Ask: "Want me to adjust the tone, length, or focus of any section?"

## Args
Target role or industry, e.g. `/career:linkedin "Staff Engineer at fintech"` or `/career:linkedin` to use the most recent application as the target.
