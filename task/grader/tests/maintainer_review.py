from pathlib import Path
import subprocess


repo = Path.cwd()
changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    cwd=repo,
    text=True,
).splitlines()
diff = subprocess.check_output(
    ["git", "diff", "HEAD"],
    cwd=repo,
    text=True,
)

assert changed, "expected a source/test diff"
assert len(changed) <= 5, f"expected a focused patch, got files: {changed}"

allowed_prefixes = (
    "lib/sqlalchemy/dialects/sqlite/",
    "lib/sqlalchemy/sql/",
    "test/dialect/sqlite/",
)
unexpected = [
    path for path in changed if not path.startswith(allowed_prefixes)
]
assert not unexpected, f"unexpected off-ticket files changed: {unexpected}"

assert "JSON.NULL" in diff, "expected the patch to address JSON.NULL"
assert "json" in diff.lower(), "expected JSON-specific implementation or tests"
assert (
    "in_op" in diff
    or ".in_(" in diff
    or ".not_in(" in diff
    or ".notin(" in diff
), "expected JSON.NULL membership handling"
assert (
    "operators.is_" in diff
    or ".is_(" in diff
), "expected JSON.NULL is_() handling"
assert (
    "is_distinct_from" in diff
), "expected JSON.NULL distinct predicate handling"
assert (
    "JSON_QUOTE(JSON_EXTRACT" in diff
    and "JSON_TYPE" in diff
), "expected mixed membership to preserve JSON scalar matching and path typing"
assert (
    "TypeDecorator" in diff
    or "_clone()" in diff
), "expected cache-stable bind handling instead of compile-time value branching"
assert (
    "operators.eq" in diff
    or "JSON.NULL ==" in diff
), "expected symmetric equality handling"
assert "TODO" not in diff and "FIXME" not in diff, "patch leaves TODO/FIXME markers"
