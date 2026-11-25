#!/usr/bin/env python3
"""Fail when a pull_request_target workflow checks out pull request code."""

import sys
from pathlib import Path

import yaml

WORKFLOW_GLOBS = ("*.yml", "*.yaml")
DEFAULT_DIR = Path(".github/workflows")
TARGET_EVENT = "pull_request_target"
CHECKOUT_ACTION = "actions/checkout"
CHECKOUT_INPUTS = ("ref", "repository")
# Values an outside contributor controls.
UNTRUSTED_MARKERS = ("github.event.pull_request.head", "github.head_ref")
# PyYAML (YAML 1.1) loads the bare key `on` as the boolean True.
ON_KEYS = ("on", True)


def triggers(doc):
    """Event names a workflow runs on, whatever shape `on:` is written in."""
    for key in ON_KEYS:
        if key not in doc:
            continue
        value = doc[key]
        if isinstance(value, str):
            return [value]
        if isinstance(value, (list, dict)):
            return list(value)
    return []


def is_untrusted_checkout(step):
    uses = step.get("uses")
    if not isinstance(uses, str) or not uses.startswith(CHECKOUT_ACTION):
        return False
    inputs = step.get("with") or {}
    return any(
        marker in str(inputs.get(name, ""))
        for name in CHECKOUT_INPUTS
        for marker in UNTRUSTED_MARKERS
    )


def audit_doc(doc):
    """Return the names of jobs that check out untrusted code."""
    if not isinstance(doc, dict) or TARGET_EVENT not in triggers(doc):
        return []
    jobs = doc.get("jobs") or {}
    return [
        name
        for name, job in jobs.items()
        if isinstance(job, dict)
        and any(
            isinstance(step, dict) and is_untrusted_checkout(step)
            for step in job.get("steps") or []
        )
    ]


def workflow_files(directory):
    for pattern in WORKFLOW_GLOBS:
        yield from sorted(directory.glob(pattern))


def main(argv):
    directories = [Path(arg) for arg in argv] or [DEFAULT_DIR]
    findings = []
    for directory in directories:
        if not directory.is_dir():
            print(f"error: {directory} is not a directory", file=sys.stderr)
            return 2
        for path in workflow_files(directory):
            doc = yaml.safe_load(path.read_text())
            for job in audit_doc(doc):
                findings.append(
                    f"{path}: job '{job}' checks out pull request code "
                    f"under {TARGET_EVENT}"
                )
    for line in findings:
        print(line)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
