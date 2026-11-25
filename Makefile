.PHONY: validate test lint audit

validate: test lint audit

test:
	python3 -m unittest discover -s tests

lint:
	actionlint

audit:
	python3 scripts/audit_pr_target.py
