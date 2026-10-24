# Mailbox Creation Wizard

## Overview
Create mailboxes for new users. The wizard supports two modes:
- **Password-based** — Set password immediately; ideal for bulk creation.
- **Invitation-based** — User receives an invite to set their own password.

## Parameters
| Parameter | Required | Notes |
|------------|----------|-------|
| domain | Yes | Domain name for the mailbox |
| local_part | Yes | Mailbox name (e.g., `alice`) |
| name | No | Display name |
| password | No | Set `password_method: "password"` (default) |
| password_method | No | `"password"` (default) or `"invitation"` |
| password_recovery_email | No | Required if `password_method: "invitation"` |
| is_internal | No | Internal-only mailboxes; no external messages accepted |
| forwarding_to | No | Forward to external address at creation |

## CLI Commands

```bash
# Create with password
migadu create-mailbox example.com alice --name "Alice Smith" --password "StrongPass123"

# Invite user (they set their own password)
migadu create-mailbox example.com bob --name "Bob Jones" --password-method invitation --password-recovery-email "bob@external.com"

# Create internal mailbox (restricted to Migadu internal routing)
migadu create-mailbox example.com internal --name "Internal Bot" --password "StrongPass123" --is-internal true

# Create with forwarding
migadu create-mailbox example.com carol --name "Carol Lee" --password "StrongPass123" --forwarding-to "carol@external.com"
```

## Tips
- Aliases can redirect only within the same domain.
- Internal mailboxes accept no external messages.
- For identities, use `create-identity` on an existing mailbox.
