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

    def test_customer_package_includes_optional_guide_without_nested_installer(self):
        from html.parser import HTMLParser

        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.links = []

            def handle_starttag(self, tag, attrs):
                self.links.extend(value for key, value in attrs if key in ("href", "src"))

        builder = module("package_skill")
        with tempfile.TemporaryDirectory(prefix="job-customer-package-", dir=ROOT.parent) as folder:
            output = Path(folder) / "customer.zip"
            builder.package(output, with_guide=True)
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                self.assertEqual(names, set(builder.FILES + ["LICENSE"] + builder.GUIDE_FILES + ["先看这里.txt"]))
                self.assertFalse(any(name.endswith(".zip") for name in names))
                self.assertIsNone(archive.testzip())
                for name in builder.FILES:
                    self.assertEqual(archive.read(name), (builder.SKILL / name).read_bytes())
                guide = archive.read("guide.html").decode("utf-8")
                self.assertIn("这是可选教程，不是投递页面", guide)
                self.assertIn("查看安装方法", guide)
                self.assertIn("会用的客户直接跳过", archive.read("先看这里.txt").decode("utf-8"))
                links = Links()
                links.feed(guide)
                for link in links.links:
                    if link and not link.startswith(("#", "https://", "http://")):
                        self.assertIn(link, names)
            with self.assertRaises(FileExistsError):
                builder.package(output, with_guide=True)


if __name__ == "__main__":
    unittest.main()
