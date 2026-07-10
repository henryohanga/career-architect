#!/usr/bin/env python3
"""Career Architect MCP Server.

Exposes the Career Architect pipeline as MCP tools so any MCP-compatible
AI hub (Claude, Cursor, Windsurf, Codex, etc.) can call it directly.

Usage:
    python mcp_server.py

Add to your MCP config (e.g. ~/.cursor/mcp.json or claude_desktop_config.json):
    {
      "mcpServers": {
        "career-architect": {
          "command": "python",
          "args": ["/path/to/career-architect/mcp_server.py"]
        }
      }
    }
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPLICATIONS_DIR = ROOT / "applications"
SOURCE_DIR = ROOT / "source_materials"
IDENTITY_JSON = SOURCE_DIR / "identity.json"
MASTER_EXP = SOURCE_DIR / "master_experience.md"
PROMPTS_DIR = ROOT / ".prompts"


def _load_identity() -> dict:
    if IDENTITY_JSON.exists():
        return json.loads(IDENTITY_JSON.read_text())
    return {}


def _load_prompt(path: str) -> str:
    p = PROMPTS_DIR / path
    return p.read_text() if p.exists() else f"[prompt not found: {path}]"


def _slugify(text: str) -> str:
    import re
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def _find_app_folder(company: str = "", role: str = "") -> Path | None:
    if not APPLICATIONS_DIR.exists():
        return None
    candidates = sorted(APPLICATIONS_DIR.iterdir(), reverse=True)
    candidates = [c for c in candidates if c.is_dir() and not c.name.startswith(".")]
    if not candidates:
        return None
    if company or role:
        slug = _slugify(f"{company}-{role}")
        for c in candidates:
            if slug in c.name or company.lower() in c.name or role.lower() in c.name:
                return c
    return candidates[0]


def tool_list_applications() -> dict:
    """List all job applications with their status and document completeness."""
    apps = []
    if APPLICATIONS_DIR.exists():
        for d in sorted(APPLICATIONS_DIR.iterdir(), reverse=True):
            if not d.is_dir() or d.name.startswith("."):
                continue
            app = {
                "folder": d.name,
                "company": "",
                "role": "",
                "status": "draft",
                "date": d.name[:10] if len(d.name) >= 10 else "",
                "has_resume": (d / "resume.md").exists(),
                "has_cover_letter": (d / "cover_letter.md").exists(),
                "has_pdf": any(d.glob("*.pdf")),
                "has_interview_prep": (d / "interview_prep.md").exists(),
            }
            job_desc = d / "job_desc.md"
            if job_desc.exists():
                for line in job_desc.read_text().split("\n"):
                    if line.startswith("company:"):
                        app["company"] = line.split(":", 1)[1].strip()
                    elif line.startswith("role:"):
                        app["role"] = line.split(":", 1)[1].strip()
                    elif line.startswith("status:"):
                        app["status"] = line.split(":", 1)[1].strip()
            apps.append(app)
    return {"applications": apps, "total": len(apps)}


def tool_create_application(company: str, role: str, job_description: str) -> dict:
    """Create a new application folder and save the job description.

    Args:
        company: Company name.
        role: Role/position title.
        job_description: Full job description text.
    """
    date = datetime.now().strftime("%Y-%m-%d")
    slug = f"{date}-{_slugify(company)}-{_slugify(role)}"
    app_dir = APPLICATIONS_DIR / slug

    if app_dir.exists():
        return {"error": f"Application folder already exists: {slug}"}

    app_dir.mkdir(parents=True, exist_ok=True)

    content = f"""---
company: {company}
role: {role}
date_added: {date}
status: draft
source_url:
---

# {company} - {role}

## Job Description

{job_description}

## Notes

