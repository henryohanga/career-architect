# Application Tracker

Track every application in one place. Update status as things progress.

**Status key**
| Symbol | Stage |
|---|---|
| 🟡 | Draft — documents in progress |
| 📤 | Applied — submitted, awaiting response |
| 📞 | Screen — recruiter/hiring manager call scheduled or done |
| 🔵 | Interview — active interview rounds |
| ⭐ | Offer — offer received |
| ✅ | Accepted — offer accepted |
| ❌ | Closed — rejected, withdrawn, or expired |

---

## Active

| # | Company | Role | Applied | Status | ATS | Folder | Notes |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | Add your first application with `/career:tailor` |

---

## Pipeline health

Run `/career:status` for a live dashboard with AI-generated next actions.

Quick checks:
```bash
python scripts/career.py stats     # counts by status
python scripts/career.py list      # all folders with document completeness
```

---

## Archive

Move rows here once closed (rejected, withdrawn, accepted and started).

| # | Company | Role | Applied | Closed | Outcome | Folder |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

---

## Notes and patterns

Use this section to capture things you notice across applications — what messaging lands, which roles convert to interviews, salary ranges by company tier, etc.

<!-- Add notes here as you go -->

---

## How to update this file

**When you apply:**
1. Run `/career:tailor` — it creates the application folder automatically
2. Add a row to Active with status `📤` and the ATS score from the output

**When something moves:**
- Update the Status column
- Add a date or note in the Notes column

**When it closes:**
- Move the row to Archive with the outcome and close date

**Quick update via Claude Code:**
```
/career:status   ← generates the full dashboard, including suggested next actions
```
