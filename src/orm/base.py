from abc import ABC, abstractmethod
import pandas as pd
from typing import Any


class Row(ABC):
    @property
    @abstractmethod
    def row_dict(self) -> dict[str, Any]:
        pass

    @property
    def row(self):
        return pd.DataFrame(self.row_dict, index=pd.Series([0]))


class Table(ABC):
    _table = pd.DataFrame(dtype=object)

    @property
    def table(self):
        return self._table

    def add_row(self, row):
        if len(self._table) == 0:
            self._table = row.row
        else:
            self._table = pd.concat([self._table, row.row]).reset_index(drop=True)

    def load(self, path, **kwargs):
        self._table = pd.read_csv(path, **kwargs)
    
    @abstractmethod
    def write(self, *args, **kwargs):
        pass
