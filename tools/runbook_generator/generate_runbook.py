#!/usr/bin/env python3
"""AI runbook generator (Phase 14).

Generates a fully-structured runbook from a YAML config
(``templates/runbook-config.yaml``). Output contains valid front matter (all
required + extended metadata), all 25 canonical sections, two Mermaid diagrams
(Investigation Workflow + Decision Tree), checklists, a table, and an example
report scaffold — so it passes the structural validator immediately. Authors
then enrich the prose with domain expertise.

Usage:
    python tools/runbook_generator/generate_runbook.py --config templates/runbook-config.yaml
    python tools/runbook_generator/generate_runbook.py --config my.yaml --print   # stdout only
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import (  # type: ignore  # noqa: E402
    REPO_ROOT,
    SUPPORTED_AGENTS,
    bold,
    difficulty_from_risk,
    green,
    red,
    yellow,
)

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def _list(v, default):
    if not v:
        return list(default)
    return v if isinstance(v, list) else [v]


def _fmt_yaml_list(items) -> str:
    return "\n".join(f"  - {i}" for i in items)


def build_front_matter(cfg: dict) -> str:
    risk = cfg.get("risk_level", "medium")
    agents = _list(cfg.get("supported_agents"), SUPPORTED_AGENTS)
    lines = [
        "---",
        f"id: {cfg['id']}",
        f"title: {cfg['title']}",
        f"category: {cfg.get('category', 'reliability')}",
        f"maturity: draft",
        f"risk_level: {risk}",
        f"estimated_duration: {cfg.get('estimated_duration', '1h-4h')}",
        "supported_agents:",
        _fmt_yaml_list(agents),
        "required_access:",
        _fmt_yaml_list(_list(cfg.get("required_access"), ["read-only-observability"])),
        f"human_in_the_loop: {cfg.get('human_in_the_loop', 'recommended')}",
        f"owner: {cfg.get('owner', 'awesome-ai-runbooks-maintainers')}",
        "version: 0.1.0",
        f"last_reviewed: {date.today().isoformat()}",
        "tags:",
        _fmt_yaml_list(_list(cfg.get("tags"), [cfg.get("category", "reliability")])),
        f"difficulty: {cfg.get('difficulty') or difficulty_from_risk(risk)}",
        f"domain: {cfg.get('domain', cfg.get('category', 'reliability'))}",
        f"platform: {cfg.get('platform', 'cross-platform')}",
        f"agent_type: [{', '.join(agents)}]",
        f"author: {cfg.get('author', cfg.get('owner', 'awesome-ai-runbooks-maintainers'))}",
        "reviewers:",
        _fmt_yaml_list(_list(cfg.get("reviewers"), ["awesome-ai-runbooks-maintainers"])),
        "required_tools:",
        _fmt_yaml_list(_list(cfg.get("required_tools"), ["git"])),
        f"compliance_tags: [{', '.join(_list(cfg.get('compliance_tags'), []))}]",
        "status: draft",
        "maturity_level: 1",
        "---",
    ]
    return "\n".join(lines)


SECTION_GUIDE = {
    "Objective": "State the single measurable objective. Define what 'done' looks like.",
    "Business Context": "Connect this work to revenue, risk, cost, customer experience, or velocity.",
    "Problem Statement": "Describe the problem precisely, including symptoms and what is out of scope.",
    "Success Criteria": None,
    "Trigger Conditions": "Enumerate the alerts, schedules, or requests that legitimately trigger this runbook.",
    "Inputs Required": None,
    "Required Access": "List least-privilege scopes; flag any write/production access explicitly.",
    "Assumptions": "State preconditions; if any is false, the agent should escalate.",
    "Risks": None,
    "Constraints": "Hard boundaries: change freezes, blast-radius limits, no prod writes without approval.",
    "Agent Persona": "Define the role, tone, and bias controls. Reference ../../docs/AI_AGENT_STANDARDS.md.",
    "Planning Instructions": "Steps to produce and externalize a plan before acting.",
    "Execution Instructions": "Ordered, concrete steps. Show read-only steps before any mutation.",
    "Investigation Workflow": None,
    "Analysis Framework": "How to reason about evidence, rank hypotheses, and avoid confirmation bias.",
    "Decision Tree": None,
    "Validation Steps": None,
    "Expected Outputs": "Describe the concrete artifacts produced (reports, PRs, tickets).",
    "Deliverables": "Final reviewable deliverable using ../../templates/report-template.md.",
    "Escalation Process": "Who to escalate to, when, with what context; severity mapping.",
    "Rollback Strategy": "Exact steps to undo any change and confirm rollback success.",
    "Post-Execution Review": "Short retrospective: what worked, what surprised us, what to automate.",
    "Metrics": None,
    "Example Execution": None,
    "References": None,
}


def build_body(cfg: dict) -> str:
    title = cfg["title"]
    summary = cfg.get("summary", f"Operational runbook for {title}.")
    obj = cfg.get("objective", "Describe the single measurable objective here.")
    biz = cfg.get("business_context", SECTION_GUIDE["Business Context"])

    parts = [f"# {title}", "", f"> {summary.strip()}", ""]

    def h2(name: str, content: str) -> None:
        parts.append(f"## {name}")
        parts.append("")
        parts.append(content.strip())
        parts.append("")

    h2("Objective", obj)
    h2("Business Context", biz)
    h2("Problem Statement", SECTION_GUIDE["Problem Statement"])
    h2("Success Criteria", "- [ ] Criterion 1 (objective, measurable)\n- [ ] Criterion 2\n- [ ] Criterion 3")
    h2("Trigger Conditions", "- Alert: ...\n- Schedule: ...\n- Manual request: ...")
    h2(
        "Inputs Required",
        "| Input | Description | Example | Required |\n|-------|-------------|---------|----------|\n"
        "| `service_name` | Target service | `checkout-api` | Yes |",
    )
    h2("Required Access", SECTION_GUIDE["Required Access"])
    h2("Assumptions", SECTION_GUIDE["Assumptions"])
    h2(
        "Risks",
        "| Risk | Likelihood | Impact | Mitigation |\n|------|-----------|--------|------------|\n"
        "| Misdiagnosis | Medium | High | Require evidence before recommending a change |",
    )
    h2("Constraints", SECTION_GUIDE["Constraints"])
    h2("Agent Persona", SECTION_GUIDE["Agent Persona"])
    h2("Planning Instructions", SECTION_GUIDE["Planning Instructions"])
    h2(
        "Execution Instructions",
        "```bash\n# Example read-only command (replace with real steps)\nkubectl get pods -n <namespace>\n```",
    )
    h2(
        "Investigation Workflow",
        "```mermaid\nflowchart TD\n    A[Start] --> B{Signal present?}\n"
        "    B -->|Yes| C[Collect evidence]\n    B -->|No| D[Expand scope]\n"
        "    C --> E[Form hypothesis]\n    E --> F{Confirmed?}\n"
        "    F -->|Yes| G[Document finding]\n    F -->|No| E\n```",
    )
    h2("Analysis Framework", SECTION_GUIDE["Analysis Framework"])
    h2(
        "Decision Tree",
        "```mermaid\nflowchart TD\n    Start[Observation] --> Q1{Is X true?}\n"
        "    Q1 -->|Yes| A1[Action A]\n    Q1 -->|No| Q2{Is Y true?}\n"
        "    Q2 -->|Yes| A2[Action B]\n    Q2 -->|No| A3[Escalate]\n```",
    )
    h2("Validation Steps", "- [ ] Validation 1 (before/after evidence)\n- [ ] Validation 2 (no regression)")
    h2("Expected Outputs", SECTION_GUIDE["Expected Outputs"])
    h2("Deliverables", SECTION_GUIDE["Deliverables"])
    h2("Escalation Process", SECTION_GUIDE["Escalation Process"])
    h2("Rollback Strategy", SECTION_GUIDE["Rollback Strategy"])
    h2("Post-Execution Review", SECTION_GUIDE["Post-Execution Review"])
    h2(
        "Metrics",
        "| Metric | Definition | Target |\n|--------|-----------|--------|\n| MTTR | Mean time to resolve | < 30m |",
    )
    h2(
        "Example Execution",
        "A realistic walkthrough. Inputs, agent reasoning, commands, and a sample report "
        "excerpt built from `../../templates/report-template.md`.\n\n"
        "```text\nInputs: service_name=checkout-api, environment=prod\nFinding: ...\nRecommendation: ...\n```",
    )
    h2("References", "- [AI Agent Standards](../../docs/AI_AGENT_STANDARDS.md)\n- [Report template](../../templates/report-template.md)")

    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--print", action="store_true", dest="to_stdout")
    parser.add_argument("--force", action="store_true", help="overwrite if the file exists")
    args = parser.parse_args()

    if yaml is None:
        print(red("PyYAML is required: pip install -r requirements-dev.txt"))
        return 2

    cfg_path = Path(args.config)
    if not cfg_path.is_absolute():
        cfg_path = REPO_ROOT / cfg_path
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    for req in ("id", "title", "category"):
        if not cfg.get(req):
            print(red(f"config missing required key: {req}"))
            return 2

    content = build_front_matter(cfg) + "\n\n" + build_body(cfg)

    if args.to_stdout:
        print(content)
        return 0

    out = REPO_ROOT / "runbooks" / cfg.get("category", "reliability") / f"{cfg['id']}.md"
    if out.exists() and not args.force:
        print(yellow(f"{out.relative_to(REPO_ROOT)} exists; use --force to overwrite."))
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8", newline="\n")
    print(green(bold(f"Generated {out.relative_to(REPO_ROOT)}")))
    print("Next: enrich the prose to >= 1000 words, then run tools/quality/runbook_validator.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
