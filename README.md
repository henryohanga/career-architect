# Career Architect 🏗️

> **Paste a job description. Let AI do the rest.**

An open-source, AI-powered job application pipeline. Works natively as a **Claude Code agent** (slash commands), an **MCP server** (Cursor, Windsurf, Claude Desktop), or a **headless CI pipeline** (GitHub Actions). Generates tailored resumes, cover letters, interview prep, and PDFs — all from your personal experience lake.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/henryohanga/career-architect)

> ⭐ **If this saves you time on a job application, please star the repo** — it helps others find it.

---

## How It Works

```
┌──────────────┐     ┌─────────────────────────────────┐     ┌───────────────┐
│  1. SETUP    │────▶│       2. PASTE JOB DESC          │────▶│  3. BUILD PDF │
├──────────────┤     ├─────────────────────────────────┤     ├───────────────┤
│ Fill identity│     │ /career:tailor → full pipeline:  │     │ CI builds on  │
│ Add resumes  │     │ • Strategic match report         │     │ every push,   │
│ Build lake   │     │ • Tailored resume (ATS-scored)   │     │ or: make build│
│ (once only)  │     │ • Cover letter                   │     │               │
└──────────────┘     │ • Interview prep                 │     └───────────────┘
                     │ • PDF/DOCX artifacts              │
                     └─────────────────────────────────┘
```

---

## Quick Start

### Option A — GitHub Codespaces (zero install, fastest)

Click the badge above or:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/henryohanga/career-architect)

Python, Pandoc, and LaTeX are pre-installed. Just open the terminal and run `/career:setup`.

### Option B — Claude Code (local)

```bash
git clone https://github.com/henryohanga/career-architect.git
cd career-architect
pip install -r requirements.txt
```

Open the folder in Claude Code, then run:

```
/career:setup
```

That's it. `/career:setup` walks you through everything interactively — identity, source materials, and building your experience lake. When it's done, you're ready:

```
/career:tailor   ← paste a job description here
```

### Option C — Docker (no LaTeX install needed)

```bash
git clone https://github.com/henryohanga/career-architect.git
cd career-architect
docker build -t career-architect .
docker run -it -v $(pwd):/work career-architect python scripts/career.py status
```

### Option D — Cursor / Windsurf / Claude Desktop (MCP)

```bash
git clone https://github.com/henryohanga/career-architect.git
cd career-architect
pip install -r requirements.txt
```

Open the folder in your editor. The `.mcp.json` file auto-registers the `career-architect` MCP server. Ask your AI:

```
"Set up Career Architect for me — walk me through identity and source materials"
"Create an application for Stripe - Senior Engineer. Here's the JD: ..."
"Get the pipeline context and generate a tailored resume"
"Build the PDF artifacts"
```

### Option E — OpenAI Codex / Agents SDK

See [AGENTS.md](AGENTS.md) for tool wiring and prompt patterns.

### Option F — Headless / CI only

Set up once locally with Claude Code (`/career:setup`), then push `resume.md` files — GitHub Actions auto-builds PDFs and posts ATS scores on every PR. No local LaTeX needed.

---

## Agent Skills (Claude Code slash commands)

All skills run a setup gate first and redirect to `/career:setup` if anything is missing.

| Command | What it does |
|---|---|
| `/career:setup` | **One-time onboarding** — identity, source materials, experience lake |
| `/career:tailor` | Full pipeline from JD → resume + cover letter + artifacts |
| `/career:analyze` | Analyse a JD and produce a strategic match report (no generation) |
| `/career:interview-prep` | Tailored question bank + STAR story starters |
| `/career:cover-letter` | Generate or regenerate a cover letter for an existing application |
| `/career:ats-score` | Run ATS keyword scoring with pass/fail guidance |
| `/career:salary` | Salary research + negotiation talking points |
| `/career:rebuild-lake` | Refresh experience lake after adding new resumes or projects |
| `/career:rebuild` | Regenerate PDF/DOCX artifacts from existing markdown (no content regen) |
| `/career:follow-up` | Generate post-application or post-interview follow-up emails |
| `/career:linkedin` | Optimise all LinkedIn profile sections for a target role |
| `/career:mock-interview` | Live mock interview with per-answer coaching and feedback |
| `/career:status` | Full application dashboard with AI-generated next actions |

---

## First-Time Setup (4 Steps)

Run `/career:setup` — it handles all of this interactively. Here's what happens under the hood:

### Step 1 — Identity

Edit `source_materials/identity.json` with your real contact info:

```json
{
  "full_name": "Jane Smith",
  "email": "jane@email.com",
  "phone": "+1 234 567 8901",
  "location": "San Francisco, CA",
  "linkedin": "https://linkedin.com/in/janesmith",
  "github": "https://github.com/janesmith",
  "preferences": {
    "language": "en",
    "resume_style": "modern_builder",
    "tone": "professional",
    "template": "default"
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

### Step 2 — Source Materials

Add your existing resumes and project docs to:

```
source_materials/resumes/
├── 2024-google-resume.md      ← paste raw resume text here
├── 2023-startup-resume.md
└── general-resume.md

source_materials/projects/
├── payment-system.md          ← project details + metrics
└── open-source-library.md
```

Just paste raw text — the AI extracts and structures everything. See the README files in each directory for the expected format.

### Step 3 — Build the Experience Lake

The AI reads all your source materials and produces `source_materials/master_experience.md` — a comprehensive, metrics-rich knowledge base every future application draws from.

```bash
# Via Claude Code:
/career:setup    ← handles this automatically

