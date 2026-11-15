import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lumen_media import __version__
from lumen_media.cli import main
from lumen_media.project import load_config


class CliTests(unittest.TestCase):
    def test_version_prints_package_version(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(output.getvalue(), f"lumen-media {__version__}\n")

    def test_init_reports_a_clear_error_when_target_is_a_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "not-a-project-directory"
            target.write_text("keep this file", encoding="utf-8")
            errors = io.StringIO()

            with contextlib.redirect_stderr(errors):
                self.assertEqual(main(["init", str(target)]), 2)

            self.assertEqual(
                errors.getvalue(),
                f"lumen-media: Project path exists but is not a directory: {target}\n",
            )
            self.assertEqual(target.read_text(encoding="utf-8"), "keep this file")

    def test_action_list_prints_configured_action_names_in_sorted_order(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            self.assertEqual(main(["init", str(project)]), 0)
            self.assertEqual(
                main(["action", "set", "zebra", "python -V", str(project)]),
                0,
            )
            self.assertEqual(
                main(["action", "set", "alpha", "python -c pass", str(project)]),
                0,
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["action", "list", str(project)]), 0)

            self.assertEqual(output.getvalue(), "alpha\nzebra\n")

    def test_action_remove_deletes_a_configured_action(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            self.assertEqual(main(["init", str(project)]), 0)
            self.assertEqual(
                main(["action", "set", "preview", "python -V", str(project)]),
                0,
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(
                    main(["action", "remove", "preview", str(project)]),
                    0,
                )

            self.assertEqual(output.getvalue(), "Removed action 'preview' from " + str(project) + "\n")
            self.assertNotIn("preview", load_config(project)["actions"])

    def test_module_version_prints_package_version(self):
        environment = os.environ.copy()
        source_directory = Path(__file__).resolve().parents[1] / "src"
        environment["PYTHONPATH"] = os.pathsep.join(
            filter(None, (str(source_directory), environment.get("PYTHONPATH")))
        )

        completed = subprocess.run(
            [sys.executable, "-m", "lumen_media", "--version"],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, f"lumen-media {__version__}\n")


if __name__ == "__main__":
    unittest.main()