-
"""
    (app_dir / "job_desc.md").write_text(content)

    return {
        "folder": slug,
        "path": str(app_dir),
        "message": f"Created application: {slug}. Now run get_pipeline_context to get the prompt for tailoring your resume.",
    }


def tool_get_pipeline_context(folder: str = "", company: str = "", role: str = "") -> dict:
    """Return the full orchestrator prompt and all relevant source material context
    needed to run the Career Architect pipeline in any AI hub.

    Args:
        folder: Application folder name (optional, auto-detects most recent).
        company: Company name to find the folder (optional).
        role: Role title to find the folder (optional).
    """
    app_dir = (APPLICATIONS_DIR / folder) if folder else _find_app_folder(company, role)
    if not app_dir or not app_dir.exists():
        return {"error": "No application folder found. Run create_application first."}

    identity = _load_identity()
    master_exp = MASTER_EXP.read_text() if MASTER_EXP.exists() else "[master_experience.md not found]"
    orchestrator = _load_prompt("main_orchestrator.md")
    job_desc = (app_dir / "job_desc.md").read_text() if (app_dir / "job_desc.md").exists() else "[job_desc.md not found]"

    return {
        "folder": app_dir.name,
        "instructions": "Feed the following context + orchestrator to your AI to run the full pipeline.",
        "orchestrator_prompt": orchestrator,
        "job_description": job_desc,
        "identity": identity,
        "master_experience_summary": master_exp[:3000] + "..." if len(master_exp) > 3000 else master_exp,
    }


def tool_run_ats_score(folder: str = "", company: str = "", role: str = "") -> dict:
    """Run ATS keyword scoring on an application folder.

    Args:
        folder: Application folder name (optional, auto-detects most recent).
        company: Company name to find the folder (optional).
        role: Role title to find the folder (optional).
    """
    app_dir = (APPLICATIONS_DIR / folder) if folder else _find_app_folder(company, role)
    if not app_dir or not app_dir.exists():
        return {"error": "No application folder found."}

    result = subprocess.run(
        [sys.executable, "scripts/ats_score.py", str(app_dir)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )

    return {
        "folder": app_dir.name,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def tool_build_resume(folder: str = "", template: str = "default", company: str = "", role: str = "") -> dict:
    """Build PDF and DOCX artifacts from resume.md in an application folder.

    Args:
        folder: Application folder name (optional, auto-detects most recent).
        template: LaTeX template — default, minimal, creative, or executive.
        company: Company name to find the folder (optional).
        role: Role title to find the folder (optional).
    """
    app_dir = (APPLICATIONS_DIR / folder) if folder else _find_app_folder(company, role)
    if not app_dir or not app_dir.exists():
        return {"error": "No application folder found."}

    resume_md = app_dir / "resume.md"
    if not resume_md.exists():
        return {"error": "resume.md not found in the application folder."}

    valid_templates = {"default", "minimal", "creative", "executive"}
    if template not in valid_templates:
        return {"error": f"Invalid template. Choose from: {', '.join(valid_templates)}"}

    result = subprocess.run(
        [sys.executable, "scripts/build_resume.py", str(resume_md), "--template", template],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )

    artifacts = {
        "pdf": str(app_dir / "resume.pdf") if (app_dir / "resume.pdf").exists() else None,
        "docx": str(app_dir / "resume.docx") if (app_dir / "resume.docx").exists() else None,
        "txt": str(app_dir / "resume.txt") if (app_dir / "resume.txt").exists() else None,
    }

    return {
        "folder": app_dir.name,
        "template": template,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "artifacts": artifacts,
    }


def tool_update_status(folder: str, status: str) -> dict:
    """Update the status of an application.

    Args:
        folder: Application folder name.
        status: New status — draft, applied, interview, rejected, or offer.
    """
    valid = {"draft", "applied", "interview", "rejected", "offer"}
    if status not in valid:
        return {"error": f"Invalid status. Choose from: {', '.join(valid)}"}

    app_dir = APPLICATIONS_DIR / folder
    job_desc = app_dir / "job_desc.md"
    if not job_desc.exists():
        return {"error": f"job_desc.md not found in {folder}"}

    lines = job_desc.read_text().split("\n")
    updated = [f"status: {status}" if l.startswith("status:") else l for l in lines]
    job_desc.write_text("\n".join(updated))

    return {"folder": folder, "status": status, "message": "Status updated."}


def tool_check_setup() -> dict:
    """Check whether Career Architect is set up (identity, source materials,
    experience lake). Run this before any other tool."""
    result = subprocess.run(
        [sys.executable, "scripts/check_setup.py"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    try:
        status = json.loads(result.stdout)
    except json.JSONDecodeError:
        status = {"raw_output": result.stdout}
    status["exit_code"] = result.returncode
    return status


def tool_write_document(folder: str, filename: str, content: str) -> dict:
    """Write a document (resume.md, cover_letter.md, ...) into an application
    folder. Path-sandboxed: only .md/.txt files inside applications/.

    Args:
        folder: Application folder name (must already exist).
        filename: Document filename, e.g. 'resume.md' or 'cover_letter.md'.
        content: Full markdown content to write.
    """
    if Path(filename).suffix not in {".md", ".txt"}:
        return {"error": "Only .md and .txt files can be written."}

    app_dir = (APPLICATIONS_DIR / folder).resolve()
    target = (app_dir / filename).resolve()
    apps_root = APPLICATIONS_DIR.resolve()
    if apps_root not in app_dir.parents and app_dir != apps_root:
        return {"error": "Folder must be inside applications/."}
    if target.parent != app_dir:
        return {"error": "Filename must not contain path separators."}
    if not app_dir.is_dir():
        return {"error": f"Application folder not found: {folder}. Run create_application first."}

    target.write_text(content, encoding="utf-8")
    return {
        "folder": folder,
        "path": str(target),
        "bytes_written": len(content.encode("utf-8")),
        "message": f"Wrote {filename}.",
    }


def tool_get_prompt(prompt_path: str) -> dict:
    """Retrieve a specific prompt file by path (relative to .prompts/).
    Useful for AI hubs that want to load individual pipeline stages.

    Args:
        prompt_path: Relative path within .prompts/, e.g. 'core/cover_letter.md' or 'engineering/tailor_resume.md'.
    """
    content = _load_prompt(prompt_path)
    return {"path": prompt_path, "content": content}


# MCP protocol implementation
TOOLS = {
    "list_applications": {
        "fn": tool_list_applications,
        "description": "List all job applications with status and document completeness.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "create_application": {
        "fn": tool_create_application,
        "description": "Create a new application folder and save the job description.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company": {"type": "string", "description": "Company name"},
                "role": {"type": "string", "description": "Role/position title"},
                "job_description": {"type": "string", "description": "Full job description text"},
            },
            "required": ["company", "role", "job_description"],
        },
    },
    "get_pipeline_context": {
        "fn": tool_get_pipeline_context,
        "description": "Get the full orchestrator prompt and source material context to run the Career Architect pipeline in any AI hub.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "Application folder name (optional)"},
                "company": {"type": "string", "description": "Company name (optional)"},
                "role": {"type": "string", "description": "Role title (optional)"},
            },
            "required": [],
        },
    },
    "run_ats_score": {
        "fn": tool_run_ats_score,
        "description": "Run ATS keyword scoring on an application folder.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "Application folder name (optional)"},
                "company": {"type": "string", "description": "Company name (optional)"},
                "role": {"type": "string", "description": "Role title (optional)"},
            },
            "required": [],
        },
    },
    "build_resume": {
        "fn": tool_build_resume,
        "description": "Build PDF and DOCX artifacts from resume.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "Application folder name (optional)"},
                "template": {"type": "string", "description": "Template: default, minimal, creative, or executive", "default": "default"},
                "company": {"type": "string", "description": "Company name (optional)"},
                "role": {"type": "string", "description": "Role title (optional)"},
            },
            "required": [],
        },
    },
    "update_status": {
        "fn": tool_update_status,
        "description": "Update the status of an application (draft, applied, interview, rejected, offer).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "Application folder name"},
                "status": {"type": "string", "description": "New status: draft, applied, interview, rejected, offer"},
            },
            "required": ["folder", "status"],
        },
    },
    "get_prompt": {
        "fn": tool_get_prompt,
        "description": "Retrieve a specific prompt file by path relative to .prompts/ (e.g. 'core/cover_letter.md').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt_path": {"type": "string", "description": "Relative path within .prompts/"},
            },
            "required": ["prompt_path"],
        },
    },
}


def handle_request(request: dict) -> dict:
    method = request.get("method", "")
    req_id = request.get("id")

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def err(code, message):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

    if method == "initialize":
        return ok({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "career-architect", "version": "1.0.0"},
        })

    if method == "tools/list":
        tools = []
        for name, spec in TOOLS.items():
            tools.append({
                "name": name,
                "description": spec["description"],
                "inputSchema": spec["inputSchema"],
            })
        return ok({"tools": tools})

    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        args = params.get("arguments", {})

        if tool_name not in TOOLS:
            return err(-32601, f"Unknown tool: {tool_name}")

        try:
            result = TOOLS[tool_name]["fn"](**args)
            return ok({
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            })
        except Exception as e:
            return err(-32603, str(e))

    return err(-32601, f"Method not found: {method}")


def main():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
