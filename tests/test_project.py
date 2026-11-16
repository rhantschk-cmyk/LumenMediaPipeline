import json
import tempfile
import unittest
from pathlib import Path

from lumen_media.project import ProjectError, init_project, load_config


class ProjectTests(unittest.TestCase):
    def test_init_creates_layout_and_portable_lumen_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            project = init_project(Path(directory) / "demo")
            self.assertTrue((project / "exports").is_dir())
            config = load_config(project)
            self.assertEqual(config["profile"], "lumen")
            self.assertEqual(config["profile_defaults"]["export"]["video_codec"], "h264")

    def test_init_refuses_existing_project(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            init_project(project)
            with self.assertRaises(ProjectError):
                init_project(project)

    def test_init_rejects_unsupported_profile_without_creating_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"

            with self.assertRaisesRegex(ProjectError, "Unsupported profile: portable"):
                init_project(project, profile="portable")

            self.assertFalse(project.exists())

    def test_invalid_config_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / ".lumen-media.json").write_text(json.dumps({"version": 99}), encoding="utf-8")
            with self.assertRaises(ProjectError):
                load_config(project)


if __name__ == "__main__":
    unittest.main()
