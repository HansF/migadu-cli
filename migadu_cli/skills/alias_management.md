# Alias Management

## Overview
Manage aliases — forwarding rules without a mailbox behind them. Aliases can only redirect within the same domain.

## Parameters
| Parameter | Required | Notes |
|------------|----------|-------|
| domain | Yes | Domain name |
| local_part | Yes | Alias name |
| destinations | Yes | Comma-separated list of target addresses |
| is_internal | No | Internal-only alias |

## CLI Commands

```bash
# Create alias forwarding to multiple addresses
migadu create-alias example.com support --destinations "alice@example.com,bob@example.com"

# Create alias with internal forwarding
migadu create-alias example.com team --destinations "alice@example.com" --is-internal true

# List all aliases for a domain
migadu list-aliases example.com

# Update alias destinations
migadu update-alias example.com support --destinations "carol@example.com,dave@example.com"

# Delete an alias
migadu delete-alias example.com support
```

## Tips
- Aliases can forward to addresses on the same domain only.
- Setting `is_internal: true` restricts the alias to Migadu internal routing only.
- One alias can have multiple destinations.