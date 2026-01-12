import json
from click.testing import CliRunner
from envscan.cli import main


def test_cli_no_envs(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "No Python environments found" in result.output


def test_cli_json_output(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    (d / "pyvenv.cfg").write_text("# venv")
    runner = CliRunner()
    result = runner.invoke(main, ["--path", str(tmp_path), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 1
