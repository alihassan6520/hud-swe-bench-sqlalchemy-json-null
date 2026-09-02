from sqlalchemy import Column
from sqlalchemy import event
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

seen_value_params = []


@event.listens_for(engine, "before_cursor_execute")
def collect_json_predicate_params(
    conn, cursor, statement, parameters, context, executemany
):
    if "WHERE" not in statement or "JSON_EXTRACT" not in statement:
        return
    if isinstance(parameters, dict):
        values = list(parameters.values())
    else:
        values = list(parameters)
    seen_value_params.append(
        [
            value
            for value in values
            if not (isinstance(value, str) and value.startswith("$."))
        ]
    )


def ids(connection, expr):
    return connection.scalars(
        select(table.c.id).where(expr).order_by(table.c.id)
    ).all()


json_null = GenericJSON.NULL
flag = table.c.payload["flag"]

with engine.begin() as connection:
    connection.execute(
        table.insert(),
        [
            {"id": 1, "payload": {"flag": None}},
            {"id": 2, "payload": {"flag": "ready"}},
            {"id": 3, "payload": {"flag": 7}},
            {"id": 4, "payload": {"flag": "other"}},
            {"id": 5, "payload": {}},
            {"id": 6, "payload": None},
        ],
    )

    assert ids(connection, flag == json_null) == [1]
    assert ids(connection, flag == "ready") == [2]
    assert ids(connection, flag == 7) == [3]
    assert ids(connection, flag.in_([json_null, "ready", 7])) == [1, 2, 3]
    assert ids(connection, flag.in_(["ready", "other"])) == [2, 4]
    assert ids(connection, flag.in_([json_null, "other"])) == [1, 4]

assert seen_value_params[0] == ["null", "null", "null"], seen_value_params
assert seen_value_params[1] == ['"ready"', '"ready"', '"ready"'], seen_value_params
assert seen_value_params[2] == ["7", "7", "7"], seen_value_params
assert seen_value_params[3] == ["null", '"ready"', "7"], seen_value_params
assert seen_value_params[4] == ['"ready"', '"other"'], seen_value_params
assert seen_value_params[5] == ["null", '"other"'], seen_value_params

flat_values = [value for values in seen_value_params for value in values]
assert GenericJSON.NULL not in flat_values, seen_value_params
assert "ready" not in flat_values, seen_value_params
assert "other" not in flat_values, seen_value_params
assert 7 not in flat_values, seen_value_params
