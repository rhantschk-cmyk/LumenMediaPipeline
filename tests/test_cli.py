import contextlib
import io
import os
import subprocess
import sys
import unittest
from pathlib import Path

from lumen_media import __version__
from lumen_media.cli import main


class CliTests(unittest.TestCase):
    def test_version_prints_package_version(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(output.getvalue(), f"lumen-media {__version__}\n")

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
