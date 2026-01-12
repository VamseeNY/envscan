import sys
import subprocess
import json
from pathlib import Path
from click.testing import CliRunner
from cli.main import main


def test_probe_populates_python(tmp_path):
    # Create a real venv using current Python
    repo_venv = tmp_path / "repo_venv"
    subprocess.check_call([sys.executable, "-m", "venv", str(repo_venv)])

    runner = CliRunner()
    result = runner.invoke(main, ["--path", str(tmp_path), "--format", "json", "--probe"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) >= 1

    # Find our repo_venv entry
    found = None
    for item in data:
        if str(Path(item["path"]).resolve()).endswith("repo_venv"):
            found = item
            break
    assert found is not None
    # Probe should populate a short version string like '3.9.12' or similar
    assert found.get("python") is not None
    assert isinstance(found.get("python"), str)
    assert found.get("python").startswith("3")
