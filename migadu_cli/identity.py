"""Identity commands."""
import click
from .dependencies import make_client, _print, _handle_error

def register_identity_commands(cli):
    @cli.group(name="identity")
    def identity_group():
        """Manage identities (send-as addresses) on a mailbox."""
        pass

    @identity_group.command(name="list")
    @click.argument("domain")
    @click.argument("mailbox")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def list_identities(ctx, domain, mailbox, as_json):
        try:
            data = make_client(ctx, None, None).list_identities(domain, mailbox)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)

    @identity_group.command(name="get")
    @click.argument("domain")
    @click.argument("mailbox")
    @click.argument("local_part")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def get_identity(ctx, domain, mailbox, local_part, as_json):
        try:
            data = make_client(ctx, None, None).get_identity(domain, mailbox, local_part)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)

    @identity_group.command(name="create")
    @click.argument("domain")
    @click.argument("mailbox")
    @click.argument("local_part")
    @click.option("--name", help="Display name.")
    @click.option("--password-use", type=click.Choice(["none", "mailbox", "custom"]), default="none")
    @click.option("--password", help="Required if password-use=custom.")
    @click.option("--may-send/--no-may-send", "may_send", default=True)
    @click.option("--may-receive/--no-may-receive", "may_receive", default=True)
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def create_identity(ctx, domain, mailbox, local_part, name, password_use, password, may_send, may_receive, as_json):
        try:
            data = make_client(ctx, None, None).create_identity(domain, mailbox, local_part,
                name=name, password_use=password_use, password=password,
                may_send=may_send, may_receive=may_receive)
            _print({"identity": data, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)

    @identity_group.command(name="update")
    @click.argument("domain")
    @click.argument("mailbox")
    @click.argument("local_part")
    @click.option("--name", help="Display name.")
    @click.option("--password", help="New password.")
    @click.option("--password-use", type=click.Choice(["none", "mailbox", "custom"]))
    @click.option("--may-send/--no-may-send", "may_send", default=None)
    @click.option("--may-receive/--no-may-receive", "may_receive", default=None)
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def update_identity(ctx, domain, mailbox, local_part, name, password, password_use, may_send, may_receive, as_json):
        try:
            data = make_client(ctx, None, None).update_identity(domain, mailbox, local_part,
                name=name, password=password, password_use=password_use,
                may_send=may_send, may_receive=may_receive)
            _print({"identity": data, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)

    @identity_group.command(name="delete")
    @click.argument("domain")
    @click.argument("mailbox")
    @click.argument("local_part")
    @click.option("--json", "as_json", is_flag=True)
    @click.pass_context
    def delete_identity(ctx, domain, mailbox, local_part, as_json):
        try:
            make_client(ctx, None, None).delete_identity(domain, mailbox, local_part)
            _print({"success": True, "deleted": f"{local_part}@{domain}"}, as_json)
            ctx.exit(0)
        except Exception as exc: _handle_error(exc)
