"""Simple Python environment detection utilities.

This module is deliberately conservative: it only looks for file markers
that indicate a virtual environment or environment manager. It avoids
running arbitrary code by default.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional, Set

from .utils import is_hidden


def find_python_environments(path: str = '.', max_depth: int = 3, include_hidden: bool = False, follow_symlinks: bool = False, probe: bool = False, verbose: bool = False) -> List[Dict]:
    """Recursively scan `path` for well-known Python environment markers.

    Returns a list of dicts with keys: path, type, name, python (optional), source.
    When `probe=True` the function will attempt to run the environment's Python
    interpreter (if found) to gather a version string. Probing is time-limited
    and optional to avoid running arbitrary code by default.

    When `verbose=True`, the function will emit informational logs when probing
    fails so the user can get diagnostic information.
    """
    import logging

    base = Path(path)
    results: List[Dict] = []
    seen: Set[str] = set()

    def _key_for_path(p: Path) -> str:
        try:
            st = p.stat()
            return f"{st.st_dev}:{st.st_ino}"
        except Exception:
            return str(p.resolve())

    def _scan_dir(p: Path, depth: int):
        if depth > max_depth:
            return
        key = _key_for_path(p)
        if key in seen:
            return
        seen.add(key)

        # Check the directory itself for environment markers
        d = detect_env_at_path(p)
        if d:
            # Optionally probe interpreter to get python version
            if probe:
                interp = find_interpreter_for_env(p)
                if interp:
                    info = probe_interpreter(interp)
                    if info and info.get("version"):
                        d["python"] = info.get("version")
                        d["interpreter"] = interp
                    else:
                        # Populate a short probe_error field and optionally log
                        d["python"] = None
                        d["probe_error"] = "probe failed"
                        if verbose:
                            import logging
                            logging.info(f"Probe failed for interpreter: {interp}")
            results.append(d)
            # Do not traverse inside detected environment directories
            return

        # Otherwise traverse children
        try:
            for child in sorted(p.iterdir()):
                if child.is_dir():
                    if not include_hidden and is_hidden(child):
                        continue
                    _scan_dir(child, depth + 1)
        except PermissionError:
            return
        except FileNotFoundError:
            return

    _scan_dir(base, 0)
    return results


def find_interpreter_for_env(p: Path) -> Optional[str]:
    """Return the path to a likely python interpreter inside environment `p`.

    Checks common locations (`Scripts/python.exe` on Windows, `bin/python` on Unix).
    """
    # Windows venv layout
    win_path = p / "Scripts" / "python.exe"
    if win_path.exists():
        return str(win_path)
    # Unix-like layout
    bin_path = p / "bin" / "python"
    if bin_path.exists():
        return str(bin_path)
    return None


def detect_env_at_path(p: Path) -> Optional[Dict]:
    """Detect whether a path appears to be a Python environment.

    Heuristics used:
    - venv: presence of pyvenv.cfg
    - virtualenv: presence of bin/activate or Scripts/activate
    - conda: presence of conda-meta directory
    - pipenv/poetry: presence of Pipfile or poetry.lock
    - pyenv: presence of .python-version
    """
    if not p.exists():
        return None

    # venv
    if (p / "pyvenv.cfg").exists():
        return {"path": str(p), "type": "venv", "name": p.name, "python": None, "source": "pyvenv.cfg"}

    # virtualenv (activate scripts)
    if (p / "bin" / "activate").exists() or (p / "Scripts" / "activate").exists():
        return {"path": str(p), "type": "virtualenv", "name": p.name, "python": None, "source": "activate script"}

    # conda
    if (p / "conda-meta").is_dir():
        return {"path": str(p), "type": "conda", "name": p.name, "python": None, "source": "conda-meta"}

    # pipenv / poetry
    if (p / "Pipfile").exists() or (p / "poetry.lock").exists():
        return {"path": str(p), "type": "pipenv/poetry", "name": p.name, "python": None, "source": "Pipfile/poetry.lock"}

    # pyenv marker
    if (p / ".python-version").exists():
        return {"path": str(p), "type": "pyenv", "name": p.name, "python": None, "source": ".python-version"}

    return None


# Optional: helper to probe interpreter for python version (not used by default)
def probe_interpreter(interpreter_path: str) -> Optional[Dict]:
    """Run interpreter and fetch a minimal JSON with version info.

    Returns a dict with key 'version' on success, otherwise None.
    This function suppresses stderr and uses a short timeout.
    """
    try:
        import subprocess, json, logging
        # Request only the short version string to keep output concise
        cmd = [interpreter_path, "-c", "import sys, json; print(json.dumps({'version': sys.version.split()[0]}))"]
        out = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.DEVNULL, timeout=3)
        data = json.loads(out)
        return {"version": data.get("version")}
    except Exception as e:
        # Log debug details; informational messages are emitted by callers when verbose
        logging.debug(f"probe_interpreter failed for {interpreter_path}: {e}")
        return None
