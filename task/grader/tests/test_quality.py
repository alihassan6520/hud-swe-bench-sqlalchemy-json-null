from pathlib import Path
import subprocess


repo = Path.cwd()
diff = subprocess.check_output(
    ["git", "diff", "HEAD", "--", "test/dialect/sqlite/test_types.py"],
    cwd=repo,
    text=True,
)

assert "JSON.NULL" in diff, "expected SQLite JSON.NULL regression coverage"
assert "missing" in diff.lower(), "expected missing-path regression coverage"
assert "!=" in diff, "expected inequality regression coverage"

