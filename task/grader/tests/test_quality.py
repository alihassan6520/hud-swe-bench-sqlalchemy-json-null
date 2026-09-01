from pathlib import Path
import subprocess


repo = Path.cwd()
diff = subprocess.check_output(
    ["git", "diff", "HEAD", "--", "test/dialect/sqlite/test_types.py"],
    cwd=repo,
    text=True,
)
lower_diff = diff.lower()

assert "JSON.NULL" in diff, "expected SQLite JSON.NULL regression coverage"
assert any(
    token in lower_diff
    for token in (
        "does_not_exist",
        "missing",
        "nonexistent",
        "no_such",
        "unknown",
        "absent",
    )
), "expected absent-path regression coverage"
assert "!=" in diff, "expected inequality regression coverage"
