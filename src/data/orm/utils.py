import datetime as dt
from typing import Any
from sqlalchemy import text
from sqlalchemy.engine.base import Engine


def check_if_primary_key_exists_in_db(table_name: str, 
                                      primary_keys: dict[str, Any],
                                      engine: Engine):
    query = check_if_primary_key_exists_in_db_query(
        table_name=table_name, primary_keys=primary_keys
    )
    with engine.connect() as conn:
        result = conn.execute(text(query))
    check = result.fetchall()
    if check:
        return True 
    else:
        return False 


def check_if_primary_key_exists_in_db_query(table_name: str, 
                                            primary_keys: dict[str, Any]):
    query = f"select * from {table_name} where "
    for primary_key in primary_keys:
        value = primary_keys[primary_key]
        if isinstance(value, str):
            query += f"{primary_key} = '{value}' and "
        else:
            query += f"{primary_key} = {value} and "
    return query[:-4] + ";"


def get_dates(engine: Engine, table_name: str):
    with engine.connect() as conn:
        result = conn.execute(text(f"select distinct(date) from {table_name}"))
    return sorted([x[0] for x in result.fetchall()])


def missing_days(engine: Engine, table_name: str, include_today: bool = False):
    dts = [dt.datetime.strptime(x, "%Y-%m-%d") for x in get_dates(engine, table_name)]
    today = dt.datetime.strptime(dt.datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    dates = []
    last = dts[-1]
    while last < today:
        last += dt.timedelta(days=1)
        dates.append(last.strftime("%Y-%m-%d"))
    if include_today:
        return dates
    else:
        return dates[:-1]
