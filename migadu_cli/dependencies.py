"""Shared CLI state and helpers.

Principles implemented here:
- stdout (clean data) is separated from stderr (diagnostics).
- Standardized exit codes: 0=ok, 1=general error, 2=config/auth, 4=not found.
- Every command yields clean data; error diagnostics go to stderr only.
"""
import functools
import json
import sys
import click
from .config import load_config
from .client import MigaduClient, Auth, MigaduAPIError


def make_client(ctx, param, value):
    """Click callback that builds a MigaduClient from config/env."""
    del param, value  # we ignore the callback's argument
    cfg = load_config()
    if not cfg["email"] or not cfg["api_key"]:
        raise click.ClickException(
            "Missing credentials. Set MIGADU_EMAIL/MIGADU_API_KEY env vars or run `migadu init`"
        )
    domain = ctx.obj.get("domain") if ctx.obj else (cfg["default_domain"] or "")
    client = MigaduClient(Auth(cfg["email"], cfg["api_key"]))
    ctx.obj["client"] = client
    ctx.obj["domain"] = domain
    return client


def _print(obj, as_json):
    """Write clean result to stdout: JSON or compact, never diagnostics."""
    if as_json:
        click.echo(json.dumps(obj))
    else:
        click.echo(json.dumps(obj, indent=2))


def _handle_error(exc):
    """Map API errors to exit codes. Diagnostics to stderr only."""
    if isinstance(exc, MigaduAPIError):
        click.echo(f"API error ({exc.status_code}): {exc}", err=True)
        if exc.status_code == 401:
            sys.exit(2)
        if exc.status_code == 404:
            sys.exit(4)
        if exc.status_code == 422:
            sys.exit(3)
        sys.exit(1)
    click.echo(f"Error: {exc}", err=True)
    sys.exit(1)