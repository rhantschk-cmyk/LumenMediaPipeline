"""Command line interface for Lumen Media Pipeline."""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from .project import (
    PROJECT_DIRECTORIES,
    ProjectError,
    get_action_argv,
    init_project,
    load_config,
    project_path,
    validate_action_name,
    write_config,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lumen-media", description="Local-first media project pipeline.")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a media project")
    init.add_argument("path", nargs="?", default=".")
    init.add_argument("--profile", default="lumen", choices=["lumen"])

    status = sub.add_parser("status", help="show project state")
    status.add_argument("path", nargs="?", default=".")

    action = sub.add_parser("action", help="manage project actions")
    action_sub = action.add_subparsers(dest="action_command", required=True)
    action_set = action_sub.add_parser("set", help="store a command as an action")
    action_set.add_argument("name")
    action_set.add_argument("action_value")
    action_set.add_argument("path", nargs="?", default=".")
    action_run = action_sub.add_parser("run", help="run an action from the project root")
    action_run.add_argument("name")
    action_run.add_argument("path", nargs="?", default=".")

    sync = sub.add_parser("sync-exports", help="share exports via optional LumenLanDrop")
    sync.add_argument("path", nargs="?", default=".")
    sync.add_argument("--to", required=True, metavar="URL")
    sync.add_argument("--token", required=True, metavar="TOKEN")
    return parser


def _project(value: str) -> tuple[Path, dict]:
    path = project_path(value)
    return path, load_config(path)


def _status(project: Path, config: dict) -> None:
    payload = {
        "project": str(project),
        "profile": config["profile"],
        "directories": {name: str(project / name) for name in PROJECT_DIRECTORIES},
        "actions": config["actions"],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


def _set_action(project: Path, config: dict, name: str, command: str) -> None:
    validate_action_name(name)
    try:
        argv = shlex.split(command, posix=True)
    except ValueError as exc:
        raise ProjectError(f"Cannot parse action command: {exc}") from exc
    if not argv:
        raise ProjectError("Action command must not be empty.")
    config["actions"][name] = {"argv": argv}
    write_config(project, config)
    print(f"Configured action {name!r} in {project}")


def _run_action(project: Path, config: dict, name: str) -> int:
    validate_action_name(name)
    argv = get_action_argv(config, name)
    print("Running:", shlex.join(argv))
    completed = subprocess.run(argv, cwd=project, shell=False, check=False)
    return completed.returncode


def _sync_exports(project: Path, target: str, token: str) -> int:
    executable = shutil.which("lumen-landrop")
    if not executable:
        raise ProjectError(
            "LumenLanDrop is optional and is not installed. Install lumen-landrop, then retry sync-exports."
        )
    exports = project / "exports"
    if not exports.is_dir():
        raise ProjectError(f"Missing exports directory: {exports}")
    return subprocess.run(
        [executable, "send", "--to", target, "--token", token, str(exports)],
        cwd=project,
        shell=False,
        check=False,
    ).returncode


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "init":
            project = init_project(args.path, args.profile)
            print(f"Initialized Lumen Media project at {project}")
            return 0
        project, config = _project(args.path)
        if args.command == "status":
            _status(project, config)
            return 0
        if args.command == "action" and args.action_command == "set":
            _set_action(project, config, args.name, args.action_value)
            return 0
        if args.command == "action" and args.action_command == "run":
            return _run_action(project, config, args.name)
        if args.command == "sync-exports":
            return _sync_exports(project, args.to, args.token)
        raise ProjectError("Unsupported command")
    except ProjectError as exc:
        print(f"lumen-media: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