# Check status anytime:
make validate
# or:
python scripts/check_setup.py
```

### Step 4 — Apply

```
/career:tailor   ← paste any job description
```

The pipeline auto-detects role type, runs gap analysis, generates documents, scores ATS coverage, and builds PDF/DOCX artifacts.

---

## MCP Tools

When connected as an MCP server, these tools are available to any AI hub:

| Tool | Description |
|---|---|
| `list_applications` | List all applications with status and document completeness |
| `create_application` | Create a new application folder and save the job description |
| `get_pipeline_context` | Return the orchestrator prompt + source material context for running the full pipeline |
| `run_ats_score` | Run ATS keyword scoring on an application folder |
| `build_resume` | Build PDF and DOCX artifacts from resume.md |
| `update_status` | Update application status (draft → applied → interview → offer) |
| `get_prompt` | Retrieve any prompt file by path (e.g. `core/cover_letter.md`) |

**Manual MCP config** (if `.mcp.json` isn't picked up automatically):

```json
{
  "mcpServers": {
    "career-architect": {
      "command": "python",
      "args": ["/absolute/path/to/career-architect/mcp_server.py"]
    }
  }
}
```

---

## GitHub Actions (CI/CD)

Three workflows run automatically:

| Workflow | Trigger | What it does |
|---|---|---|
| `build-artifacts` | Push to any `resume.md` / `cover_letter.md` | Installs LaTeX+Pandoc, picks the right template, builds PDF/DOCX, runs ATS check, commits artifacts back |
| `ats-check` | PR touching `resume.md` | Posts ATS score comment (✅ ≥80% / ⚠️ 50–79% / ❌ <50%) on the PR |
| `validate-setup` | Push to `source_materials/**` | Runs `check_setup.py` and surfaces gaps in the Actions log |

---

## Supported Role Categories

The pipeline auto-detects role type from the JD and routes to the right prompts:

| Category | Example Roles | Framework |
|---|---|---|
| `engineering` | Software Engineer, DevOps, Data, ML | Modern Builder |
| `business` | Sales, Marketing, Operations, Finance, HR | Business Impact |
| `creative` | Designer, Writer, Brand Manager | Creative Portfolio |
| `healthcare` | Nurse, Physician, Clinical, Medical | Clinical Outcomes |
| `academic` | Professor, Researcher, Postdoc | Academic Research |

---

## Templates

| Template | Best For |
|---|---|
| `default` | Modern professional (all engineering/business roles) |
| `minimal` | Conservative industries, healthcare, academic |
| `creative` | Design roles, startups, bold styling |
| `executive` | Director+, VP, C-level, senior leadership |

---

## CLI Reference

```bash
# Setup
make setup                              # Check setup status
make validate                           # Validate source materials
make install                            # Install Python dependencies
make check                              # Verify LaTeX + Pandoc are installed

# Building
make build                              # Build most recent application
make build-all                          # Build all applications
make build APP=2025-01-09-stripe-eng    # Build specific application
make ats                                # ATS score for most recent application

# Scripts
python scripts/career.py new --company "Stripe" --role "Senior Engineer"
python scripts/career.py list
python scripts/career.py status
python scripts/career.py validate
python scripts/career.py ats
python scripts/career.py export         # TXT + JSON Resume formats
python scripts/career.py stats          # Application analytics

# Web dashboard
make dashboard                          # streamlit run app.py
```

---

## Project Structure

```
career-architect/
├── .claude/
│   └── commands/career/     # Claude Code slash commands (/career:<name>)
│       ├── setup.md         # /career:setup
│       ├── tailor.md        # /career:tailor
│       ├── analyze.md       # /career:analyze
│       ├── interview-prep.md
│       ├── cover-letter.md
│       ├── ats-score.md
│       ├── salary.md
│       ├── rebuild-lake.md
│       ├── rebuild.md       # /career:rebuild — regen PDFs only
│       ├── follow-up.md
│       ├── linkedin.md
│       ├── mock-interview.md
│       └── status.md
├── .github/
│   └── workflows/
│       ├── build-artifacts.yml
│       ├── ats-check.yml
│       └── validate-setup.yml
├── .prompts/
│   ├── main_orchestrator.md # Pipeline controller
│   ├── core/                # Shared prompts (all role types)
│   └── engineering|business|creative|healthcare|academic/
├── applications/            # Generated per-job folders
│   └── YYYY-MM-DD-company-role/
│       ├── job_desc.md
│       ├── resume.md
│       ├── cover_letter.md
│       ├── interview_prep.md
│       ├── salary_brief.md
│       └── *.pdf, *.docx
├── source_materials/
│   ├── identity.json        # Contact info + preferences (source of truth)
│   ├── master_experience.md # Experience lake (built by /setup)
│   ├── resumes/             # Your historical resumes as .md files
│   └── projects/            # Project case studies as .md files
├── scripts/
│   ├── check_setup.py       # Setup validator (exit 0 = ready)
│   ├── career.py            # Main CLI
│   ├── build_resume.py      # PDF/DOCX builder
│   ├── ats_score.py         # ATS keyword scorer
│   └── ...
├── templates/               # LaTeX templates
├── mcp_server.py            # MCP server (JSON-RPC 2.0)
├── .mcp.json                # Auto-registers MCP server in compatible editors
├── CLAUDE.md                # Claude Code context
├── AGENTS.md                # OpenAI Codex / Agents SDK instructions
└── app.py                   # Streamlit web dashboard
```

---

## Development

```bash
make test       # Run unit tests (pytest)
make lint       # Check Python syntax
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT — see [LICENSE](LICENSE).

---

**Built for people who treat job applications as a system to be optimized.** 🎯
