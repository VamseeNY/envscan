import os
from pathlib import Path
from envscan.detector import detect_env_at_path, find_python_environments


def test_detect_venv_pyvenv_cfg(tmp_path):
    d = tmp_path / "project_venv"
    d.mkdir()
    (d / "pyvenv.cfg").write_text("# venv")
    res = detect_env_at_path(d)
    assert res is not None
    assert res["type"] == "venv"


def test_detect_virtualenv_activate(tmp_path):
    d = tmp_path / "venv2"
    (d / "bin").mkdir(parents=True)
    (d / "bin" / "activate").write_text("# activate")
    res = detect_env_at_path(d)
    assert res is not None
    assert res["type"] in ("virtualenv",)


def test_detect_conda(tmp_path):
    d = tmp_path / "conda_env"
    (d / "conda-meta").mkdir(parents=True)
    res = detect_env_at_path(d)
    assert res is not None
    assert res["type"] == "conda"


def test_find_with_depth_limit(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "level1").mkdir()
    (root / "level1" / "level2").mkdir()
    (root / "level1" / "level2" / "venv").mkdir(parents=True)
    (root / "level1" / "level2" / "venv" / "pyvenv.cfg").write_text("# venv")

    res = find_python_environments(root, max_depth=1)
    assert res == []

    res2 = find_python_environments(root, max_depth=3)
    assert len(res2) == 1
