# Career Architect — Agent Integration Guide

Career Architect is designed to work with any LLM or agent framework, not just Claude. This guide covers every supported integration path.

---

## Supported integrations

| Integration | Entry point |
|---|---|
| Claude Code | `CLAUDE.md` + `.claude/commands/career/` |
| Gemini CLI | `GEMINI.md` |
| GitHub Copilot agent | `.github/copilot-instructions.md` |
| MCP (Cursor, Windsurf, Claude Desktop, etc.) | `.mcp.json` + `mcp_server.py` |
| OpenAI Agents SDK / GPT-4o function calling | `tools/openai_tools.json` |
| LangChain / LangGraph | `tools/langchain_tools.py` |
| CrewAI | `tools/langchain_tools.py` (compatible) |
| Aider | `.aider.conf.yml` + file-based interface |
| Any LLM with file access | File-based interface (see below) |

---

## Universal rules

These apply regardless of which LLM or framework you use.

1. **Setup gate first, always.** Run `python scripts/check_setup.py` before any generation step. Only proceed when `ready: true`.
2. **Never hallucinate contact info.** All names, emails, phones, and URLs must come from `source_materials/identity.json` verbatim.
3. **No H1 headers in `resume.md`.** The build script injects the name and contact header from `identity.json` — an H1 breaks the PDF layout.
4. **YAML frontmatter required** on every generated document: `company`, `role`, `date`, `status`.
5. **ATS gate.** If `ats_score.py` returns <50%, revise the resume before building PDF artifacts.
6. **Role boundaries.** Use only the prompts from the detected `role_category` subdirectory. Never mix frameworks across categories.

---

## MCP integration

The fastest path for any MCP-compatible client (Cursor, Windsurf, Claude Desktop, VS Code with MCP extension).

The `.mcp.json` at the repo root auto-registers the server:

```json
{
  "mcpServers": {
    "career-architect": {
      "command": "python3",
      "args": ["${workspaceFolder}/mcp_server.py"]
    }
  }
}
```

If your editor does not pick it up automatically, add it to your editor's MCP settings manually with the absolute path to `mcp_server.py`.

### MCP tools

| Tool | Description |
|---|---|
| `check_setup` | Validate setup, returns JSON |
| `create_application` | Create folder and save JD |
| `get_pipeline_context` | Return orchestrator + source context |
| `write_document` | Write resume.md, cover_letter.md, etc. |
| `run_ats_score` | ATS keyword scoring |
| `build_resume` | Build PDF/DOCX/TXT artifacts |
| `update_status` | Update application status |
| `list_applications` | Survey all applications |
| `get_prompt` | Load any prompt file |
| `rebuild_experience_lake` | Rebuild master_experience.md |

### Recommended MCP flow

```
1. check_setup()
2. create_application(company, role, job_description)
3. get_pipeline_context(folder)
4. [LLM runs orchestrator, generates documents]
5. write_document(folder, "resume.md", content)
6. write_document(folder, "cover_letter.md", content)
7. run_ats_score(folder)
8. build_resume(folder, template)
9. update_status(folder, "applied")
```

---

## OpenAI Agents SDK / function calling

Use `tools/openai_tools.json` — standard OpenAI tool schema compatible with GPT-4o, Gemini (OpenAI-compatible API), Mistral, and any LLM that accepts the OpenAI function calling format.

```python
import json
import openai
from pathlib import Path

tools = json.loads(Path("tools/openai_tools.json").read_text())

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": Path("AGENTS.md").read_text()},
        {"role": "user", "content": "Apply to this job at Stripe: <JD>"},
    ],
    tools=tools,
    tool_choice="auto",
)
```

Each tool in `openai_tools.json` maps to a script in `scripts/`. Implement a dispatcher that calls the appropriate script when the LLM requests a tool:

```python
import subprocess, sys

def dispatch_tool(name: str, args: dict) -> str:
    if name == "check_setup":
        r = subprocess.run([sys.executable, "scripts/check_setup.py"],
                           capture_output=True, text=True)
        return r.stdout

    elif name == "create_application":
        r = subprocess.run([
            sys.executable, "scripts/career.py", "new",
            "--company", args["company"], "--role", args["role"]
        ], capture_output=True, text=True)
        return r.stdout

    elif name == "run_ats_score":
        r = subprocess.run([
            sys.executable, "scripts/ats_score.py",
            f"applications/{args['folder']}/"
        ], capture_output=True, text=True)
        return r.stdout

    elif name == "build_resume":
        r = subprocess.run([
            sys.executable, "scripts/build_resume.py",
            f"applications/{args['folder']}/resume.md",
            "--template", args.get("template", "default")
        ], capture_output=True, text=True)
        return r.stdout

    return f"Unknown tool: {name}"
```

