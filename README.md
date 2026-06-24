# Career Architect

> **Paste a job description. Get a tailored resume, cover letter, interview prep, and PDF — in one command.**

Career Architect is an AI-powered job application pipeline you run from your own machine. It learns from your experience once, then generates high-quality, personalised application materials for every role you target — automatically ATS-scored and export-ready.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/henryohanga/career-architect)

---

## How it works

```
Your experience  ──▶  Experience lake  ──▶  Job description  ──▶  Application artifacts
(resumes, projects)    (built once)          (paste any JD)         resume · cover letter
                                                                     interview prep · PDF
```

1. **Setup once** — fill in your identity, drop in your existing resumes and project docs, run `/career:setup`. Career Architect reads everything and builds a rich, structured experience lake.
2. **Apply to anything** — paste a job description and run `/career:tailor`. The pipeline detects the role type, runs gap analysis against your lake, writes tailored documents, scores ATS coverage, and exports PDF/DOCX.
3. **Iterate fast** — every subsequent application takes seconds. The lake grows as your career does.

---

## Getting started

### GitHub Codespaces — zero install

Everything pre-installed. Click, wait 60 seconds, run the setup command.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/henryohanga/career-architect)

```
/career:setup
```

### Claude Code — local

```bash
git clone https://github.com/henryohanga/career-architect.git
cd career-architect
pip install -r requirements.txt
```

Open the folder in Claude Code, then:

```
/career:setup
```

When setup finishes, paste any job description and run:

```
/career:tailor
```

### Docker — no LaTeX install

```bash
git clone https://github.com/henryohanga/career-architect.git
cd career-architect
docker build -t career-architect .
docker run -it -v "$(pwd)":/work career-architect bash
```

Then run any `python scripts/` command or `make` target inside the container.

### Cursor / Windsurf / Claude Desktop — MCP

Clone the repo, install requirements, then open in your editor. The `.mcp.json` file auto-registers the MCP server. Ask your AI assistant:

```
"Set up Career Architect for me"
"Apply to this role at Stripe: <paste JD>"
"Build the PDF artifacts for my Stripe application"
```

See [AGENTS.md](AGENTS.md) for the full MCP tool reference and OpenAI Codex wiring.

### CI only — GitHub Actions

Set up once locally, then push. Every `resume.md` commit triggers a PDF build and ATS score comment on the PR — no local LaTeX required.

---

## First-time setup

Run `/career:setup` — it walks you through each step interactively.

### 1. Identity

Edit `source_materials/identity.json` with your real details. Only `full_name`, `email`, `phone`, and `location` are required. LinkedIn, GitHub, and portfolio are optional — they appear in the PDF header only if provided.

```json
{
  "full_name": "Jane Smith",
  "email": "jane@email.com",
  "phone": "+1 234 567 8901",
  "location": "San Francisco, CA",
  "linkedin": "https://linkedin.com/in/janesmith",
  "github": "https://github.com/janesmith",
  "portfolio": "",
  "preferences": {
    "template": "default",
    "tone": "professional"
  },
  "logistics": {
    "salary_expectation": "150000",
    "salary_currency": "USD",
    "notice_period": "2 weeks",
    "work_authorization": "US Citizen",
    "remote_preference": "hybrid"
  }
}
```

### 2. Source materials

Drop your existing resumes and project docs into:

```
source_materials/
├── resumes/
│   ├── google-2024.md         ← paste raw resume text, any format
│   └── startup-2022.md
└── projects/
    ├── payment-system.md      ← describe what you built + metrics
    └── ml-pipeline.md
```

Markdown is preferred but plain text works too. The AI extracts structure, metrics, and achievements — don't worry about formatting.

### 3. Build the experience lake

`/career:setup` does this automatically. It reads everything in `source_materials/` and writes `source_materials/master_experience.md` — a structured, metrics-rich knowledge base that every future application draws from.

Check status any time:

```bash
python scripts/check_setup.py   # JSON output, exit 0 = ready
make validate                   # Human-readable output
```

### 4. Apply

```
/career:tailor
```

Paste a job description when prompted. The pipeline runs end-to-end and produces everything in `applications/YYYY-MM-DD-company-role/`.

---

## Commands

All commands run a setup gate and redirect to `/career:setup` if anything is missing.

| Command | What it does |
|---|---|
| `/career:setup` | One-time onboarding — identity, source materials, experience lake |
| `/career:tailor` | Full pipeline: JD → resume + cover letter + interview prep + PDF |
| `/career:analyze` | Analyse a JD and produce a strategic match report, no generation |
| `/career:interview-prep` | Tailored question bank and STAR story starters |
| `/career:cover-letter` | Write or regenerate a cover letter for an existing application |
| `/career:ats-score` | Run ATS keyword scoring — ≥70% strong, 50–69% acceptable, <50% revise |
| `/career:salary` | Market salary research and negotiation talking points |
| `/career:rebuild-lake` | Refresh the experience lake after adding new source materials |
| `/career:rebuild` | Regenerate PDF/DOCX from existing markdown — no content changes |
| `/career:follow-up` | Draft a post-application or post-interview follow-up email |
| `/career:linkedin` | Rewrite every LinkedIn section optimised for a target role |
| `/career:mock-interview` | Live mock interview — one question at a time, per-answer STAR feedback |
| `/career:status` | Application dashboard with AI-generated next actions |

