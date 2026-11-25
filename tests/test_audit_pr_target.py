import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit_pr_target.py"
FIXTURES = ROOT / "tests" / "fixtures"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
    )


class AuditPrTargetTest(unittest.TestCase):
    def test_flags_head_checkout_under_pull_request_target(self):
        result = run(str(FIXTURES / "unsafe"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("head-ref.yml: job 'build'", result.stdout)

    def test_accepts_base_checkout_and_plain_pull_request(self):
        result = run(str(FIXTURES / "safe"))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, "")

    def test_missing_directory_is_a_usage_error(self):
        result = run(str(FIXTURES / "nope"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("nope", result.stderr)


if __name__ == "__main__":
    unittest.main()
