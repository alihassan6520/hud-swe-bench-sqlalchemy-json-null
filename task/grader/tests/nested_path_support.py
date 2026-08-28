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
            {
                "id": 1,
                "payload": {
                    "profile": {"status": None},
                    "events": [{"kind": None}],
                },
            },
            {"id": 2, "payload": {"profile": {}, "events": [{}]}},
            {
                "id": 3,
                "payload": {
                    "profile": {"status": "null"},
                    "events": [{"kind": "null"}],
                },
            },
            {"id": 4, "payload": None},
        ],
    )

    nested_ids = connection.scalars(
        select(table.c.id)
        .where(table.c.payload[("profile", "status")] == GenericJSON.NULL)
        .order_by(table.c.id)
    ).all()
    array_ids = connection.scalars(
        select(table.c.id)
        .where(table.c.payload[("events", 0, "kind")] == GenericJSON.NULL)
        .order_by(table.c.id)
    ).all()
    missing_ids = connection.scalars(
        select(table.c.id)
        .where(table.c.payload[("profile", "missing")] == GenericJSON.NULL)
        .order_by(table.c.id)
    ).all()

assert nested_ids == [1], nested_ids
assert array_ids == [1], array_ids
assert missing_ids == [], missing_ids

