# Migadu CLI

Agent-friendly CLI wrapper for the [Migadu](https://migadu.com/) API — an email hosting provider.

Built following the 37signals **API + CLI + Skills** architecture pattern for agent-friendly tooling.

## Installation

```bash
pip install migadu-cli
```

Or from source:

```bash
git clone <this-repo>
cd migadu-cli
pip install -e .
```

## Usage

```bash
# Set credentials
export MIGADU_EMAIL="you@example.com"
export MIGADU_API_KEY="your-api-key"
export MIGADU_DOMAIN="example.com"   # optional default

# Run commands
migadu domain list --json
migadu domain get example.com --json
migadu domain create newdomain.org
migadu mailbox create example.com alice --name "Alice" --password "StrongPass123"

# List workflow skills
migadu skills --list
```

## Design Principles

1. **Start with a Solid API, Then Build a Clean CLI** — All commands are thin wrappers over the Migadu API.

2. **Deterministic Execution Loop** — Standard exit codes (`0` = success, `2` = auth, `3` = validation, `4` = not found). Stdout = clean data; stderr = diagnostics only.

3. **Machine-Readable Outputs** — Every command supports `--json` for structured output.

4. **Idempotency by Default** — Updates use PATCH semantics (only changed fields sent).

5. **Clear, Self-Documenting Help** — Dynamic `--help` trees per command group.

6. **Skills Are the Last Mile** — Workflow guides live in `migadu_cli/skills/*.md` (lightweight markdown for agent workflows).

## Available Commands

- `migadu domain` — domains: list, get, create, update, records, diagnostics, activate, usage
- `migadu mailbox` — mailboxes: list, get, create, update, delete, reset-password, set-autoresponder
- `migadu alias` — aliases: list, get, create, update, delete
- `migadu identity` — identities: list, get, create, update, delete
- `migadu forwarding` — forwardings: list, get, create, update, delete
- `migadu rewrite` — rewrites: list, get, create, update, delete
- `migadu skills` — list available workflow guides

## License

MIT
