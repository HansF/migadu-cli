"""Mailbox commands: list, get, create, update, delete, reset-password, set-autoresponder."""
import click
from .dependencies import make_client, _print, _handle_error


def register_mailbox_commands(cli):
    @cli.group(name="mailbox")
    def mailbox_group():
        """Manage mailboxes on a domain."""
        pass

    @mailbox_group.command(name="list")
    @click.option("--domain", help="Domain name (defaults to configured domain).")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def list_mailboxes(ctx, domain, as_json):
        """List all mailboxes for a domain."""
        try:
            client = make_client(ctx, None, None)
            domain = domain or ctx.obj.get("domain", "")
            if not domain:
                raise click.ClickException("Domain required: pass --domain or set default with `migadu init`")
            data = client.list_mailboxes(domain)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @mailbox_group.command(name="get")
    @click.argument("local_part")
    @click.option("--domain", help="Domain name (defaults to configured domain).")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def get_mailbox(ctx, local_part, domain, as_json):
        """Get mailbox details."""
        try:
            client = make_client(ctx, None, None)
            domain = domain or ctx.obj.get("domain", "")
            if not domain:
                raise click.ClickException("Domain required")
            data = client.get_mailbox(domain, local_part)
            _print(data, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @mailbox_group.command(name="create")
    @click.argument("domain")
    @click.argument("local_part")
    @click.option("--name", help="Display name.")
    @click.option("--password", help="Set password immediately (default: password method).")
    @click.option("--password-method", type=click.Choice(["password", "invitation"]), default="password",
                  help="How to set password: 'password' (immediate) or 'invitation' (user sets it).")
    @click.option("--password-recovery-email", help="Required if password-method=invitation.")
    @click.option("--forwarding-to", help="External address to forward to.")
    @click.option("--is-internal/--no-is-internal", "is_internal", default=False,
                  help="Internal-only mailbox (no external messages).")
    @click.option("--wildcard/--no-wildcard", "wildcard_sender", default=False,
                  help="Enable wildcard sender (can be left false/default for standard use).")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def create_mailbox(ctx, domain, local_part, name, password, password_method,
                       password_recovery_email, forwarding_to, is_internal,
                       wildcard_sender, as_json):
        """Create a mailbox. Idempotent: re-running returns existing mailbox."""
        try:
            client = make_client(ctx, None, None)
            data = client.create_mailbox(
                domain, local_part,
                name=name,
                password=password,
                password_method=password_method,
                password_recovery_email=password_recovery_email,
                forwarding_to=forwarding_to,
                is_internal=is_internal,
                wildcard_sender=wildcard_sender,
            )
            _print({"mailbox": data, "address": f"{local_part}@{domain}", "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @mailbox_group.command(name="update")
    @click.argument("domain")
    @click.argument("local_part")
    @click.option("--name", help="Display name.")
    @click.option("--password", help="New password.")
    @click.option("--password-method", type=click.Choice(["password", "invitation"]), help="Change password method.")
    @click.option("--password-recovery-email", help="Recovery email for invitation method.")
    @click.option("--forwarding-to", help="External forwarding address.")
    @click.option("--is-internal/--no-is-internal", "is_internal", help="Internal-only mailbox.")
    @click.option("--wildcard/--no-wildcard", "wildcard_sender", help="Enable wildcard sender.")
    @click.option("--may-send/--no-may-send", "may_send", help="Allow sending.")
    @click.option("--may-receive/--no-may-receive", "may_receive", help="Allow receiving.")
    @click.option("--may-access-imap/--no-may-access-imap", "may_access_imap", help="IMAP access.")
    @click.option("--may-access-pop3/--no-may-access-pop3", "may_access_pop3", help="POP3 access.")
    @click.option("--may-access-managesieve/--no-may-access-managesieve", "may_access_managesieve", help="ManageSieve access.")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def update_mailbox(ctx, domain, local_part, name, password, password_method,
                       password_recovery_email, forwarding_to, is_internal,
                       may_send, may_receive, may_access_imap, may_access_pop3,
                       may_access_managesieve, as_json):
        """Update mailbox fields. Idempotent: PATCH only sends changed fields."""
        try:
            client = make_client(ctx, None, None)
            data = client.update_mailbox(
                domain, local_part,
                name=name, password=password, password_method=password_method,
                password_recovery_email=password_recovery_email,
                forwarding_to=forwarding_to, is_internal=is_internal,
                may_send=may_send, may_receive=may_receive,
                may_access_imap=may_access_imap, may_access_pop3=may_access_pop3,
                may_access_managesieve=may_access_managesieve,
                wildcard_sender=wildcard_sender,
            )
            _print({"mailbox": data, "success": True}, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @mailbox_group.command(name="delete")
    @click.argument("domain")
    @click.argument("local_part")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def delete_mailbox(ctx, domain, local_part, as_json):
        """Delete a mailbox. Idempotent: deleting non-existent succeeds."""
        try:
            client = make_client(ctx, None, None)
            client.delete_mailbox(domain, local_part)
            _print({"success": True, "deleted": f"{local_part}@{domain}"}, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @mailbox_group.command(name="reset-password")
    @click.argument("domain")
    @click.argument("local_part")
    @click.argument("password")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def reset_mailbox_password(ctx, domain, local_part, password, as_json):
        """Reset mailbox password."""
        try:
            client = make_client(ctx, None, None)
            data = client.reset_mailbox_password(domain, local_part, password)
            _print({"success": True, "data": data}, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    @mailbox_group.command(name="set-autoresponder")
    @click.argument("domain")
    @click.argument("local_part")
    @click.option("--enabled/--disabled", default=True, help="Enable or disable autoresponder.")
    @click.option("--subject", help="Autoresponder subject.")
    @click.option("--message", help="Autoresponder message body.")
    @click.option("--start-date", help="Start date (YYYY-MM-DD).")
    @click.option("--end-date", help="End date (YYYY-MM-DD).")
    @click.option("--json", "as_json", is_flag=True, default=False, help="Output machine-readable JSON.")
    @click.pass_context
    def set_autoresponder(ctx, domain, local_part, enabled, subject, message, start_date, end_date, as_json):
        """Set autoresponder on a mailbox."""
        try:
            client = make_client(ctx, None, None)
            data = client.set_autoresponder(
                domain, local_part,
                enabled=enabled, subject=subject, message=message,
                start_date=start_date, end_date=end_date,
            )
            _print({"success": True, "data": data}, as_json)
            ctx.exit(0)
        except Exception as exc:
            _handle_error(exc)

    return mailbox_group