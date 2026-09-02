from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.types import JSON as GenericJSON


def build_table(name):
    engine = create_engine("sqlite://", query_cache_size=50)
    metadata = MetaData()
    table = Table(
        name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("payload", JSON),
    )
    metadata.create_all(engine)
    return engine, table


def populate(connection, table):
    connection.execute(
        table.insert(),
        [
            {"id": 1, "payload": {"flag": None}},
            {"id": 2, "payload": {"flag": "ready"}},
            {"id": 3, "payload": {}},
            {"id": 4, "payload": None},
            {"id": 5, "payload": {"flag": "other"}},
            {"id": 6, "payload": {"flag": 7}},
        ],
    )


def ids(connection, table, expr):
    return connection.scalars(
        select(table.c.id).where(expr).order_by(table.c.id)
    ).all()


json_null = GenericJSON.NULL

engine, table = build_table("payloads_forward")
flag = table.c.payload["flag"]
with engine.begin() as connection:
    populate(connection, table)

    assert ids(connection, table, flag.in_([json_null, "ready"])) == [1, 2]
    assert ids(connection, table, flag.in_(["other", 7])) == [5, 6]
    assert ids(connection, table, flag.not_in([json_null, "ready"])) == [
        3,
        4,
        5,
        6,
    ]
    assert ids(connection, table, flag.not_in(["other", 7])) == [1, 2, 3, 4]

engine, table = build_table("payloads_reverse")
flag = table.c.payload["flag"]
with engine.begin() as connection:
    populate(connection, table)

    assert ids(connection, table, flag.in_(["ready", 7])) == [2, 6]
    assert ids(connection, table, flag.in_([json_null, "other"])) == [1, 5]
    assert ids(connection, table, flag.not_in(["ready", 7])) == [1, 3, 4, 5]
    assert ids(connection, table, flag.not_in([json_null, "other"])) == [
        2,
        3,
        4,
        6,
    ]
