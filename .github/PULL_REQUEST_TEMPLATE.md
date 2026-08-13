<!--
  Thanks for contributing to awesome-ai-runbooks!
  Please fill in every relevant section. Delete sections that do not apply,
  but do not delete the checklists for the type of change you are making.
-->

## Summary

<!-- What does this PR change and why? Keep it concise and outcome-focused. -->

## Type of change

- [ ] New runbook
- [ ] Runbook improvement / fix
- [ ] Prompt library
- [ ] Tooling / CI
- [ ] Documentation
- [ ] Governance / process
- [ ] Other (describe below)

## Runbook author checklist

<!-- Required if this PR adds or changes a runbook. Mirrors
     templates/runbook-template.md and the bar in docs/QUALITY_ASSURANCE.md. -->

- [ ] Copied from [`templates/runbook-template.md`](../templates/runbook-template.md); **all 25 sections present, in order**, with headings unchanged
- [ ] Valid YAML front matter with **extended metadata** (`id`, `title`, `category`, `maturity`, `risk_level`, `estimated_duration`, `supported_agents`, `required_access`, `human_in_the_loop`, `owner`, `version`, `last_reviewed`, `tags`); `id` matches filename; category is correct
- [ ] **≥ 1000 words** of real, substantive content — no placeholders, no `TODO`, no fabricated tools/APIs
- [ ] **≥ 2 Mermaid diagrams** (Investigation Workflow + Decision Tree) that render
- [ ] At least **one table** and at least **one checklist**
- [ ] Concrete, language-tagged commands; read-only/observation steps shown before any mutating steps
- [ ] **Example execution** with a realistic sample report excerpt
- [ ] **Rollback strategy** is real, specific, and verifiable
- [ ] **Escalation process** is real and specific (who, when, with what context)
- [ ] `risk_level` and `human_in_the_loop` are consistent with [QUALITY_ASSURANCE §3](../docs/QUALITY_ASSURANCE.md)
- [ ] Least-privilege / defensive posture upheld (see [`SECURITY.md`](../SECURITY.md))

## Validation

Paste command output below or confirm each check passes locally:

- [ ] `python tools/quality/runbook_validator.py`
- [ ] `python -m pytest`
- [ ] `npx markdownlint-cli2 "**/*.md"` (or your local `markdownlint`)

```text
# paste relevant command output here
```

## Screenshots / rendered output

<!-- For diagrams, tables, or docs changes, paste a rendered screenshot or excerpt. -->

## Reviewer notes

<!-- Anything reviewers should focus on: security-sensitive areas, high-risk steps,
     open questions, or intentional deviations from the template. -->

## Linked issues

Closes #
