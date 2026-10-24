# Rewrite Management

## Overview
Manage rewrites — pattern-based routing rules. Rewrites listen for matching patterns and forward to destinations.

## Parameters
| Parameter | Required | Notes |
|------------|----------|-------|
| domain | Yes | Domain name |
| name | Yes | Rewrite name (slug) |
| local_part_rule | Yes | Pattern to match (e.g., `demo-*`) |
| destinations | Yes | Comma-separated list of target addresses |

## CLI Commands

```bash
# Create rewrite
migadu create-rewrite example.com demo --local-part-rule "demo-*" --destinations "alice@example.com,bob@example.com"

# Update rewrite
migadu update-rewrite example.com demo --destinations "carol@example.com"

# Delete rewrite
migadu delete-rewrite example.com demo
```

## Tips
- Rewrites must use same domain as destinations.
- Pattern matching uses wildcards like `*` in the local part rule.
- Rewrites are useful for routing based on email patterns.