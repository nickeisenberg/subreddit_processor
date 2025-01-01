from abc import ABC, abstractmethod
import os
import pandas as pd
from typing import Any, Iterable, Literal


def get_submission_id_and_date_from_summary(summary: pd.DataFrame):
    columns = summary.columns
    if not "submission_id" in columns and not "date" in columns:
        raise Exception("submission_id and date are not in the columns of summary")
    submission_id = summary["submission_id"].values[0]
    date_str = summary["date"].values[0]
    return submission_id, date_str


def common_write(table: pd.DataFrame, root: str, overwrite: bool = False):
    columns = table.columns
    if not "submission_id" in columns and not "date" in columns:
        raise Exception("submission_id and date are not in the columns of summary")
    submission_id = table["submission_id"].values[0]
    date_str = table["date"].values[0]
    save_csv_to = os.path.join(root, f"{date_str}_{submission_id}.csv")
    if not overwrite and os.path.isfile(save_csv_to):
        raise Exception(f"{save_csv_to} exists")
    table.to_csv(save_csv_to)


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
        self._rows = [pd.DataFrame([row]) for _, row in self._table.iterrows()]
    
    @abstractmethod
    def write(self, *args, **kwargs):
        pass


class SentimentRow(Row):
    def __init__(self, submission_id: str, comment_id: str, date: str, 
                 sentiment: Literal["positive", "negative", "neutral"], 
                 sentiment_score: float, 
                 tickers_mentioned: Iterable[str]):
        self.submission_id = submission_id
        self.comment_id = comment_id
        self.date = date
        self.sentiment = sentiment
        self.sentiment_score = sentiment_score
        self.tickers_mentioned = ", ".join(tickers_mentioned) if tickers_mentioned else "N/A"
    
    @property
    def row_dict(self):
        return {
            "submission_id": self.submission_id,
            "comment_id": self.comment_id,
            "date": self.date,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "tickers_mentioned": self.tickers_mentioned 
        }
    

class Sentiment(Table):
    @property
    def new_row(self):
        return SentimentRow

    def write(self, root: str, overwrite: bool = False):
        common_write(self.table, root, overwrite)


class CommentsRow(Row):
    def __init__(self, date: str, submission_id: str, comment_id: str,
                 comment: str):
        self.date = date 
        self.submission_id = submission_id 
        self.comment_id = comment_id
        self.comment = comment

    @property
    def row_dict(self):
        return {
            "submission_id": self.submission_id,
            "comment_id": self.comment_id,
            "date": self.date,
            "comment": self.comment 
        }


class Comments(Table):
    @property
    def new_row(self):
        return CommentsRow

    def write(self, root: str, overwrite: bool = False):
        common_write(self.table, root, overwrite)


if __name__ == "__main__":
    coms = Comments()
    row0 = coms.new_row("2024-01-01", "00a1", "00b1", "hello there")
    coms.add_row(row0)
    row1 = coms.new_row("2024-01-02", "00a2", "00b2", "another comment")
    coms.add_row(row1)
    print(coms.table)