---

## MCP tools

When connected as an MCP server, these tools are available to any compatible AI:

| Tool | Description |
|---|---|
| `list_applications` | List all applications with status and document completeness |
| `create_application` | Create a new application folder and save the job description |
| `get_pipeline_context` | Return the orchestrator prompt and source material context |
| `run_ats_score` | Run ATS keyword scoring on an application folder |
| `build_resume` | Build PDF and DOCX artifacts from resume.md |
| `update_status` | Update application status: draft → applied → interview → offer |
| `get_prompt` | Retrieve any prompt file by path |

---

## GitHub Actions

| Workflow | Trigger | What it does |
|---|---|---|
| `build-artifacts` | Push to `resume.md` or `cover_letter.md` | Builds PDF/DOCX, runs ATS check, commits artifacts back |
| `ats-check` | PR touching `resume.md` | Posts ATS score comment on the PR |
| `validate-setup` | Push to `source_materials/**` | Runs `check_setup.py` and surfaces gaps |

---

## Role categories

The pipeline auto-detects role type from the JD:

| Category | Typical roles | Approach |
|---|---|---|
| `engineering` | Software Engineer, DevOps, ML, Data | Impact metrics, system scale, technical depth |
| `business` | Sales, Marketing, Operations, Finance | Revenue, efficiency, stakeholder outcomes |
| `creative` | Designer, Writer, Brand, Content | Portfolio framing, craft, audience impact |
| `healthcare` | Nurse, Physician, Clinical, Allied Health | Patient outcomes, clinical accuracy, compliance |
| `academic` | Professor, Researcher, Postdoc | Publications, grants, teaching, institutional fit |

## Templates

| Template | Best for |
|---|---|
| `default` | Engineering and business roles — modern, clean |
| `minimal` | Healthcare, academic, conservative industries |
| `creative` | Design and creative roles — bold, colourful |
| `executive` | Director, VP, C-level — authoritative, understated |

Set your preferred template in `identity.json → preferences.template`, or override per build:

```bash
python scripts/build_resume.py applications/<folder>/resume.md --template executive
# or
/career:rebuild stripe executive
```

---

## CLI reference

```bash
# Setup
make install                                    # pip install -r requirements.txt
make check                                      # verify LaTeX + Pandoc installed
make validate                                   # validate source materials
python scripts/check_setup.py                   # JSON status, exit 0 = ready

# Applications
make build                                      # build most recent application
make build APP=2025-01-09-stripe-eng            # build specific application
make build-all                                  # build all applications
python scripts/career.py new --company "Stripe" --role "Senior Engineer"
python scripts/career.py list
python scripts/career.py status
python scripts/career.py stats

# Scoring and export
python scripts/ats_score.py applications/<folder>/
python scripts/export_resume.py all <folder>    # TXT + JSON Resume

# Web dashboard
make dashboard                                  # streamlit run app.py
```

---

## Project structure

```
career-architect/
├── source_materials/
│   ├── identity.json            ← your contact info and preferences
│   ├── master_experience.md     ← experience lake (built by /career:setup)
│   ├── resumes/                 ← your historical resumes as .md files
│   └── projects/                ← project case studies as .md files
│
├── applications/
│   └── YYYY-MM-DD-company-role/
│       ├── job_desc.md
│       ├── resume.md
│       ├── cover_letter.md
│       ├── interview_prep.md
│       ├── salary_brief.md
│       └── resume.pdf / resume.docx
│
├── .claude/
│   └── commands/career/         ← 13 slash commands (/career:<name>)
│
├── .prompts/
│   ├── main_orchestrator.md     ← pipeline controller
│   ├── core/                    ← shared prompts
│   └── engineering|business|creative|healthcare|academic/
│
├── scripts/
│   ├── career.py                ← main CLI
│   ├── build_resume.py          ← PDF/DOCX builder (reads identity.json for header)
│   ├── check_setup.py           ← setup validator (exit 0 = ready)
│   ├── ats_score.py             ← ATS keyword scorer
│   └── export_resume.py         ← TXT + JSON Resume export
│
├── templates/
│   ├── style.tex                ← default template
│   ├── minimal.tex
│   ├── creative.tex
│   ├── executive.tex
│   └── cover_letter_style.tex
│
├── mcp_server.py                ← MCP server (JSON-RPC 2.0 over stdio)
├── .mcp.json                    ← auto-registers server in compatible editors
├── CLAUDE.md                    ← Claude Code session context
├── AGENTS.md                    ← OpenAI Codex / Agents SDK reference
├── TRACKER.md                   ← your personal application tracker
└── app.py                       ← Streamlit web dashboard
```

---

## Contributing

Bug reports and feature requests welcome — use the issue templates. PRs should target a feature branch, not `main` directly.

```bash
make test     # pytest
make lint     # flake8
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT — see [LICENSE](LICENSE).

---

*Built for people who treat job applications as a system, not a lottery.*

> ⭐ If Career Architect saved you time on an application, a star helps others find it.
