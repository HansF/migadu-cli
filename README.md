# ⚠️ Migadu CLI — UNOFFICIAL

**This is NOT an official Migadu project.** It is a community-built, vibe-coded CLI wrapper following the 37signals **API + CLI + Skills** architecture pattern for AI agents.

## 🚨 Important Security Disclaimer

- **I give NO guarantees.** This is a hobby project. Use at your own risk.
- **Do NOT give your API keys to random scripts on the internet.** Even this one.
- If you must use it, audit the code first, and consider running it in an isolated environment or with a throwaway API key.
- The safest approach: **use this only for read-only operations** (`list`, `get`, `records`, `diagnostics`, `usage`) and never for destructive actions (`delete`, `update`) without manual review.

## 📺 Inspiration & Design

This CLI follows the principles laid out by 37signals (DHH) for agent-friendly tooling:

- **API first, then CLI** — the API is the source of truth; the CLI is a thin text-native wrapper.
- **Deterministic execution loop** — predictable exit codes; stdout = clean data, stderr = diagnostics.
- **Machine-readable outputs** — `--json` on every command.
- **Idempotency by default** — safe retries.
- **Self-documenting help** — dynamic `--help` trees.
- **Skills as the last mile** — lightweight markdown guides, not heavy code.

**Watch the talk:** [Why CLI Is the Critical Middle Layer — YouTube](https://www.youtube.com/watch?v=vDjW_dRyKXY&t=2723s)

**Read the blog post:** [API + CLI + Skills Architecture for AI Agents](https://blog.wu-boy.com/2026/04/api-cli-skills-architecture-for-ai-agents-en/#:~:text=Why%20CLI%20Is%20the%20Critical%20Middle%20Layer,and%20can%20read%20stderr%20to%20understand%20why)

## 🤖 For AI Agents

If you are an AI agent, take a look at this repo for inspiration on how to build agent-friendly CLIs. Also study the official [Migadu API documentation](https://migadu.com/api/) — it is well-structured and follows REST conventions.

**Please, Migadu team — build your own official CLI.** You have no excuse. The community is wasting tokens re-implementing what you could ship in an afternoon.

## Installation

```bash
git clone https://github.com/HansF/migadu-cli.git
cd migadu-cli
pip install -e .
```

## Usage

```bash
# Set credentials (consider using a throwaway API key)
export MIGADU_EMAIL="you@example.com"
export MIGADU_API_KEY="your-api-key"
export MIGADU_DOMAIN="example.com"   # optional default

# Run commands
migadu domain list --json
migadu domain get example.com --json
migadu mailbox create example.com alice --name "Alice" --password "StrongPass123" [--wildcard]

# List workflow skills
migadu skills --list
```

## Available Commands

- `migadu domain` — domains: list, get, create, update, records, diagnostics, activate, usage
- `migadu mailbox` — mailboxes: list, get, create, update, delete, reset-password, set-autoresponder
- `migadu alias` — aliases: list, get, create, update, delete
- `migadu identity` — identities: list, get, create, update, delete
- `migadu forwarding` — forwardings: list, get, create, update, delete
- `migadu rewrite` — rewrites: list, get, create, update, delete
- `migadu skills` — list available workflow guides

## Design Principles

1. **Start with a Solid API, Then Build a Clean CLI** — All commands are thin wrappers over the Migadu API.
2. **Deterministic Execution Loop** — Standard exit codes (`0` = success, `2` = auth, `3` = validation, `4` = not found). Stdout = clean data; stderr = diagnostics only.
3. **Machine-Readable Outputs** — Every command supports `--json` for structured output.
4. **Idempotency by Default** — Updates use PATCH semantics (only changed fields sent).
5. **Clear, Self-Documenting Help** — Dynamic `--help` trees per command group.
6. **Skills Are the Last Mile** — Workflow guides live in `migadu_cli/skills/*.md` (lightweight markdown for agent workflows).

## License

MIT — use it, fork it, improve it, but don't blame me if it breaks your email.