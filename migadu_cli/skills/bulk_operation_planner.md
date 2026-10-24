# Bulk Operation Planner

## Overview
Plan and execute bulk operations across multiple resources. This skill guides agents through safe multi-step workflows.

## Principles
1. **Order of operations** — Create parent resources first (mailboxes before identities).
2. **Rollback strategy** — Verify each batch before proceeding to the next.
3. **Verification** — List/get results after each batch to confirm success.
4. **Explicit destructive operations** — Confirm before deleting.

## CLI Commands

```bash
# Bulk create mailboxes
migadu list-mailboxes example.com  # Verify current state
migadu create-mailbox example.com user1 --name "User 1" --password "Pass1"
migadu create-mailbox example.com user2 --name "User 2" --password "Pass2"

# Verify after creation
migadu list-mailboxes example.com

# Create identities (after mailboxes exist)
migadu create-identity example.com user1 info --name "Info Sender"

# Bulk update (update one at a time)
migadu update-mailbox example.com user1 --name "Updated Name"
```

## Tips
- Use `list-*` commands to verify state before and after bulk operations.
- For destructive operations (delete), confirm targets explicitly.
- Create resources in dependency order.
- Check results using `get-*` commands after each batch.