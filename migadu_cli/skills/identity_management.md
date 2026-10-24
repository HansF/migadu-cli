# Identity Management

## Overview
Manage identities (send-as addresses) on existing mailboxes. Identities allow users to send email as different addresses on the same mailbox.

## Parameters
| Parameter | Required | Notes |
|------------|----------|-------|
| domain | Yes | Domain name |
| mailbox | Yes | Mailbox name |
| local_part | Yes | Identity name |
| name | No | Display name |
| password | No | Set `password_use: "custom"` (default) |
| password | No | Set `password_use: "custom"` |
| password_method | No | `"custom"` for user-set passwords |
| password | No | Required if `password_method: "custom"` |
| may_send | No | Default: true |
| may_receive | No | Default: true |
| may_access_imap | No | Default: true |
| may_access_pop3 | No | Default: true |
| may_access_managesieve | No | Default: false |

## CLI Commands

```bash
# Create identity with custom password
migadu create-identity example.com user1 info --name "Info Sender" --password "CustomPass"

# Create identity with user-set password (invite user to set their own)
migadu create-identity example.com user2 support --name "Support" --password-method invitation

# Update identity
migadu update-identity example.com user1 --name "Updated Info" --password "NewPass"

# Delete identity
migadu delete-identity example.com user1
```

## Tips
- Use `password_method: "custom"` to let users set their own passwords.
- Identities can be restricted with `may_send`, `may_receive`, `may_access_imap`, etc.
- Internal identities can be restricted to `is_internal: true`.
