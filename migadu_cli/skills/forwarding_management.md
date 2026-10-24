# Forwarding Management

## Overview
Manage forwardings — external delivery copies with a confirmation flow. Forwardings redirect email to external addresses.

## Parameters
| Parameter | Required | Notes |
|------------|----------|-------|
| domain | Yes | Domain name |
| mailbox | Yes | Mailbox name |
| address | Yes | External email address to forward to |
| expires_on | No | Expiration date (YYYY-MM-DD) |
| remove_upon_expiry | No | Remove forwarding when it expires |

## CLI Commands

```bash
# Create forwarding
migadu create-forwarding example.com user1 external@example.com

# Create forwarding with expiration
migadu create-forwarding example.com user1 temp@example.com --expires-on 2024-12-31 --remove-upon-expiry true

# Update forwarding
migadu update-forwarding example.com user1 external@example.com --is-active true --expires-on 2025-01-01 --remove-upon-expiry true

# Delete forwarding
migadu delete-forwarding example.com user1 external@example.com
```

## Tips
- Forwardings require confirmation by the external address.
- Expired forwardings can be automatically removed.
- Use `expires_on` only with future dates.