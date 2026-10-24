"""Domain commands: list, get, create, update, records, diagnostics, activate, usage.

Follows the six principles:
1. API-first: thin wrapper over MigaduClient
2. Exit codes: 0 success, non-zero for config/4xx/5xx
3. stdout = clean data (--json), stderr = diagnostics
4. Idempotent by default where possible
5. Self-documenting via Click --help
"""
import click
from .dependencies import make_client, _print, _handle_error


def register_domain_commands(cli):
    @cli.group(name="domain")
    def domain_group():
        """Manage domains on your Migadu account."""
        pass

    @domain_group.command(name="list")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def list_domains(ctx, as_json):
        """List all domains for the authenticated account."""
        try:
            client = make_client(ctx, None, None)
            data = client.list_domains()
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @domain_group.command(name="get")
    @click.argument("name")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def get_domain(ctx, name, as_json):
        """Get full details for a specific domain."""
        try:
            client = make_client(ctx, None, None)
            data = client.get_domain(name)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @domain_group.command(name="create")
    @click.argument("name")
    @click.option("--hosted-dns/--no-hosted-dns", "hosted_dns", default=False,
                  help="Use Migadu's DNS (false recommended).")
    @click.option("--create-default-addresses/--no-create-default-addresses", "create_default_addresses", default=True,
                  help="Create admin/postmaster/abuse addresses (recommended).")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def create_domain(ctx, name, hosted_dns, create_default_addresses, as_json):
        """Create a new domain. Idempotent: if it already exists, returns existing domain."""
        try:
            client = make_client(ctx, None, None)
            data = client.create_domain(name, hosted_dns=hosted_dns,
                                        create_default_addresses=create_default_addresses)
            _print({"domain": data, "name": name, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @domain_group.command(name="update")
    @click.argument("name")
    @click.option("--description", help="Domain description.")
    @click.option("--tags", help="Comma-separated tags.")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def update_domain(ctx, name, description, tags, as_json):
        """Update domain fields. Idempotent: PATCH only sends changed fields."""
        try:
            client = make_client(ctx, None, None)
            data = client.update_domain(name, description=description,
                                        tags=tags)
            _print({"domain": data, "name": name, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @domain_group.command(name="records")
    @click.argument("name")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def get_domain_records(ctx, name, as_json):
        """Get DNS records needed to configure your domain externally."""
        try:
            client = make_client(ctx, None, None)
            data = client.get_domain_records(name)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @domain_group.command(name="diagnostics")
    @click.argument("name")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def get_domain_diagnostics(ctx, name, as_json):
        """Run DNS validation diagnostics on a domain."""
        try:
            client = make_client(ctx, None, None)
            data = client.get_domain_diagnostics(name)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @domain_group.command(name="activate")
    @click.argument("name")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def activate_domain(ctx, name, as_json):
        """Activate a domain once DNS records are configured (fails with 422 if DNS not ready)."""
        try:
            client = make_client(ctx, None, None)
            data = client.activate_domain(name)
            _print({"domain": data, "name": name, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @domain_group.command(name="usage")
    @click.argument("name")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def get_domain_usage(ctx, name, as_json):
        """Get message and storage usage metrics for a domain."""
        try:
            client = make_client(ctx, None, None)
            data = client.get_domain_usage(name)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    return domain_group