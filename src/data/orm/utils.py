from sqlalchemy import text
from sqlalchemy.engine.base import Engine


def check_if_primary_key_exists_in_db(row: object, table_name: str, primary_keys: list[str],
                                       engine: Engine):
    query = check_if_primary_key_exists_in_db_query(
        row=row, table_name=table_name, primary_keys=primary_keys
    )
    with engine.connect() as conn:
        result = conn.execute(text(query))
    check = result.fetchall()
    if check:
        return True 
    else:
        return False 


def check_if_primary_key_exists_in_db_query(row: object, table_name: str, 
                                             primary_keys: list[str]):
    query = f"select * from {table_name} where "
    for primary_key in primary_keys:
        query += f"{primary_key} = '{row.__getattribute__(primary_key)}' and "
    return query[:-4] + ";"
