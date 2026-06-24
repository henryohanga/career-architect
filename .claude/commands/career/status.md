## Setup gate (run first, every time)

Run `python scripts/check_setup.py` and parse the JSON output.

- If exit code is non-zero or `ready` is false, surface the specific issues and tell the user:
  > "Career Architect isn't fully set up yet. Run `/career:setup` to complete the one-time onboarding."

Unlike other commands, do **not** stop here — continue to render the dashboard even if setup is incomplete, so the user can see exactly what's missing.

---

## What to do

Run `python scripts/career.py status` and `python scripts/check_setup.py`, then render a comprehensive dashboard.

1. Run both commands and capture output:
   ```bash
   python scripts/check_setup.py
   python scripts/career.py status
   python scripts/career.py stats
   ```

2. Render the dashboard in this format:

---

**Setup Health**
| Component | Status |
|---|---|
| Identity | ✅ Jane Smith / jane@email.com |
| Source materials | ✅ 4 files |
| Experience lake | ✅ 312 lines |

**Applications** _(sorted by date, most recent first)_
| Date | Company | Role | Status | Resume | Cover | PDF | ATS |
|---|---|---|---|---|---|---|---|
| 2026-06-24 | Stripe | Senior Engineer | 🔵 interview | ✅ | ✅ | ✅ | 84% |
| 2026-06-20 | Notion | Staff Engineer | 🟢 applied | ✅ | ✅ | ✅ | 71% |
| 2026-06-15 | Linear | Engineering Lead | 🟡 draft | ✅ | ❌ | ❌ | — |

**Status key:** 🟡 draft · 🟢 applied · 🔵 interview · ⭐ offer · 🔴 rejected

**Next actions** _(AI-generated based on state)_
- Linear application is a draft — run `/career:cover-letter` to complete it
- Notion application has been in "applied" for 4 days — consider `/career:follow-up`
- Stripe interview stage — run `/career:mock-interview stripe` to prepare

---

3. For the "Next actions" section, look at each application and generate 1 contextual suggestion:
   - `draft` with no cover letter → suggest `/career:cover-letter`
   - `draft` with no PDF → suggest `make build`
   - `applied` for >7 days → suggest `/career:follow-up`
   - `interview` stage → suggest `/career:mock-interview`
   - ATS score <50% → suggest re-running `/career:tailor`

4. End with setup health — if `check_setup.py` returns any issues, surface them prominently.

## Args
No args needed. `/career:status` always shows the full dashboard.
