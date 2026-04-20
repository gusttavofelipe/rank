"""Parse uv.lock files and generate dependency change summary."""

import re
import sys


def parse_lockfile(filepath: str) -> dict[str, str]:
	"""Extract package names and versions from uv.lock file."""
	with open(filepath) as f:
		content = f.read()

	package_pattern = r'\[\[package\]\]\s+name = "([^"]+)"[^\[]*?version = "([^"]+)"'
	return {name: version for name, version in re.findall(package_pattern, content)}


def generate_summary(old_file: str, new_file: str, output_file: str) -> None:
	"""Generate a formatted summary of dependency changes."""
	old_packages = parse_lockfile(old_file)
	new_packages = parse_lockfile(new_file)

	updated = []
	added = []
	removed = []

	for name, new_ver in sorted(new_packages.items()):
		if name in old_packages:
			old_ver = old_packages[name]
			if old_ver != new_ver:
				updated.append(f"- {name}: {old_ver} → {new_ver}")
		else:
			added.append(f"- {name}: {new_ver}")

	for name, old_ver in sorted(old_packages.items()):
		if name not in new_packages:
			removed.append(f"- {name}: {old_ver}")

	summary_parts = [
		"### Updated",
		"\n".join(updated) if updated else "(none)",
		"",
		"### Added",
		"\n".join(added) if added else "(none)",
		"",
		"### Removed",
		"\n".join(removed) if removed else "(none)",
	]

	summary = "\n".join(summary_parts)

	with open(output_file, "w") as f:
		f.write(summary)

	print(summary)


if __name__ == "__main__":
	if len(sys.argv) != 4:
		print("Usage: parse_dependencies.py <old_lock> <new_lock> <output_file>")
		sys.exit(1)

	generate_summary(sys.argv[1], sys.argv[2], sys.argv[3])
