"""Project configuration and filesystem operations for Lumen Media Pipeline."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict

CONFIG_FILENAME = ".lumen-media.json"
PROJECT_DIRECTORIES = ("inbox", "assets", "work", "projects", "exports", "archive")
PROFILE_LUMEN = "lumen"
ACTION_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class ProjectError(Exception):
    """Raised when a project cannot be read or changed."""


def project_path(value: str | Path) -> Path:
    """Return an absolute, normalized path without requiring it to exist."""
    return Path(value).expanduser().resolve()


def config_path(project: Path) -> Path:
    return project / CONFIG_FILENAME


def profile_defaults(profile: str) -> Dict[str, Any]:
    if profile != PROFILE_LUMEN:
        raise ProjectError("Unsupported profile: {0}".format(profile))
    # These values are portable metadata. They do not require Arch or any media tool.
    return {
        "description": "Portable Lumen workstation defaults; safe on Arch, macOS, NixOS, and other Linux.",
        "export": {
            "video_codec": "h264",
            "audio_codec": "aac",
            "crf": 18,
            "preset": "medium",
        },
    }


def new_config(profile: str) -> Dict[str, Any]:
    return {
        "version": 1,
        "profile": profile,
        "profile_defaults": profile_defaults(profile),
        "actions": {},
    }


def init_project(value: str | Path, profile: str = PROFILE_LUMEN) -> Path:
    """Create a project and its fixed layout without overwriting a config."""
    project = project_path(value)
    if config_path(project).exists():
        raise ProjectError(
            "A Lumen Media project already exists at {0}".format(project)
        )

    project.mkdir(parents=True, exist_ok=True)
    for name in PROJECT_DIRECTORIES:
        (project / name).mkdir(exist_ok=True)
    write_config(project, new_config(profile))
    return project


def load_config(project: Path) -> Dict[str, Any]:
    path = config_path(project)
    if not path.is_file():
        raise ProjectError(
            "No Lumen Media project found at {0}; run 'lumen-media init {0}' first."
            .format(project)
        )
    try:
        with path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectError("Cannot read {0}: {1}".format(path, exc)) from exc

    if not isinstance(config, dict) or config.get("version") != 1:
        raise ProjectError("Unsupported or invalid project config: {0}".format(path))
    if config.get("profile") != PROFILE_LUMEN:
        raise ProjectError("Unsupported project profile in {0}".format(path))
    if not isinstance(config.get("actions"), dict):
        raise ProjectError("Invalid actions in project config: {0}".format(path))
    return config


def write_config(project: Path, config: Dict[str, Any]) -> None:
    """Atomically persist project metadata using only the standard library."""
    destination = config_path(project)
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=str(project), delete=False
        ) as handle:
            json.dump(config, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temporary_name = handle.name
        os.replace(temporary_name, destination)
    except OSError as exc:
        raise ProjectError("Cannot write {0}: {1}".format(destination, exc)) from exc


def validate_action_name(name: str) -> None:
    if not ACTION_NAME_RE.fullmatch(name):
        raise ProjectError(
            "Invalid action name {0!r}; use letters, numbers, '.', '_', or '-' only."
            .format(name)
        )


def get_action_argv(config: Dict[str, Any], name: str) -> list[str]:
    action = config["actions"].get(name)
    if not isinstance(action, dict) or not isinstance(action.get("argv"), list):
        raise ProjectError("Action {0!r} is not configured.".format(name))
    argv = action["argv"]
    if not argv or not all(isinstance(item, str) and item for item in argv):
        raise ProjectError("Action {0!r} has an invalid command.".format(name))
    return argv
