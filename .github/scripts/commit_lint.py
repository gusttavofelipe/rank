import os
import re
import subprocess
import sys

SEMANTIC_PATTERN = re.compile(
	r"^(build|ci|docs|feat|fix|perf|refactor|style|test|chore|env)(\(.+\))?: .+"
)

IGNORED_PREFIXES = "Merge", "Revert", "WIP"

base_ref = os.getenv("GITHUB_BASE_REF")

if not base_ref:
	print("No base ref found. This script must run in a pull_request event.")
	sys.exit(1)

cmd = ["git", "log", f"origin/{base_ref}..HEAD", "--pretty=format:%s"]
result = subprocess.run(cmd, capture_output=True, text=True)
messages = result.stdout.strip().split("\n")

invalid = False

for msg in messages:
	if msg.startswith(IGNORED_PREFIXES):
		continue

	if not SEMANTIC_PATTERN.match(msg):
		print(f"Invalid commit message: '{msg}'")
		print("Expected format: <type>(optional-scope): description")
		invalid = True

if invalid:
	sys.exit(1)

print("All commit messages follow the semantic commit convention.")
