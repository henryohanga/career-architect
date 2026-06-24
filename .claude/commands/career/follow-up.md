## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/career:setup` — it takes about 5 minutes."
  List the specific issues from the JSON.

Only proceed past this gate if `ready: true`.

---

Execute `.prompts/core/follow_up.md` for an existing application.

## What to do

1. Identify the application folder:
   - If args include a folder path or company/role, find the matching folder under `applications/`.
   - If there is only one application folder, use it.
   - If ambiguous, list available folders and ask the user to pick one.

2. Ask the user for context needed to personalise the email:
   - What stage? (after applying / after interview / after silence)
   - Interviewer names (if known)
   - Date of last interaction
   - Anything specific to mention (a topic discussed, a project they mentioned)

3. Read `source_materials/identity.json` for contact info and tone preferences.
4. Read `applications/<folder>/job_desc.md` and `resume.md` for context.
5. Execute `.prompts/core/follow_up.md`.
6. Generate the appropriate email type based on the user's stage:
   - **Application follow-up** — 1 week after applying, no response
   - **Post-interview thank you** — within 24 hours of any interview
   - **Status check** — 2+ weeks of silence after interview
   - **Offer negotiation follow-up** — after receiving an offer
7. Present the email ready to copy-paste. Ask if they want any tone or detail adjustments.
8. Save to `applications/<folder>/follow_up_[type].md`.

## Args
Company/role name, folder path, or context e.g. `/career:follow-up stripe after-interview "spoke with Sarah and James"`.
