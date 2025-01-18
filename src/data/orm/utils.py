from sqlalchemy import text
from sqlalchemy.engine.base import Engine

def check_query(row: object, table_name: str, primary_keys: list[str]):
    query = f"select * from {table_name} where "
    for primary_key in primary_keys:
        query += f"{primary_key} = '{row.__getattribute__(primary_key)}' and "
    return query[:-4] + ";"


def check(query: str, engine: Engine):
    with engine.connect() as conn:
        result = conn.execute(text(query))
    check = result.fetchall()
    if check:
        return False
    else:
        return True
