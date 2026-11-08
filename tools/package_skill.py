"""Build a self-contained skill ZIP from an explicit file allowlist."""
import argparse
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/entry-level-job-application"
FILES = ["SKILL.md", "agents/openai.yaml", "assets/application.example.json", "scripts/check_application.py", "scripts/application_state.py",
         "references/intake-and-privacy.md", "references/scoring.md", "references/mcp.md",
         "references/clients.md", "references/accounts-and-recovery.md", "references/captcha.md",
         "references/evidence.md", "references/execution.md"]


def package(output):
    output = Path(output)
    if output.exists():
        raise FileExistsError("Choose a new output ZIP; existing artifacts are not overwritten")
    entries = [(SKILL / name, name) for name in FILES] + [(ROOT / "LICENSE", "LICENSE")]
    for path, _ in entries:
        if not path.is_file() or path.is_symlink() or ROOT.resolve() not in path.resolve().parents:
            raise ValueError("Missing or external package member")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, name in entries:
            archive.write(path, name)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(package(args.output))
