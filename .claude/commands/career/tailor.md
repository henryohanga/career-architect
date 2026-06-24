## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/career:setup` to complete the one-time onboarding (fills out your identity, adds your source materials, and builds your experience lake). It takes about 5 minutes."
  Then list the specific issues from the JSON so they know exactly what's missing.

Only proceed past this gate if `ready: true`.

---

Execute the full Career Architect pipeline from `.prompts/main_orchestrator.md`.

## What to do

1. If the user provided a JD as text, that is the job description. If they provided a file path, read it.
2. If no JD was provided, ask: "Please paste the job description."
3. Execute `.prompts/main_orchestrator.md` exactly — all steps, all quality gates.
4. At **Step 1** (after the Strategic Match Report), pause and wait for the user to say "GO" before continuing to generation.
5. Report the output folder path and ATS score when done.
6. Add a row to `TRACKER.md` under **Active** with status `📤`, the ATS score, and the folder path. If the user hasn't submitted yet (still drafting), use `🟡`.

## Args
The user may pass the JD inline as the skill argument, e.g. `/tailor <JD text or file path>`.
If args are present, treat them as the job description input and proceed without asking.
