# devops-ci-pr-target-audit

A small script that flags GitHub Actions workflows which run on
`pull_request_target` and then check out code from the pull request.

`pull_request_target` runs with the base repository's secrets and a
write-capable token. Checking out the PR head in that context and running
anything from it (a build, a test, a script) hands those privileges to whoever
opened the PR.

## Usage

    pip install -r requirements.txt
    python3 scripts/audit_pr_target.py [workflow-dir ...]

With no arguments it reads `.github/workflows`. It exits 1 when it finds a
risky checkout and prints one line per finding.

## Rule

A job is flagged when its workflow triggers on `pull_request_target` and an
`actions/checkout` step sets `ref` or `repository` to a PR-controlled value
(`github.event.pull_request.head.*`, `github.head_ref`).

## Validate

    make validate
