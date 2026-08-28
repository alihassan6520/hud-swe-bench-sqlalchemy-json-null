from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import JSON


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
                    "profile": {"age": 42, "name": "Ada", "active": True},
                    "records": [{"score": 9}],
                },
            }
        ],
    )

    assert connection.scalar(select(table.c.payload)) == {
        "profile": {"age": 42, "name": "Ada", "active": True},
        "records": [{"score": 9}],
    }
    assert connection.scalar(select(table.c.payload["profile"])) == {
        "age": 42,
        "name": "Ada",
        "active": True,
    }
    assert connection.scalar(
        select(table.c.payload[("profile", "age")].as_integer())
    ) == 42
    assert connection.scalar(
        select(table.c.payload[("profile", "name")].as_string())
    ) == "Ada"
    assert connection.scalar(
        select(table.c.payload[("records", 0, "score")].as_integer())
    ) == 9

