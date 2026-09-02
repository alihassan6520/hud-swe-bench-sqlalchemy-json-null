from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.types import JSON as GenericJSON


engine = create_engine("sqlite://", query_cache_size=50)
metadata = MetaData()
table = Table(
    "payloads",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("payload", JSON),
)
metadata.create_all(engine)


def ids(connection, expr):
    return connection.scalars(
        select(table.c.id).where(expr).order_by(table.c.id)
    ).all()


json_null = GenericJSON.NULL

with engine.begin() as connection:
    connection.execute(
        table.insert(),
        [
            {
                "id": 1,
                "payload": {"flag": None, "nested": {"flag": None}},
            },
            {
                "id": 2,
                "payload": {"flag": "ready", "nested": {"flag": "ready"}},
            },
            {"id": 3, "payload": {}},
            {"id": 4, "payload": None},
            {
                "id": 5,
                "payload": {"flag": "null", "nested": {"flag": "null"}},
            },
            {"id": 6, "payload": {"flag": 7, "nested": {"flag": 7}}},
            {
                "id": 7,
                "payload": {"flag": "other", "nested": {"flag": "other"}},
            },
        ],
    )

    flag = table.c.payload["flag"]
    nested_flag = table.c.payload[("nested", "flag")]

    assert ids(connection, flag == json_null) == [1]
    assert ids(connection, nested_flag == "ready") == [2]
    assert ids(connection, nested_flag == json_null) == [1]
    assert ids(connection, "ready" == flag) == [2]
    assert ids(connection, json_null == nested_flag) == [1]
    assert ids(connection, flag.is_distinct_from(json_null)) == [
        2,
        3,
        4,
        5,
        6,
        7,
    ]
    assert ids(connection, flag == json_null) == [1]
    assert ids(connection, nested_flag.is_not_distinct_from(json_null)) == [1]

    assert ids(connection, flag.in_([json_null])) == [1]
    assert ids(connection, flag.in_(["ready", "other", 7])) == [2, 6, 7]
    assert ids(connection, nested_flag.in_([json_null, "ready", "other", 7])) == [
        1,
        2,
        6,
        7,
    ]
    assert ids(connection, nested_flag.not_in([json_null])) == [2, 3, 4, 5, 6, 7]
    assert ids(connection, flag.not_in(["ready", "other"])) == [1, 3, 4, 5, 6]
    assert ids(connection, nested_flag.in_([json_null, "null"])) == [1, 5]
    assert ids(connection, flag.in_(["null"])) == [5]
