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
