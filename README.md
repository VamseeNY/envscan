# envscan — CLI to discover Python environments

envscan is a small, open-source command-line tool that scans a directory tree and reports local Python environments (venv/virtualenv, conda envs, pipenv/poetry markers, pyenv markers).

Install
-------

```bash
# From PyPI (after release)
pip install envscan

# From source (development)
python -m pip install -e .
```

Quick start
-----------

- Scan the current directory (text output):

```bash
envscan
```

- Scan a specific directory and print JSON:

```bash
envscan --path ./project --format json
```

- Probe detected environments to get Python version (optional and time-limited):

```bash
envscan --probe --verbose
```

Command summary
---------------
- `-p, --path PATH` : Path to scan (default `.`)
- `-d, --depth INT` : Max recursion depth (default `3`)
- `-f, --format {text,json}` : Output format (default `text`)
- `--include-hidden` : Include hidden directories and files
- `--follow-symlinks` : Follow symbolic links
- `--probe` : Probe discovered environments to get Python version (optional, time-limited)
- `--json-file PATH` : Write JSON output to the given file
- `-v, --verbose` : Verbose output (shows probe diagnostic logs)

Notes
-----
- By default envscan uses conservative file-marker heuristics (e.g., presence of `pyvenv.cfg`, `conda-meta`, `Pipfile`, `.python-version`) and does not execute any discovered interpreters. Use `--probe` to request a safe, short, time-limited interpreter probe when available.
- The optional Streamlit visualization from the original project is preserved as a `web` extra (installable via `pip install envscan[web]`) and can be run with `streamlit run app.py` in the repository; however the primary focus of this package is the `envscan` CLI.

Contributing
------------
Contributions welcome — open a PR with tests.

License
-------
MIT

---


### Extending Functionality

To add more features:

1. **File type categorization**: Extend the `get_file_type_group` function in `directory_scanner.py`
2. **Additional statistics**: Modify the `calculate_directory_stats` function in `app.py`
3. **UI improvements**: Add more Streamlit components in `app.py`

## License

This project is open-source and available under the MIT License.
