## SQLite JSON.NULL comparison semantics

SQLAlchemy's SQLite JSON implementation currently treats some JSON path comparisons against `JSON.NULL` too broadly.

Please update the SQLite dialect so expressions like:

```python
table.c.payload["key"] == JSON.NULL
table.c.payload[("nested", 0, "key")] == JSON.NULL
```

match only rows where the addressed JSON path exists and the value at that path is explicit JSON null.

They must not match:

- a missing object key or array index
- a SQL NULL JSON column/container
- a JSON string value such as `"null"`

The inverse comparison should also behave consistently:

```python
table.c.payload["key"] != JSON.NULL
```

should exclude explicit JSON null values, but should allow non-null values, missing paths, and SQL NULL containers.

Keep this narrowly scoped to SQLite JSON index/path comparison behavior. Do not change JSON persistence semantics, `none_as_null`, normal JSON extraction results, scalar casters, or non-SQLite dialect behavior.

Add focused regression coverage in the existing SQLite JSON tests.

