"""Thin compatibility wrapper for the top-level `cli` module.

The canonical CLI entrypoint is now `envscan.cli:main` (packaged). This
module imports and delegates to the packaged `envscan.cli.main` so that
`python -m cli.main` still works in the development checkout.
"""

from envscan.cli import main

if __name__ == '__main__':
    main()
