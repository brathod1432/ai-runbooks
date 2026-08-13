# Security Policy

## Our scope

`awesome-ai-runbooks` is a documentation repository: it contains Markdown
runbooks, templates, prompts, and lightweight validation scripts. It ships **no
runtime service** and **no secrets**. Nonetheless, security matters here in two
distinct ways:

1. **Repository security** — the integrity of the content and tooling.
2. **Operational security guidance** — ensuring the runbooks themselves promote
   safe, defensive, least-privilege agent behavior.

## Supported versions

The `main` branch is the supported version. Tagged releases receive fixes on a
best-effort basis. Always adopt runbooks from a pinned tag or commit for
production use.

## Reporting a vulnerability

If you discover a security issue — for example, a runbook that could induce an
agent to take an unsafe action, a script vulnerability, or a supply-chain
concern in tooling — please report it privately:

1. Preferred: open a **GitHub Security Advisory** ("Report a vulnerability") on
   this repository.
2. Alternative: contact the maintainers through the private channel listed on
   the repository's community profile.

Please include:

- A clear description of the issue and its impact.
- Steps to reproduce or the affected file(s) and lines.
- Any suggested remediation.

**Please do not open a public issue for security-sensitive reports.**

### Our commitment

- We will acknowledge your report within **3 business days**.
- We will provide an assessment and remediation plan within **10 business days**.
- We will credit reporters in the changelog unless you prefer to remain
  anonymous.

## Safe-content principles for runbooks

All contributed runbooks must uphold these principles, which reviewers enforce:

- **Defensive only.** Security runbooks focus on detection, hardening, and
  remediation. We reject content designed primarily to enable attacks, harvest
  credentials, or evade defenses.
- **Least privilege.** Runbooks request the minimum access needed and prefer
  read-only investigation before any mutation.
- **Human-in-the-loop for high risk.** Destructive or production-mutating steps
  must be gated behind explicit human approval and include a rollback strategy.
- **No secrets.** Never commit credentials, tokens, private keys, customer data,
  or internal hostnames. Use placeholders like `<REDACTED>` or `<YOUR_TOKEN>`.
- **Reversibility.** Any action an agent may take must have a documented,
  verifiable rollback.

## Secret hygiene

- The repository is scanned for secrets in CI (see
  [`.github/workflows`](./.github/workflows)).
- If you accidentally commit a secret, treat it as compromised: rotate it
  immediately and notify the maintainers so history can be scrubbed.

## Dependencies

Tooling dependencies are kept minimal and pinned. We avoid brand-new package
versions (prefer releases at least 7 days old) to reduce supply-chain risk, and
we never weaken security controls to work around CI failures.
