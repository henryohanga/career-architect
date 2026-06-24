"""LangChain tool wrappers for the Career Architect pipeline.

Usage:
    from tools.langchain_tools import get_career_tools
    tools = get_career_tools()

    # With LangChain agent
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)

    # With LangGraph
    from langgraph.prebuilt import create_react_agent
    graph = create_react_agent(llm, tools)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    from langchain_core.tools import tool
except ImportError:
    raise ImportError(
        "langchain-core is required: pip install langchain-core"
    )

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str]) -> str:
    """Run a command from the repo root and return combined stdout+stderr."""
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    output = result.stdout
    if result.stderr:
        output += "\n" + result.stderr
    return output.strip()


@tool
def check_setup() -> str:
    """Validate that Career Architect is fully configured.

    Always call this before any pipeline action. Returns JSON with a top-level
    'ready' boolean and per-step detail. Only proceed when ready is true.
    """
    return _run([sys.executable, "scripts/check_setup.py"])


@tool
def list_applications() -> str:
    """List all application folders with status and document completeness."""
    return _run([sys.executable, "scripts/career.py", "list"])


@tool
def create_application(company: str, role: str) -> str:
    """Create a new application folder for a job.

    Args:
        company: Company name, e.g. 'Stripe'
        role: Role title, e.g. 'Senior Backend Engineer'

    Returns the created folder path.
    """
    return _run([sys.executable, "scripts/career.py", "new", "--company", company, "--role", role])


@tool
def get_pipeline_context() -> str:
    """Return the orchestrator prompt and source material summary.

    Feed this to the LLM before asking it to generate application documents.
    Includes identity.json fields, master_experience.md summary, and the
    main_orchestrator.md prompt.
    """
    parts = []

    orchestrator = ROOT / ".prompts" / "main_orchestrator.md"
    if orchestrator.exists():
        parts.append("## Orchestrator\n" + orchestrator.read_text())

    identity = ROOT / "source_materials" / "identity.json"
    if identity.exists():
        parts.append("## Identity\n```json\n" + identity.read_text() + "\n```")

    lake = ROOT / "source_materials" / "master_experience.md"
    if lake.exists():
        parts.append("## Experience Lake\n" + lake.read_text())

    return "\n\n---\n\n".join(parts) if parts else "Setup incomplete — run check_setup first."


@tool
def write_document(folder: str, filename: str, content: str) -> str:
    """Write a generated document to an application folder.

    Args:
        folder: Application folder name, e.g. '2026-06-24-stripe-senior-engineer'
        filename: File to write, e.g. 'resume.md' or 'cover_letter.md'
        content: Full file content including YAML frontmatter
    """
    target = ROOT / "applications" / folder / filename
    if not target.parent.exists():
        return f"Folder not found: applications/{folder} — run create_application first."
    target.write_text(content, encoding="utf-8")
    return f"Written: {target.relative_to(ROOT)}"


@tool
def run_ats_score(folder: str) -> str:
    """Run ATS keyword scoring on an application folder.

    Compares resume.md against job_desc.md. Returns score and missing keywords.
    Score ≥70% is strong, 50–69% acceptable, <50% is a blocker — revise before building.

    Args:
        folder: Application folder name
    """
    return _run([sys.executable, "scripts/ats_score.py", f"applications/{folder}/"])


@tool
def build_resume(folder: str, template: str = "default") -> str:
    """Build PDF, DOCX, and TXT artifacts from resume.md.

    Only call after ATS score is ≥50%. Reads identity.json to inject the
    contact header automatically.

    Args:
        folder: Application folder name
        template: LaTeX template — default, minimal, creative, or executive
    """
    resume_path = ROOT / "applications" / folder / "resume.md"
    if not resume_path.exists():
        return f"resume.md not found in applications/{folder}/"
    return _run([
        sys.executable, "scripts/build_resume.py",
        str(resume_path), "--template", template
    ])


@tool
def get_prompt(path: str) -> str:
    """Retrieve the content of any prompt file from .prompts/.

    Use this to load role-specific prompts or quality gate definitions.

    Args:
        path: Relative path within .prompts/, e.g. 'core/cover_letter.md'
               or 'engineering/tailor_resume.md'
    """
    prompt_file = ROOT / ".prompts" / path
    if not prompt_file.exists():
        available = [str(p.relative_to(ROOT / ".prompts")) for p in (ROOT / ".prompts").rglob("*.md")]
        return f"Prompt not found: {path}\n\nAvailable:\n" + "\n".join(sorted(available))
    return prompt_file.read_text(encoding="utf-8")


@tool
def get_status() -> str:
    """Return a summary of all applications and their current status."""
    return _run([sys.executable, "scripts/career.py", "status"])


def get_career_tools() -> list:
    """Return all Career Architect tools as a list for use with any LangChain agent."""
    return [
        check_setup,
        list_applications,
        create_application,
        get_pipeline_context,
        write_document,
        run_ats_score,
        build_resume,
        get_prompt,
        get_status,
    ]
