# Maintainers

This document describes who maintains **awesome-ai-runbooks**, how the teams are
organized, and how decisions get made. Maintainers are stewards of a
safety-first library of agent runbooks; the role is a responsibility, not a
badge. All maintainers uphold the [Code of Conduct](CODE_OF_CONDUCT.md).

## Roles and responsibilities

Maintainers review pull requests, triage issues and discussions, uphold the
quality bar in [`docs/QUALITY_ASSURANCE.md`](docs/QUALITY_ASSURANCE.md), keep
tooling and CI healthy, and cut releases. They are expected to review within the
SLAs in [`REVIEW_GUIDE.md`](REVIEW_GUIDE.md), respond to security reports
promptly, and mentor new contributors.

## Teams and scopes

Ownership is enforced through [`.github/CODEOWNERS`](.github/CODEOWNERS). Each
team owns a scope and is auto-requested for review on matching changes.

| Team | GitHub team | Scope | Primary responsibilities |
|------|-------------|-------|--------------------------|
| Maintainers | `@awesome-ai-runbooks/maintainers` | Whole repo (default), `/tools/`, `/scripts/`, `/.github/` | General review, tooling, CI, releases, final say on merges |
| Security | `@awesome-ai-runbooks/security` | `/runbooks/security/`, `/security/`, `SECURITY.md` | Security/safety review, advisory triage, mandatory second review on high-risk PRs |
| Governance | `@awesome-ai-runbooks/governance` | `/governance/` | Process, policy, and standards changes |
| Docs | `@awesome-ai-runbooks/docs` | `/docs/` | Documentation accuracy, clarity, and structure |

A maintainer may belong to more than one team. Security and high-risk runbook
PRs require a second, independent review — see the triggers in
[`REVIEW_GUIDE.md`](REVIEW_GUIDE.md).

## Decision-making

We work by **lazy consensus**: a proposal with no sustained objection after a
reasonable review window is accepted. Routine changes (a new runbook, a doc fix,
a tooling improvement) need at least one maintainer approval — two for
security-category or `high`/`critical` risk. Substantive changes to standards,
governance, or the review process are proposed as an issue or discussion, given
time for comment, and decided by the relevant team. When consensus cannot be
reached, the Maintainers team makes the final call, favoring the safest option.

## How to become a maintainer

Maintainership is earned through sustained, high-quality contribution:

1. Contribute merged runbooks, tooling, or reviews over time.
2. Demonstrate sound judgment on safety, least privilege, and quality.
3. Be nominated by an existing maintainer; the Maintainers team confirms by
   lazy consensus.

New maintainers typically start with a focused scope (for example, docs) and
expand as trust grows. Team membership is reflected in the GitHub teams above.

## Release duties

The releasing maintainer verifies CI is green on `main`, confirms
`CHANGELOG.md` is updated, tags the release, and posts an **Announcement**
discussion. Runbooks in production should always be adopted from a pinned tag or
commit, so releases must be reproducible and clearly noted.

## Emeritus policy

Maintainers who step back are moved to **emeritus** status: recognized for their
past contributions, removed from active teams and CODEOWNERS, and thanked in the
project history. Emeritus maintainers are welcome to return through the standard
nomination process. Inactive maintainers (no meaningful activity for ~6 months)
may be moved to emeritus after a friendly heads-up, keeping review load on
active hands.
