from abc import ABC, abstractmethod
from collections import defaultdict
from tqdm import tqdm
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.session import Session
from sqlalchemy.engine.base import Engine

from .utils import check_if_primary_key_exists_in_db


class Database(ABC):
    _base = None
    _session = None
    _engine = None

    
    @property
    def engine(self) -> Engine:
        if not self._engine:
            raise Exception("session is not yet started") 
        return self._engine
    
    @engine.setter
    def engine(self, engine: Engine):
        if isinstance(engine, Engine):
            self._engine = engine
        else:
            raise Exception("engine must be of type Engine")
    
    @property
    def session(self) -> Session:
        if not self._session:
            raise Exception("session is not yet started") 
        return self._session
    
    @session.setter
    def session(self, session: Session):
        if isinstance(session, Session):
            self._session = session 
        else:
            raise Exception("session must be of type Session")

    @property
    def base(self) -> DeclarativeMeta:
        if self._base is None:
            self._base = declarative_base()
        return self._base

    def add_row_to_database(self, row: object):
        try:
            self.session.add(row)
            self.session.commit()
        except Exception as e:
            print(e)
            self.session.rollback()

    def add_rows_to_database(self, rows: list[object]):
        pbar = tqdm(rows)
        session_keys = defaultdict(int)
        num_successful_rows = 0
        num_fail_rows = 0
        print("adding the rows to the session")
        for row in pbar:
            table = row.__getattribute__("__table__")
            table_name = table.name
            row_primary_key_values = {
                x.name: row.__getattribute__(x.name) for x in table.primary_key
            }
            row_primary_key_values_str = table_name + "-" + "-".join(
                [
                    str(row_primary_key_values[key]) for key in row_primary_key_values 
                ]
            )
            if check_if_primary_key_exists_in_db(table_name=table_name, 
                                                 primary_keys=row_primary_key_values, 
                                                 engine=self.engine):
                num_fail_rows += 1
                pbar.set_postfix(success=num_successful_rows, fail=num_fail_rows)
            elif session_keys[row_primary_key_values_str] == 1:
                num_fail_rows += 1
                pbar.set_postfix(success=num_successful_rows, fail=num_fail_rows)
            else:
                self.session.add(row)
                session_keys[row_primary_key_values_str] = 1
                num_successful_rows += 1
                pbar.set_postfix(success=num_successful_rows, fail=num_fail_rows)
        print("committing the session")
        self.session.commit()
        print(f"{num_successful_rows} / {len(rows)} rows were made")
    
    @property
    @abstractmethod
    def tables(self) -> dict[str, DeclarativeMeta]:...
