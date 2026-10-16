from pathlib import Path

import pytest

from agent_bridge.bridge import selected_provider, sync_provider, use_provider


def make_agents_root(tmp_path: Path) -> Path:
    root = tmp_path / "canonical-agents"
    files = {
        "AGENTS.md": "# Canonical workflow\n",
        "rules/common.md": "# Common rules\n",
        "hooks/lifecycle.json": '{"instructions":{"pre_task":"hooks/pre-task.md"}}\n',
        "hooks/pre-task.md": "# Pre-task\n",
        "base/AGENTS.md": "# Base workflow\n",
        "base/agents/reviewer.md": (
            "---\nname: reviewer\ndescription: Review changes.\n---\n\nReview carefully.\n"
        ),
        "base/skills/base-check/SKILL.md": (
            "---\nname: base-check\ndescription: Check the base.\n---\n\nCheck it.\n"
        ),
        "base/commands/build.md": "---\ndescription: Build safely.\n---\n\nBuild.\n",
        "base/hooks/lifecycle.json": ('{"instructions":{"pre_task":"hooks/pre-task.md"}}\n'),
        "base/hooks/pre-task.md": "# Base pre-task\n",
        "skills/start-build/SKILL.md": (
            "---\nname: start-build\ndescription: Start the build.\n---\n\nStart.\n"
        ),
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def test_codex_is_default_without_selection(tmp_path: Path) -> None:
    assert selected_provider(tmp_path) == "codex"


def test_claude_projection_and_selection(tmp_path: Path) -> None:
    root = make_agents_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    result = use_provider(project, "claude", check_executable=False, agents_root=root)

    assert result["agents"] == 1
    assert result["skills"] == 2
    assert result["commands"] == 2
    assert selected_provider(project) == "claude"
    assert (project / ".claude/agents/reviewer.md").is_file()
    assert (project / ".claude/skills/start-build/SKILL.md").is_file()
    assert (project / ".claude/commands/start-build.md").is_file()
    assert "hooks/pre-task.md" in (project / "CLAUDE.md").read_text(encoding="utf-8")
    assert ".agent-bridge-state/" in (project / ".gitignore").read_text(encoding="utf-8")


def test_opencode_and_gemini_native_formats(tmp_path: Path) -> None:
    root = make_agents_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    sync_provider(project, "opencode", agents_root=root)
    sync_provider(project, "gemini", agents_root=root)

    assert "mode: subagent" in (project / ".opencode/agents/reviewer.md").read_text(
        encoding="utf-8"
    )
    assert '"instructions"' in (project / "opencode.json").read_text(encoding="utf-8")
    assert "kind: local" in (project / ".gemini/agents/reviewer.md").read_text(encoding="utf-8")
    assert "{{args}}" in (project / ".gemini/commands/start-build.toml").read_text(encoding="utf-8")


def test_sync_only_does_not_change_selection(tmp_path: Path) -> None:
    root = make_agents_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    use_provider(project, "claude", check_executable=False, agents_root=root)

    use_provider(
        project,
        "opencode",
        check_executable=False,
        agents_root=root,
        save_selection=False,
    )

    assert selected_provider(project) == "claude"


def test_refuses_to_overwrite_edited_generated_file(tmp_path: Path) -> None:
    root = make_agents_root(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    sync_provider(project, "claude", agents_root=root)
    generated = project / ".claude/agents/reviewer.md"
    generated.write_text("locally edited\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="edited locally"):
        sync_provider(project, "claude", agents_root=root)
