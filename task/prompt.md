## SQLite JSON.NULL path predicates

A customer found that SQLite JSON filters using SQLAlchemy's `JSON.NULL`
sentinel are not precise enough when the filter targets a JSON path.

Update the SQLite dialect so JSON path predicates treat an explicit JSON null
as a different value from an absent path, a SQL NULL JSON container, and the
JSON string `"null"`.

The behavior should be consistent for direct key paths, tuple JSON paths,
normal and reversed equality predicates, `is_()` / `is_not()` predicates, and
`is_distinct_from()` / `is_not_distinct_from()` predicates. Membership
predicates should work when `JSON.NULL` appears either by itself or alongside
ordinary JSON scalar values. Inverse predicates should exclude explicit JSON
null values while allowing non-null values, absent paths, and SQL NULL
containers.

The fix must remain correct when SQLAlchemy reuses compiled statements from
the engine query cache. In particular, a cached JSON path comparison compiled
for `JSON.NULL` must not corrupt later ordinary scalar comparisons on the same
path, and an ordinary scalar comparison must not corrupt a later `JSON.NULL`
comparison. The same requirement applies to JSON path membership predicates.
The cached form should also stay correct across direct-key paths, tuple JSON
paths, reversed operands, distinct predicates, and membership lists of different
lengths.

Raw Python scalar right-hand-side values used in JSON path predicates must
still be compared as JSON values. For example, string and numeric values such
as `"ready"` and `7` should reach SQLite as JSON-serialized bind values
(`"\"ready\""` and `"7"`), while `JSON.NULL` should bind as `"null"`, including
when these values appear in cached equality comparisons or cached `IN`
membership lists.

Keep the change limited to SQLite JSON index/path predicate compilation. Do
not change JSON persistence semantics, `none_as_null`, regular JSON extraction
results, scalar casters, or other dialects.

Add focused regression coverage in the existing SQLite JSON tests.
