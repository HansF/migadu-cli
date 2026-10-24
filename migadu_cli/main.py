"""Main entry point for the Migadu CLI application.

Follows the six 37signals design principles for an API + CLI + Skills architecture:

1. **Start with a Solid API, Then Build a Clean CLI** — All commands thin-wrap the MigaduClient.
2. **Design for a Deterministic Execution Loop** — Predictable exit codes; stdout = data, stderr = errors.
3. **Machine-Readable Outputs (--json)** — Every command has a --json flag.
4. **Idempotency by Default** — Create/update commands use PATCH semantics; changes only what you specify.
5. **Clear, Self-Documenting Help Text** — Dynamic --help trees, no need for injected schemas upfront.
6. **Skills Are the Last Mile** — Workflow markdown guides live in the skills/ directory.

CLI structure:
  migadu domain    [list|get|create|update|records|diagnostics|activate|usage]
  migadu mailbox   [list|get|create|update|delete|reset-password|set-autoresponder]
  migadu alias     [list|get|create|update|delete]
  migadu identity  [list|get|create|update|delete]
  migadu forwarding [list|get|create|update|delete]
  migadu rewrite   [list|get|create|update|delete]
  migadu init      Initialize credentials
  migadu skills    List available workflow guides
"""
import click

from .domain import register_domain_commands
from .mailbox import register_mailbox_commands
from .alias import register_alias_commands
from .identity import register_identity_commands
from .forwarding import register_forwarding_commands
from .rewrite import register_rewrite_commands
from .config import load_config


@click.group(invoke_without_command=True)
@click.version_option("migadu-cli")
@click.option("--email", envvar="MIGADU_EMAIL", help="Migadu account email (or set MIGADU_EMAIL)")
@click.option("--api-key", envvar="MIGADU_API_KEY", help="Migadu API key (or set MIGADU_API_KEY)")
@click.option("--domain", envvar="MIGADU_DOMAIN", default=None, help="Default domain for operations")
@click.pass_context
def cli(ctx, email, api_key, domain):
    """Migadu API CLI wrapper — agent-friendly interface for email management."""
    # Initialize config if email/api-key provided
    if email or api_key:
        cfg = load_config(email=email, api_key=api_key, domain=domain)
        click.echo(f"Initialized Migadu CLI with account: {cfg['email']}", err=True)
    else:
        # Check env vars
        cfg = load_config()
        if cfg["email"]:
            click.echo(f"Using configured email: {cfg['email']}", err=True)
        else:
            click.echo("No credentials configured. Use `migadu init` or set MIGADU_EMAIL/MIGADU_API_KEY", err=True)

    ctx.ensure_object(dict)
    ctx.obj["domain"] = domain or cfg.get("default_domain", "")

    # If no subcommand given, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def register_cli_commands(cli):
    """Register all resource command groups."""
    register_domain_commands(cli)
    register_mailbox_commands(cli)
    register_alias_commands(cli)
    register_identity_commands(cli)
    register_forwarding_commands(cli)
    register_rewrite_commands(cli)
    register_skills_commands(cli)


def register_skills_commands(cli):
    @cli.command(name="skills")
    @click.option("--list", "list_skills", is_flag=True, help="List available workflow skills.")
    @click.pass_context
    def skills_cmd(ctx, list_skills):
        """Workflow skills — lightweight markdown guides."""
        import os, glob
        skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        if not os.path.exists(skills_dir):
            click.echo("No skills directory found at " + skills_dir, err=True)
            return
        files = sorted(glob.glob(os.path.join(skills_dir, "*.md")))
        if files:
            click.echo("Available skills (lightweight workflow guides):")
            for f in files:
                name = os.path.basename(f).replace(".md", "")
                click.echo(f"  - {name}")
            click.echo("\nThese are lightweight markdown instructions for agent workflows.")
            click.echo("Read them directly or ask your agent to apply them.")
        else:
            click.echo("No skills directory found.")


register_cli_commands(cli)


if __name__ == "__main__":
    cli()