"""Build a skill ZIP; optionally include the offline customer tutorial."""
import argparse
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/entry-level-job-application"
GUIDE = ROOT / "docs/starter-kit"
FILES = ["SKILL.md", "agents/openai.yaml", "assets/application.example.json", "scripts/check_application.py", "scripts/application_state.py",
         "references/intake-and-privacy.md", "references/scoring.md", "references/mcp.md",
         "references/clients.md", "references/accounts-and-recovery.md", "references/captcha.md",
         "references/evidence.md", "references/execution.md"]
GUIDE_FILES = ["guide.html", "guide.pdf", "examples/README.md",
               "examples/codex-playwright.example.toml", "examples/codex-windows-optional.example.toml",
               "examples/claude-playwright.example.json", "examples/claude-windows-optional.example.json",
               "prompts/01-search-only.txt", "prompts/02-authorized-apply.txt"]


def package(output, with_guide=False):
    output = Path(output)
    if output.exists():
        raise FileExistsError("Choose a new output ZIP; existing artifacts are not overwritten")
    entries = [(SKILL / name, name) for name in FILES] + [(ROOT / "LICENSE", "LICENSE")]
    if with_guide:
        entries += [(GUIDE / name, name) for name in GUIDE_FILES]
        entries.append((ROOT / "docs/customer-start.txt", "先看这里.txt"))
    for path, _ in entries:
        if not path.is_file() or path.is_symlink() or ROOT.resolve() not in path.resolve().parents:
            raise ValueError("Missing or external package member")
    guide_html = None
    if with_guide:
        # Customers already have the skill; do not send them to a nested installer.
        guide_html = (GUIDE / "guide.html").read_text(encoding="utf-8")
        replacements = [
            ('<a class="head-link" href="entry-level-job-application.zip" download>下载技能安装包</a>',
             '<a class="head-link" href="#start" onclick="document.getElementById(\'tab-install\').click()">查看安装方法</a>'),
            ('<a href="entry-level-job-application.zip" download>下载技能 ZIP</a>，完整解压。',
             '将解压的整个技能文件夹命名为 <code>entry-level-job-application</code>。')
        ]
        for old, new in replacements:
            if old not in guide_html:
                raise ValueError("Tutorial install instructions changed; review customer packaging")
            guide_html = guide_html.replace(old, new)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, name in entries:
            if name == "guide.html":
                archive.writestr(name, guide_html)
            else:
                archive.write(path, name)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--with-guide", action="store_true",
                        help="Include optional Chinese guide and customer instructions")
    args = parser.parse_args()
    print(package(args.output, with_guide=args.with_guide))
