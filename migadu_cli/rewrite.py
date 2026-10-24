"""Rewrite commands."""
import click
from .dependencies import make_client, _print, _handle_error

def register_rewrite_commands(cli):
    @cli.group(name="rewrite")
    def rewrite_group():
        """Manage pattern-based rewrites on a domain."""
        pass
    @rewrite_group.command(name="list")
    @click.option("--domain", default="")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def list_rewrites(ctx, domain, as_json):
        domain = domain or ctx.obj.get("domain", "")
        try:
            data = make_client(ctx, None, None).list_rewrites(domain)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @rewrite_group.command(name="get")
    @click.argument("domain")
    @click.argument("name")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def get_rewrite(ctx, domain, name, as_json):
        try:
            data = make_client(ctx, None, None).get_rewrite(domain, name)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @rewrite_group.command(name="create")
    @click.argument("domain")
    @click.argument("name")
    @click.option("--local-part-rule", required=True, help="Pattern e.g. demo-*")
    @click.option("--destinations", required=True, help="Comma-separated targets on same domain.")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def create_rewrite(ctx, domain, name, local_part_rule, destinations, as_json):
        try:
            data = make_client(ctx, None, None).create_rewrite(domain, name, local_part_rule, destinations)
            _print({"rewrite": data, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @rewrite_group.command(name="update")
    @click.argument("domain")
    @click.argument("name")
    @click.option("--new-name", help="New slug.")
    @click.option("--local-part-rule", help="New pattern.")
    @click.option("--destinations", help="Comma-separated targets.")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def update_rewrite(ctx, domain, name, new_name, local_part_rule, destinations, as_json):
        try:
            data = make_client(ctx, None, None).update_rewrite(domain, name,
                new_name=new_name, local_part_rule=local_part_rule, destinations=destinations)
            _print({"rewrite": data, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @rewrite_group.command(name="delete")
    @click.argument("domain")
    @click.argument("name")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def delete_rewrite(ctx, domain, name, as_json):
        try:
            make_client(ctx, None, None).delete_rewrite(domain, name)
            _print({"success": True, "deleted": name}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)