"""Command-line entry point for provider selection and synchronization."""

from __future__ import annotations

import argparse
from pathlib import Path

from .bridge import PROVIDERS, use_provider


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="use-adapter")
    parser.add_argument("provider", nargs="?", choices=PROVIDERS, default="codex")
    parser.add_argument("--project", default=".", help="Project root (default: current directory)")
    parser.add_argument("--agents-root", help="Canonical agents repository (default: .agents)")
    parser.add_argument("--sync-only", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--skip-executable-check", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(arguments)
    try:
        result = use_provider(
            Path(args.project),
            args.provider,
            check_executable=not args.skip_executable_check and not args.sync_only,
            agents_root=Path(args.agents_root) if args.agents_root else None,
            save_selection=not args.sync_only,
        )
    except RuntimeError as error:
        parser.error(str(error))
    print(f"Adapter: {result['provider']}")
    print(f"Agents repository: {result['agents_root']}")
    print(f"Executable: {result['executable'] or 'not checked'}")
    print(f"Agents: {result['agents']}")
    print(f"Skills: {result['skills']}")
    print(f"Commands: {result['commands']}")
    print("Status: synchronized" if args.sync_only else "Status: ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
