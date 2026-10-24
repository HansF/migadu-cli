"""Forwarding commands."""
import click
from .dependencies import make_client, _print, _handle_error

def register_forwarding_commands(cli):
    @cli.group(name="forwarding")
    def forwarding_group():
        """Manage forwardings on a mailbox."""
        pass
    @forwarding_group.command(name="list")
    @click.option("--domain", default="")
    @click.option("--mailbox", default="")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def list_forwardings(ctx, domain, mailbox, as_json):
        domain = domain or ctx.obj.get("domain", "")
        if not domain or not mailbox:
            raise click.ClickException("Domain and mailbox required.")
        try:
            data = make_client(ctx, None, None).list_forwardings(domain, mailbox)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @forwarding_group.command(name="create")
    @click.argument("domain")
    @click.argument("mailbox")
    @click.argument("address")
    @click.option("--expires-on", help="Future date YYYY-MM-DD.")
    @click.option("--remove-upon-expiry/--no-remove-upon-expiry", "remove_upon_expiry", default=False)
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def create_forwarding(ctx, domain, mailbox, address, expires_on, remove_upon_expiry, as_json):
        try:
            data = make_client(ctx, None, None).create_forwarding(domain, mailbox, address,
                expires_on=expires_on, remove_upon_expiry=remove_upon_expiry)
            _print({"forwarding": data, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @forwarding_group.command(name="update")
    @click.argument("domain")
    @click.argument("mailbox")
    @click.argument("address")
    @click.option("--is-active/--not-active", "is_active", help="Active status.")
    @click.option("--expires-on", help="Future date YYYY-MM-DD.")
    @click.option("--remove-upon-expiry/--no-remove-upon-expiry", "remove_upon_expiry")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def update_forwarding(ctx, domain, mailbox, address, is_active, expires_on, remove_upon_expiry, as_json):
        try:
            data = make_client(ctx, None, None).update_forwarding(domain, mailbox, address,
                is_active=is_active, expires_on=expires_on, remove_upon_expiry=remove_upon_expiry)
            _print({"forwarding": data, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
    @forwarding_group.command(name="delete")
    @click.argument("domain")
    @click.argument("mailbox")
    @click.argument("address")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def delete_forwarding(ctx, domain, mailbox, address, as_json):
        try:
            make_client(ctx, None, None).delete_forwarding(domain, mailbox, address)
            _print({"success": True, "deleted": address}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
