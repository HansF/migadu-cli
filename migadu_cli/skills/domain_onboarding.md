# Domain Onboarding

## Overview
Onboard a new Migadu domain end-to-end, from creation to activation.

## Steps

1. **Create the domain** — Use `create_domain` with `hosted_dns: false` and `create_default_addresses: true`.
2. **Configure DNS records** — Add MX, SPF, DKIM, DMARC, and verification records externally.
3. **Run diagnostics** — Verify DNS propagation with `get_domain_diagnostics`.
4. **Activate the domain** — Call `activate_domain` once DNS is ready.
5. **Verify usage** — Check `get_domain_usage` to confirm the domain is live.

## CLI Commands

```bash
# Initialize CLI with credentials
migadu init --email "you@example.com" --api-key "your-api-key" --domain "example.com"

# Create the domain
migadu create-domain example.com --hosted_dns false --create_default_addresses true

# Get DNS records needed for setup
migadu get-domain-records example.com

# Run diagnostics
migadu get-domain-diagnostics example.com

# Activate the domain
migadu activate-domain example.com

# Check usage
migadu get-domain-usage example.com
```

## Tips
- Set `hosted_dns: false` when creating the domain to use external DNS.
- Always add default addresses (`create_default_addresses: true`) during creation.
- Run diagnostics after configuring records externally.
- Activation fails with HTTP 422 if DNS validation fails.
