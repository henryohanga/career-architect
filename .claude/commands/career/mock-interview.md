---
description: Run a live mock interview session with per-answer coaching
argument-hint: [company/role or folder] [mode number]
---

## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, **stop** and tell the user:
  > "Career Architect isn't set up yet. Run `/career:setup` — it takes about 5 minutes."
  List the specific issues from the JSON.

Only proceed past this gate if `ready: true`.

---

Run a live mock interview session using `.prompts/core/mock_interview.md`.

## What to do

1. Identify the target role:
   - If args include a company/role name or folder path, load that application's `job_desc.md`, `resume.md`, and `interview_prep.md`.
   - If no args, use the most recent application folder.
   - If no application exists, ask: "Which role are you interviewing for?"

2. Ask the user to choose an interview mode:
   > "Which type of interview do you want to practice?
   > 1. Technical Deep Dive — system design, architecture, coding
   > 2. Behavioural Round — leadership, conflict, growth stories
   > 3. Executive / Final Round — vision, strategy, culture fit
   > 4. Full Loop Simulation — realistic mix of all types"

3. Execute `.prompts/core/mock_interview.md` with the selected mode.

4. Run the interview as follows:
   - Ask one question at a time — do NOT present all questions upfront
   - Wait for the user's answer before continuing
   - After each answer, give structured feedback:
     - **What landed**: what was strong
     - **What to sharpen**: one specific improvement
     - **STAR score**: Situation / Action / Result completeness (e.g. "strong S, weak R — add the business outcome")
   - Move to the next question only after feedback is acknowledged

5. After all questions (typically 5–8), give a **session summary**:
   - Top 3 strengths demonstrated
   - Top 2 areas to practise before the real interview
   - One STAR story that needs more metric grounding

6. Ask: "Want to retry any question, or run another round?"

## Rules
- Stay in character as the interviewer — don't break the roleplay to explain what you're about to ask
- Never reveal all questions at once
- Adapt follow-up questions based on the user's answers (probe weak spots)

## Args
Company/role name or folder path, optionally with mode number, e.g. `/career:mock-interview stripe 2` for a behavioural round for the Stripe application.
