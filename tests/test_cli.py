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
