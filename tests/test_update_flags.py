"""Regression tests for the tri-state flags on every `update` command.

Bug found in production on 2026-10-25: `migadu mailbox update rotordeck.com support --wildcard`
silently switched off may_send, may_receive and IMAP/POP3 access on the mailbox, because click
defaults a `--foo/--no-foo` pair to False when no default is given, so every unset toggle was
sent to the API as an explicit `false`. Every update command now declares `default=None`, which
means "not mentioned, don't touch it".

Run without pytest:  python tests/test_update_flags.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from click.testing import CliRunner

from migadu_cli import alias, forwarding, identity, mailbox


class Recorder:
    """Stands in for MigaduClient: records the kwargs of whichever update call arrives."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        if not name.startswith(("update_", "create_")):
            raise AttributeError(name)

        def record(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return {}

        return record


def make_client_stub(module, recorder):
    """Patch a module's make_client so the CLI uses the recorder instead of the API."""
    module.make_client = lambda *a, **kw: recorder


# The CLI groups are registered on the root command, so invoke the root and patch the module
# that the command actually imported.
from migadu_cli.main import cli


def run(module, argv):
    recorder = Recorder()
    make_client_stub(module, recorder)
    result = CliRunner().invoke(cli, argv)
    assert result.exit_code == 0, f"{argv} exited {result.exit_code}: {result.output!r}"
    assert len(recorder.calls) == 1, f"{argv} made {len(recorder.calls)} calls"
    name, args, kwargs = recorder.calls[0]
    return name, kwargs


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def test_mailbox_update_omits_unset_flags():
    _, kwargs = run(mailbox, ["mailbox", "update", "example.com", "team"])
    for field in ("may_send", "may_receive", "may_access_imap", "may_access_pop3",
                  "may_access_managesieve", "wildcard_sender", "is_internal"):
        check(kwargs.get(field) is None, f"{field} should be None when not given, got {kwargs.get(field)!r}")


def test_mailbox_update_sends_only_what_was_asked():
    _, kwargs = run(mailbox, ["mailbox", "update", "example.com", "team", "--wildcard"])
    check(kwargs["wildcard_sender"] is True, "wildcard should be True")
    check(kwargs["may_send"] is None, f"may_send must stay None, got {kwargs['may_send']!r}")
    check(kwargs["may_receive"] is None, f"may_receive must stay None, got {kwargs['may_receive']!r}")
    check(kwargs["may_access_imap"] is None, f"may_access_imap must stay None, got {kwargs['may_access_imap']!r}")


def test_mailbox_update_explicit_false_still_works():
    _, kwargs = run(mailbox, ["mailbox", "update", "example.com", "team", "--no-may-send"])
    check(kwargs["may_send"] is False, "an explicit --no-may-send must be sent as False")


def test_alias_update_omits_unset_flags():
    _, kwargs = run(alias, ["alias", "update", "example.com", "info", "--destinations", "a@example.com"])
    check(kwargs["is_internal"] is None, f"is_internal should be None, got {kwargs['is_internal']!r}")


def test_forwarding_update_omits_unset_flags():
    _, kwargs = run(forwarding, ["forwarding", "update", "example.com", "team", "a@b.c", "--expires-on", "2026-12-01"])
    check(kwargs["is_active"] is None, f"is_active should be None, got {kwargs['is_active']!r}")
    check(kwargs["remove_upon_expiry"] is None, "remove_upon_expiry should be None")


def test_identity_update_omits_unset_flags():
    _, kwargs = run(identity, ["identity", "update", "example.com", "team", "sales", "--name", "Sales"])
    check(kwargs["may_send"] is None, f"may_send should be None, got {kwargs['may_send']!r}")
    check(kwargs["may_receive"] is None, f"may_receive should be None, got {kwargs['may_receive']!r}")


def test_success_exits_zero_without_error_line():
    """A successful command must exit 0 and print no 'Error:' line (it printed 'Error: 0' before)."""
    recorder = Recorder()
    make_client_stub(mailbox, recorder)
    result = CliRunner().invoke(cli, ["mailbox", "update", "example.com", "team", "--may-send"])
    check(result.exit_code == 0, f"expected exit 0, got {result.exit_code}")
    check("Error:" not in result.output, f"a success must not print an error line: {result.output!r}")


def test_api_error_still_exits_nonzero():
    """An API failure must keep its mapped exit code, not be swallowed by the Exit passthrough."""

    class Failing(Recorder):
        def __getattr__(self, name):
            if not name.startswith("update_"):
                raise AttributeError(name)

            def boom(*a, **kw):
                from migadu_cli.client import MigaduAPIError

                raise MigaduAPIError(404, "not found")

            return boom

    mailbox.make_client = lambda *a, **kw: Failing()
    result = CliRunner().invoke(cli, ["mailbox", "update", "example.com", "team", "--name", "x"])
    check(result.exit_code == 4, f"404 should exit 4, got {result.exit_code}")


def main():
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"ok   {test.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
