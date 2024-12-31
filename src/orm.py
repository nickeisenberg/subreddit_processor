import os
import pandas as pd
from typing import Iterable, Literal


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


class SentimentRow:
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
    def row(self):
        return pd.DataFrame(self.row_dict, index=pd.Series([0]))
    
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


class Sentiment:
    def __init__(self):
        self.rows: list[pd.DataFrame] = []
        self._table = pd.DataFrame(dtype=object)
    
    @property
    def new_row(self):
        return SentimentRow

    def add_row(self, row: SentimentRow):
        self.rows.append(row.row)
    
    @property
    def table(self):
        if len(self.rows) == len(self._table):
            return self._table
        else:
            self._table = pd.concat(self.rows).reset_index(drop=True)
            return self._table

    def write(self, root: str, overwrite: bool = False):
        common_write(self.table, root, overwrite)


class CommentsRow:
    def __init__(self, date: str, submission_id: str, comment_id: str,
                 comment: str):
        self.date = date 
        self.submission_id = submission_id 
        self.comment_id = comment_id
        self.comment = comment
    
    @property
    def row(self):
        return pd.DataFrame(self.row_dict, index=pd.Series([0]))

    @property
    def row_dict(self):
        return {
            "submission_id": self.submission_id,
            "comment_id": self.comment_id,
            "date": self.date,
            "comment": self.comment 
        }


class Comments:
    def __init__(self):
        self.rows: list[pd.DataFrame] = []
        self._table = pd.DataFrame(dtype=object)
    
    @property
    def new_row(self):
        return CommentsRow

    def add_row(self, row: CommentsRow):
        self.rows.append(row.row)
    
    @property
    def table(self):
        if len(self.rows) == len(self._table):
            return self._table
        else:
            self._table = pd.concat(self.rows).reset_index(drop=True)
            return self._table

    def write(self, root: str, overwrite: bool = False):
        common_write(self.table, root, overwrite)
