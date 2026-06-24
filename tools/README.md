# tools/

Agent integration files for non-Claude LLMs and frameworks.

| File | Purpose |
|---|---|
| `openai_tools.json` | OpenAI-compatible function calling schema — works with GPT-4o, Gemini, Mistral, and any LLM that accepts OpenAI tool format |
| `langchain_tools.py` | LangChain `@tool` wrappers — import `get_career_tools()` for use with LangChain agents, LangGraph, or CrewAI |

See [AGENTS.md](../AGENTS.md) for usage examples for each integration.
