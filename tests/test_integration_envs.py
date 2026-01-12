import json
from pathlib import Path
from click.testing import CliRunner
from envscan.cli import main


def test_integration_detects_two_envs(tmp_path):
    # Create venv-like fixtures
    repo_venv = tmp_path / "repo_venv"
    repo_venv.mkdir()
    (repo_venv / "pyvenv.cfg").write_text("# venv")

    sample = tmp_path / "sample_project"
    sample.mkdir()
    v_in = sample / "venv_inside"
    v_in.mkdir(parents=True)
    (v_in / "pyvenv.cfg").write_text("# venv")

    runner = CliRunner()
    result = runner.invoke(main, ["--path", str(tmp_path), "--format", "json"])
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 2

    paths = [Path(item["path"]) for item in data]
    # Ensure both created envs are found
    assert any(p.samefile(repo_venv) for p in paths)
    assert any(p.samefile(v_in) for p in paths)

    # Ensure types and python field expectations
    for item in data:
        assert item["type"] == "venv"
        assert item["python"] is None
