## SQLite JSON.NULL path predicates

A customer found that SQLite JSON filters using SQLAlchemy's `JSON.NULL`
sentinel are not precise enough when the filter targets a JSON path.

Update the SQLite dialect so JSON path predicates treat an explicit JSON null
as a different value from an absent path, a SQL NULL JSON container, and the
JSON string `"null"`.

The behavior should be consistent for direct key paths, tuple JSON paths,
normal and reversed equality predicates, `is_()` / `is_not()` predicates, and
membership predicates where `JSON.NULL` appears either by itself or alongside
ordinary JSON scalar values. Inverse predicates should exclude explicit JSON
null values while allowing non-null values, absent paths, and SQL NULL
containers.

Keep the change limited to SQLite JSON index/path predicate compilation. Do
not change JSON persistence semantics, `none_as_null`, regular JSON extraction
results, scalar casters, or other dialects.

Add focused regression coverage in the existing SQLite JSON tests.
