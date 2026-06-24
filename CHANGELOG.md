# Changelog

All notable changes to Career Architect are documented here.

---

## [Unreleased]

### Added
- `/career:follow-up` command — generate post-application and post-interview follow-up emails
- `/career:linkedin` command — optimise all LinkedIn profile sections for a target role
- `/career:mock-interview` command — live mock interview session with per-answer feedback
- `/career:status` command — full application dashboard with AI-generated next actions
- `.devcontainer/` — GitHub Codespaces support; zero local install required
- `Dockerfile` — single-container build with Python + Pandoc + LaTeX pre-installed
- `.github/ISSUE_TEMPLATE/` — bug report and feature request templates

---

## [0.3.0] — 2026-06-24

### Added
- **Agent integration**: Career Architect now works as a native agent in Claude Code, MCP-compatible editors, and GitHub Actions
- `CLAUDE.md` — full project context loaded automatically by Claude Code
- `AGENTS.md` — instructions for OpenAI Codex / Agents SDK
- `.mcp.json` — auto-registers MCP server in Cursor, Windsurf, Claude Desktop
- `mcp_server.py` — JSON-RPC 2.0 MCP server with 7 tools
- `.claude/commands/career/` — 8 namespaced slash commands (`/career:setup`, `/career:tailor`, `/career:analyze`, `/career:interview-prep`, `/career:cover-letter`, `/career:ats-score`, `/career:salary`, `/career:rebuild-lake`)
- `scripts/check_setup.py` — reusable setup validator (exit 0 = fully ready)
- `.claude/settings.json` — branch protection hook (blocks commits on main)
- **GitHub Actions**: `build-artifacts.yml`, `ats-check.yml`, `validate-setup.yml`

### Changed
- README rewritten to lead with three usage paths: Claude Code, MCP editor, CI-only

---

## [0.2.0] — 2025-12

### Added
- Multi-profile prompt system: engineering, business, creative, healthcare, academic role categories
- Role detector — auto-classifies job type from JD
- Domain-specific capability frameworks (Modern Builder, Business Impact, Creative Portfolio, Clinical Outcomes, Academic Research)
- Quality gates (Gates A–F) throughout the pipeline
- Gap filler prompt — updates experience lake when gaps are identified
- Style guide prompt — configurable resume styles
- Mock interview and salary negotiation prompts
- Multiple LaTeX templates: default, minimal, creative, executive
- Version tracking (`scripts/version_tracker.py`)
- Batch processing (`scripts/batch_process.py`)
- Job scraper (`scripts/job_scraper.py`)
- ATS keyword scoring (`scripts/ats_score.py`)
- Streamlit web dashboard (`app.py`)

---

## [0.1.0] — 2025-01

### Added
- Initial release
- Core pipeline: setup → analyse → generate → build
- `source_materials/` structure (identity.json, master_experience.md, resumes/, projects/)
- `main_orchestrator.md` pipeline controller
- Cover letter, application questions, follow-up, PDF generator prompts
- `scripts/build_resume.py` and `scripts/compile_all.py`
- Makefile with common targets
- MIT license
