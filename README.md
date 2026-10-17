# Agent Bridge

`agent-bridge` projects a canonical `.agents` workflow repository into the native project
structures used by Codex, Claude Code, OpenCode, Gemini CLI, and Cursor. The canonical agents, skills,
commands, rules, policies, and lifecycle instructions remain owned by `.agents`; generated provider
files are adapters rather than independent copies to maintain manually.

## Install in a project

The normal installation is a nested submodule of the canonical `agents` repository:

```bash
git submodule add https://github.com/Dolan001/agents.git .agents
git -C .agents submodule update --init agent-bridge
```

Codex is the default when no adapter has been selected. Select another provider with one command:

```bash
./.agents/use-adapter claude
./.agents/use-adapter opencode
./.agents/use-adapter gemini
./.agents/use-adapter cursor
./.agents/use-adapter codex
```

Running `./.agents/use-adapter` without a provider also selects Codex. The wrapper delegates to this
repository at `.agents/agent-bridge` while keeping the user-facing command stable.

The bridge validates that the selected provider executable is installed, generates its native
project files, and stores the local selection in the gitignored
`.agent-bridge-state/selected-adapter` file.

## Generated structures

| Provider | Generated project files |
|---|---|
| Codex | Managed workflow references in `AGENTS.md` |
| Claude Code | `.claude/agents`, `.claude/skills`, `.claude/commands`, `CLAUDE.md` |
| OpenCode | `.opencode/agents`, `.opencode/skills`, `.opencode/commands`, `opencode.json`, `AGENTS.md` |
| Gemini CLI | `.gemini/agents`, `.gemini/skills`, `.gemini/commands`, `.gemini/settings.json`, `GEMINI.md` |
| Cursor | `.cursor/agents`, `.cursor/skills`, `.cursor/commands`, `.cursor/rules`, `AGENTS.md` |

Generated files are hash-tracked. The bridge refuses to overwrite a generated file that was edited
locally. Existing unrelated provider configuration is preserved and extended.

## Synchronization contract

The `agents` workflow refreshes the active projection before launching a provider:

```bash
./.agents/agent-bridge/use-adapter claude \
  --project . \
  --agents-root ./.agents \
  --sync-only
```

`--sync-only` does not change the saved provider and does not require the provider executable. It is
intended for workflow integration; normal users only need the short selection commands above.

## Development

```bash
python3 -m venv .venv
./.venv/bin/pip install -e . pytest ruff mypy
./.venv/bin/pytest
./.venv/bin/ruff check .
./.venv/bin/mypy src
```
