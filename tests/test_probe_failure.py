import logging
from pathlib import Path
from envscan.detector import find_python_environments


def test_probe_failure_sets_probe_error(tmp_path, caplog):
    # Create a fake env with a 'bin/python' that is not a real interpreter
    fake = tmp_path / "fake_env"
    (fake / "bin").mkdir(parents=True)
    python_path = fake / "bin" / "python"
    python_path.write_text("this is not an executable")
    # Add a venv marker so the detector recognizes this directory as a venv
    (fake / "pyvenv.cfg").write_text("# fake venv")

    caplog.set_level(logging.INFO)
    res = find_python_environments(str(tmp_path), max_depth=2, probe=True, verbose=True)
    assert isinstance(res, list)
    assert len(res) == 1
    item = res[0]
    assert item.get("type") in ("venv", "virtualenv", "pipenv/poetry", "pyenv", "conda") or item.get("path").endswith("fake_env")

    # Since the interpreter is invalid, probing should have failed and probe_error present
    assert item.get("probe_error") == "probe failed"
    # Also we should have emitted an informational log (visible when verbose)
    assert any("Probe failed for interpreter" in rec.message for rec in caplog.records)
