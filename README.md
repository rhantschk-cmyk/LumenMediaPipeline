# Lumen Media Pipeline

A small, cross-platform foundation for organizing media projects and running your own repeatable media commands. It has **no runtime dependencies outside Python's standard library**.

## Install

```bash
python -m pip install .
```

For development without installation:

```bash
python -m unittest discover -s tests -v
PYTHONPATH=src python -m lumen_media --version
PYTHONPATH=src python -m lumen_media init demo
```

## Quick start

```bash
# Create a project using the default, explicit "lumen" profile.
lumen-media init ~/Media/my-film

# Inspect its paths, selected profile, profile defaults, and configured actions.
lumen-media status ~/Media/my-film

# Store an action. Quote the complete command when it contains arguments.
lumen-media action set transcode "ffmpeg -i inbox/clip.mov exports/clip.mp4" ~/Media/my-film

# Run it without a shell. The command is split into an argument list and runs from the project root.
lumen-media action run transcode ~/Media/my-film
```

A project contains:

```text
.lumen-media.json
inbox/       # newly received source material
assets/      # reusable assets (graphics, fonts, audio)
work/        # intermediate media and scratch work
projects/    # editor/project files
exports/     # deliverables to publish or transfer
archive/     # completed source material and old deliverables
```

## Profiles and platform behavior

`init` defaults to the explicit `lumen` profile; use `--profile lumen` to state it in scripts.
The profile provides practical, portable defaults for a Lumen/Arch workstation: organized working paths and conventional export preferences (`h264/aac`, `crf=18`, `preset=medium`). These are configuration metadata, not installed commands. Lumen Media Pipeline does not call `pacman`, assume `/usr/bin`, modify the OS, or require an Arch-only tool, so the same project works on macOS, NixOS, and other Linux systems.

```bash
lumen-media init --profile lumen ~/Media/my-film
```

## Actions

Actions are intentionally user-defined because available media tools differ by machine. `action set` parses the command with Python's `shlex` and `action run` executes the resulting argument vector with `shell=False`; shell operators such as `|`, `>`, and `&&` are therefore not interpreted. Use a small wrapper script if you need shell pipelines.

```bash
lumen-media action set thumbnails "python tools/thumbnails.py inbox exports" .
lumen-media action list .
lumen-media action run thumbnails .
# Remove an obsolete saved command without touching project media.
lumen-media action remove thumbnails .
```

## Optional LumenLanDrop integration

To share `exports/`, install the separately distributed `lumen-landrop` CLI and run:

```bash
lumen-media sync-exports ~/Media/my-film --to https://receiver.example --token TOKEN
```

The command invokes exactly:

```text
lumen-landrop send --to URL --token TOKEN PATH_TO_EXPORTS
```

It never stores or prints the token. If `lumen-landrop` is not installed, the command exits with a clear optional-integration message.

## Commands

```text
lumen-media --version
lumen-media init [PATH] [--profile lumen]
lumen-media status [PATH]
lumen-media action set NAME COMMAND [PATH]
lumen-media action list [PATH]
lumen-media action remove NAME [PATH]
lumen-media action run NAME [PATH]
lumen-media sync-exports [PATH] --to URL --token TOKEN
```

`PATH` defaults to the current directory except `init`, whose default is `.`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
