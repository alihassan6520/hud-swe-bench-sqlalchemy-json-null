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
            {"id": 1, "payload": {"flag": None}},
            {"id": 2, "payload": {}},
            {"id": 3, "payload": None},
            {"id": 4, "payload": {"flag": "null"}},
            {"id": 5, "payload": {"flag": True}},
        ],
    )

    in_ids = connection.scalars(
        select(table.c.id)
        .where(table.c.payload["flag"].in_([GenericJSON.NULL]))
        .order_by(table.c.id)
    ).all()
    not_in_ids = connection.scalars(
        select(table.c.id)
        .where(table.c.payload["flag"].not_in([GenericJSON.NULL]))
        .order_by(table.c.id)
    ).all()
    nested_in_ids = connection.scalars(
        select(table.c.id)
        .where(table.c.payload[("details", "flag")].in_([GenericJSON.NULL]))
        .order_by(table.c.id)
    ).all()

assert in_ids == [1], in_ids
assert not_in_ids == [2, 3, 4, 5], not_in_ids
assert nested_in_ids == [], nested_in_ids
