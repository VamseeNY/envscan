import json
import sys
import click
from pathlib import Path

from . import __version__
from .detector import find_python_environments


@click.command()
@click.version_option(version=__version__, prog_name='envscan')
@click.option("--path", "path", default='.', help="Path to scan")
@click.option("--depth", "depth", default=3, type=int, help="Max depth to scan")
@click.option("--format", "out_format", default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option("--include-hidden", is_flag=True, default=False, help="Include hidden files and directories")
@click.option("--follow-symlinks", is_flag=True, default=False, help="Follow symlinks")
@click.option("--probe", is_flag=True, default=False, help="Probe discovered environments to get Python version (optional, time-limited)")
@click.option("--json-file", default=None, help="Write JSON output to file")
@click.option("--verbose", "verbose", is_flag=True, default=False, help="Verbose output")
def main(path, depth, out_format, include_hidden, follow_symlinks, probe, json_file, verbose):
    """envscan - scan a directory for Python environments"""
    import logging
    if verbose:
        logging.basicConfig(level=logging.INFO)

    try:
        results = find_python_environments(path, max_depth=depth, include_hidden=include_hidden, follow_symlinks=follow_symlinks, probe=probe, verbose=verbose)
    except Exception as e:
        click.echo(f"Error scanning for environments: {e}", err=True)
        sys.exit(2)

    if out_format == 'json':
        text = json.dumps(results, indent=2)
        click.echo(text)
        if json_file:
            try:
                Path(json_file).write_text(text, encoding='utf-8')
                if verbose:
                    click.echo(f"Wrote JSON to {json_file}")
            except Exception as e:
                click.echo(f"Failed to write JSON file: {e}", err=True)
                sys.exit(3)
    else:
        if not results:
            click.echo("No Python environments found.")
            sys.exit(0)
        for r in results:
            click.echo(f"{r.get('path')} — {r.get('type')} — {r.get('name','')} — {r.get('python','')}")


if __name__ == '__main__':
    main()
