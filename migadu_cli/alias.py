"""Alias commands."""
import click
from .dependencies import make_client, _print, _handle_error

def register_alias_commands(cli):
    @cli.group(name="alias")
    def alias_group():
        """Manage aliases on a domain."""
        pass
    @alias_group.command(name="list")
    @click.option("--domain", default="")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def list_aliases(ctx, domain, as_json):
        domain = domain or ctx.obj.get("domain", "")
        try:
            data = make_client(ctx, None, None).list_aliases(domain)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @alias_group.command(name="get")
    @click.argument("domain")
    @click.argument("local_part")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def get_alias(ctx, domain, local_part, as_json):
        try:
            data = make_client(ctx, None, None).get_alias(domain, local_part)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @alias_group.command(name="create")
    @click.argument("domain")
    @click.argument("local_part")
    @click.option("--destinations", required=True, help="Comma-separated targets.")
    @click.option("--is-internal/--no-is-internal", "is_internal", default=False)
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def create_alias(ctx, domain, local_part, destinations, is_internal, as_json):
        try:
            data = make_client(ctx, None, None).create_alias(domain, local_part, destinations, is_internal)
            _print({"alias": data, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @alias_group.command(name="update")
    @click.argument("domain")
    @click.argument("local_part")
    @click.option("--destinations", help="Comma-separated targets.")
    @click.option("--is-internal/--no-is-internal", "is_internal", default=None)
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def update_alias(ctx, domain, local_part, destinations, is_internal, as_json):
        try:
            data = make_client(ctx, None, None).update_alias(domain, local_part, destinations=destinations, is_internal=is_internal)
            _print({"alias": data, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @alias_group.command(name="delete")
    @click.argument("domain")
    @click.argument("local_part")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def delete_alias(ctx, domain, local_part, as_json):
        try:
            make_client(ctx, None, None).delete_alias(domain, local_part)
            _print({"success": True, "deleted": f"{local_part}@{domain}"}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
