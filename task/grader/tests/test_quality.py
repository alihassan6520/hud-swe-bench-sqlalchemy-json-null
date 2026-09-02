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
        "nonexistent",
        "no_such",
        "unknown",
        "absent",
    )
), "expected absent-path regression coverage"
assert "!=" in diff, "expected inequality regression coverage"
assert "==" in diff, "expected equality regression coverage"
assert ".is_(" in diff, "expected is_() regression coverage"
assert ".is_not(" in diff, "expected is_not() regression coverage"
assert ".in_(" in diff or ".in_op(" in diff, "expected membership coverage"
assert ".not_in(" in diff or ".notin(" in diff, "expected inverse membership coverage"
compact_diff = diff.replace(" ", "")
assert (
    "JSON.NULL==" in compact_diff or "json_null==" in compact_diff
), "expected reversed equality coverage"
assert (
    "JSON.NULL!=" in compact_diff or "json_null!=" in compact_diff
), "expected reversed inequality coverage"
assert (
    "[json_null," in compact_diff
    or "[JSON.NULL," in compact_diff
), "expected mixed JSON.NULL membership coverage"
