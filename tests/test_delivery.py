import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DeliveryTests(unittest.TestCase):
    def test_demo_runs_actual_guards_and_labels_simulation(self):
        report = module("demo").run_demo()
        self.assertTrue(report["passed"])
        self.assertEqual(report["evaluation_type"], "simulation_only")
        self.assertEqual(report["external_submissions"], 0)
        self.assertEqual(report["payment_transactions"], 0)
        self.assertTrue(any(not c["actual_ready"] for c in report["cases"]))
        self.assertEqual(report["final_state"], "submitted")

    def test_package_has_only_declared_members_and_does_not_overwrite(self):
        builder = module("package_skill")
        with tempfile.TemporaryDirectory(prefix="job-skill-package-", dir=ROOT.parent) as folder:
            self.assertEqual(Path(folder).resolve().parent, ROOT.parent.resolve())
            output = Path(folder) / "skill.zip"
            builder.package(output)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(set(archive.namelist()), set(builder.FILES + ["LICENSE"]))
                self.assertIn("scripts/application_state.py", archive.namelist())
                self.assertFalse(any("private" in name or name.endswith(".sqlite") for name in archive.namelist()))
            before = output.read_bytes()
            with self.assertRaises(FileExistsError):
                builder.package(output)
            self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
