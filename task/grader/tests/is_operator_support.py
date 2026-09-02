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
            {"id": 1, "payload": {"flag": None, "profile": {"flag": None}}},
            {"id": 2, "payload": {}},
            {"id": 3, "payload": None},
            {"id": 4, "payload": {"flag": "null", "profile": {"flag": "null"}}},
            {"id": 5, "payload": {"flag": 0, "profile": {}}},
        ],
    )

    json_null = GenericJSON.NULL
    is_ids = connection.scalars(
        select(table.c.id)
        .where(table.c.payload["flag"].is_(json_null))
        .order_by(table.c.id)
    ).all()
    is_not_ids = connection.scalars(
        select(table.c.id)
        .where(table.c.payload["flag"].is_not(json_null))
        .order_by(table.c.id)
    ).all()
    nested_is_ids = connection.scalars(
        select(table.c.id)
        .where(table.c.payload[("profile", "flag")].is_(json_null))
        .order_by(table.c.id)
    ).all()

assert is_ids == [1], is_ids
assert is_not_ids == [2, 3, 4, 5], is_not_ids
assert nested_is_ids == [1], nested_is_ids
