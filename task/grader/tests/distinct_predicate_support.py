from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import select
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

with engine.begin() as connection:
    connection.execute(
        table.insert(),
        [
            {"id": 1, "payload": {"flag": None, "nested": {"flag": None}}},
            {"id": 2, "payload": {"flag": "ready", "nested": {}}},
            {"id": 3, "payload": {}},
            {"id": 4, "payload": None},
            {"id": 5, "payload": {"flag": "null", "nested": {"flag": "null"}}},
            {"id": 6, "payload": {"flag": 7, "nested": {"flag": 7}}},
        ],
    )

    json_null = GenericJSON.NULL
    flag = table.c.payload["flag"]
    nested_flag = table.c.payload[("nested", "flag")]

    not_distinct_ids = connection.scalars(
        select(table.c.id)
        .where(flag.is_not_distinct_from(json_null))
        .order_by(table.c.id)
    ).all()
    distinct_ids = connection.scalars(
        select(table.c.id)
        .where(flag.is_distinct_from(json_null))
        .order_by(table.c.id)
    ).all()
    nested_not_distinct_ids = connection.scalars(
        select(table.c.id)
        .where(nested_flag.is_not_distinct_from(json_null))
        .order_by(table.c.id)
    ).all()

assert not_distinct_ids == [1], not_distinct_ids
assert distinct_ids == [2, 3, 4, 5, 6], distinct_ids
assert nested_not_distinct_ids == [1], nested_not_distinct_ids