---

## LangChain / LangGraph

`tools/langchain_tools.py` provides ready-made LangChain `@tool` functions.

```python
from tools.langchain_tools import get_career_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(model="gpt-4o")
tools = get_career_tools()

agent = create_react_agent(llm, tools)
result = agent.invoke({
    "messages": [("user", "Apply to this job at Stripe: <JD>")]
})
```

Works equally with `ChatAnthropic`, `ChatGoogleGenerativeAI`, or any LangChain-compatible LLM.

### CrewAI

```python
from crewai import Agent, Task, Crew
from tools.langchain_tools import get_career_tools

application_agent = Agent(
    role="Career Architect Agent",
    goal="Generate tailored, ATS-optimised application materials",
    backstory="Expert job application strategist with access to the user's full experience history.",
    tools=get_career_tools(),
    verbose=True,
)

apply_task = Task(
    description="Apply to {role} at {company}. JD: {job_description}. "
                "Follow the pipeline: setup → create → generate → ATS score → build PDF.",
    expected_output="Application folder path and ATS score",
    agent=application_agent,
)

crew = Crew(agents=[application_agent], tasks=[apply_task])
crew.kickoff(inputs={"company": "Stripe", "role": "Senior Engineer", "job_description": "..."})
```

---

## Aider

Add `.aider.conf.yml` to the repo root:

```yaml
read:
  - AGENTS.md
  - source_materials/identity.json
  - source_materials/master_experience.md
  - .prompts/main_orchestrator.md
```

Then:

```bash
aider --message "Apply to Senior Engineer at Stripe. JD: <paste JD>"
```

Aider reads the context files, follows the orchestrator, and writes the application documents directly.

---

## Raw file-based interface

Any LLM with filesystem access can run the full pipeline without any framework.

**Step 1 — Validate**
```bash
python scripts/check_setup.py
```

**Step 2 — Read source context**
```
source_materials/identity.json
source_materials/master_experience.md
```

**Step 3 — Read and follow the pipeline**
```
.prompts/main_orchestrator.md
```

**Step 4 — Write outputs** to `applications/YYYY-MM-DD-company-role/`:

| File | Required |
|---|---|
| `job_desc.md` | ✅ with YAML frontmatter |
| `resume.md` | ✅ no H1, no contact info, YAML frontmatter |
| `cover_letter.md` | ✅ with YAML frontmatter |
| `interview_prep.md` | recommended |
| `salary_brief.md` | optional |

**Step 5 — Score and build**
```bash
python scripts/ats_score.py applications/<folder>/
python scripts/build_resume.py applications/<folder>/resume.md --template default
python scripts/build_resume.py applications/<folder>/cover_letter.md
```

---

## Example end-to-end session

```
User:  Apply to this job at Stripe as a Senior Backend Engineer. [JD text]

Agent:
  1. check_setup()                          → ready: true
  2. create_application("Stripe", "Senior Backend Engineer", "<JD>")
     → applications/2026-06-24-stripe-senior-backend-engineer/
  3. get_pipeline_context(folder)
  4. Detect role_category: engineering
  5. Run .prompts/engineering/analyser.md   → strategic_match_report.md
  6. [Present match report — pause for user GO]
  7. Run .prompts/engineering/tailor_resume.md → resume.md
  8. Run .prompts/core/cover_letter.md      → cover_letter.md
  9. run_ats_score(folder)                  → 78%, missing: "distributed systems"
 10. Patch resume.md with missing keywords
 11. run_ats_score(folder)                  → 84% — clear to build
 12. build_resume(folder, template="default")
     → resume.pdf, resume.docx, resume.txt
 13. update_status(folder, "applied")
```

---

## Output folder structure

```
applications/2026-06-24-stripe-senior-backend-engineer/
├── job_desc.md
├── strategic_match_report.md
├── resume.md
├── cover_letter.md
├── interview_prep.md
├── salary_brief.md
├── ats_score.txt
├── resume.pdf
├── resume.docx
├── resume.txt
├── cover_letter.pdf
└── cover_letter.docx
```
