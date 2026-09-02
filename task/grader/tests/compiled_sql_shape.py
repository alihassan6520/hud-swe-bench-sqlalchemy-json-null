from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.types import JSON as GenericJSON


engine = create_engine("sqlite://")
metadata = MetaData()
table = Table(
    "payloads",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("payload", JSON),
)
metadata.create_all(engine)

flag = table.c.payload["flag"]
json_null = GenericJSON.NULL

is_sql = str(
    select(table.c.id)
    .where(flag.is_(json_null))
    .compile(dialect=sqlite.dialect())
)
mixed_sql = str(
    select(table.c.id)
    .where(flag.in_([json_null, "ready", 7]))
    .compile(dialect=sqlite.dialect())
)
inverse_mixed_sql = str(
    select(table.c.id)
    .where(flag.not_in([json_null, "ready", 7]))
    .compile(dialect=sqlite.dialect())
)

assert "JSON_TYPE" in is_sql, is_sql
assert "JSON_QUOTE(JSON_EXTRACT" not in is_sql, is_sql
assert "JSON_TYPE" in mixed_sql and "JSON_QUOTE(JSON_EXTRACT" in mixed_sql, mixed_sql
assert " IS NOT NULL " in mixed_sql, mixed_sql
assert " OR " in inverse_mixed_sql and " NOT IN " in inverse_mixed_sql, inverse_mixed_sql

with engine.begin() as connection:
    connection.execute(
        table.insert(),
        [
            {"id": 1, "payload": {"flag": "ready"}},
            {"id": 2, "payload": {"flag": "other"}},
            {"id": 3, "payload": {"flag": 8}},
            {"id": 4, "payload": {"flag": 7}},
            {"id": 5, "payload": {"flag": None}},
        ],
    )

    first_ids = connection.scalars(
        select(table.c.id)
        .where(flag.in_([json_null, "ready", 7]))
        .order_by(table.c.id)
    ).all()
    second_ids = connection.scalars(
        select(table.c.id)
        .where(flag.in_([json_null, "other", 8]))
        .order_by(table.c.id)
    ).all()

assert first_ids == [1, 4, 5], first_ids
assert second_ids == [2, 3, 5], second_ids
