#!/usr/bin/env python3
"""Secret scanner (Phase 23).

A dependency-free, defensive secret scanner tuned for a documentation repo. It
flags likely committed credentials while tolerating the intentional placeholders
runbooks use in examples (``<REDACTED>``, ``<YOUR_TOKEN>``, ``example``, ...).

Writes ``security/secret-scan.json``. Exit 1 if any high-confidence secret is
found.

Usage:
    python tools/security/secret_scanner.py [--all]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import REPO_ROOT, bold, green, red, write_json, yellow  # type: ignore  # noqa: E402

# (name, regex, confidence)
PATTERNS = [
    ("aws_access_key_id", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "high"),
    ("aws_secret_access_key", re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?"), "high"),
    ("github_pat", re.compile(r"\bghp_[A-Za-z0-9]{36}\b"), "high"),
    ("github_fine_grained", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b"), "high"),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "high"),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"), "high"),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "high"),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), "medium"),
    ("generic_secret_assignment", re.compile(r"(?i)(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]"), "medium"),
]

# If a match line contains any of these, treat it as an intentional placeholder.
ALLOWLIST = [
    "<", ">", "redact", "example", "your-", "placeholder", "changeme", "xxxx",
    "dummy", "sample", "fake", "test", "0000000000", "abc123", "...", "$env",
    "${", "vault:", "secretref", "secretkeyref",
]

SCAN_EXTS = {".md", ".py", ".yml", ".yaml", ".json", ".jsonc", ".txt", ".sh", ".env", ".cfg", ".ini"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "site"}


def is_allowlisted(line: str) -> bool:
    low = line.lower()
    return any(tok in low for tok in ALLOWLIST)


def iter_files(all_files: bool):
    for p in REPO_ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if not all_files and p.suffix.lower() not in SCAN_EXTS:
            continue
        yield p


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="scan all file types")
    parser.add_argument("--json", default="security/secret-scan.json")
    args = parser.parse_args()

    findings = []
    high = 0
    files = 0
    self_path = Path(__file__).resolve()
    for f in iter_files(args.all):
        # Never scan this scanner (it contains the detection patterns themselves).
        if f.resolve() == self_path:
            continue
        files += 1
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if is_allowlisted(line):
                continue
            for name, rx, conf in PATTERNS:
                if rx.search(line):
                    findings.append({
                        "file": str(f.relative_to(REPO_ROOT)).replace("\\", "/"),
                        "line": lineno,
                        "rule": name,
                        "confidence": conf,
                    })
                    if conf == "high":
                        high += 1

    report = {
        "generated_by": "tools/security/secret_scanner.py",
        "files_scanned": files,
        "findings": findings,
        "high_confidence": high,
    }
    write_json(REPO_ROOT / args.json, report)

    print(bold(f"Secret scan: {files} file(s) scanned"))
    if not findings:
        print(green(bold("No secrets detected.")))
    for fnd in findings:
        color = red if fnd["confidence"] == "high" else yellow
        print(color(f"  [{fnd['confidence']}] {fnd['file']}:{fnd['line']} {fnd['rule']}"))
    print(green(f"Wrote {args.json}"))
    if high:
        print(red(bold(f"{high} high-confidence secret(s) found.")))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
