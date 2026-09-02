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
            {"id": 2, "payload": {"flag": "ready"}},
            {"id": 3, "payload": None},
            {"id": 4, "payload": {"flag": "null"}},
            {"id": 5, "payload": {"flag": 7}},
            {"id": 6, "payload": {"flag": False}},
            {"id": 7, "payload": {}},
        ],
    )

    json_null = GenericJSON.NULL
    flag = table.c.payload["flag"]

    singleton_ids = connection.scalars(
        select(table.c.id)
        .where(flag.in_([json_null]))
        .order_by(table.c.id)
    ).all()
    mixed_ids = connection.scalars(
        select(table.c.id)
        .where(flag.in_([json_null, "ready", 7]))
        .order_by(table.c.id)
    ).all()
    inverse_mixed_ids = connection.scalars(
        select(table.c.id)
        .where(flag.not_in([json_null, "ready", 7]))
        .order_by(table.c.id)
    ).all()

assert singleton_ids == [1], singleton_ids
assert mixed_ids == [1, 2, 5], mixed_ids
assert inverse_mixed_ids == [3, 4, 6, 7], inverse_mixed_ids
